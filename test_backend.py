"""Unit and integration test suite for Warranty Watch backend."""
import sys
from datetime import date, timedelta
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base
from models import Product, ServiceRequest, RecallAlert, Notification, Setting
from warranty_service import warranty_status
from notification_service import regenerate_notifications
from settings_service import get_mode, set_mode
from services.tinyfish import search, fetch, agent, browser, monitor


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


def test_warranty_calculations():
    today = date.today()

    # Active product (expires in 100 days)
    p_active = Product(
        name="Test TV",
        category="Television",
        manufacturer="Sony",
        model_number="TV-100",
        purchase_date=today - timedelta(days=50),
        warranty_expiry_date=today + timedelta(days=100),
    )
    status_active = warranty_status(p_active, today)
    assert status_active["status"] == "Active"
    assert status_active["days_to_expiry"] == 100

    # Expiring soon (expires in 15 days)
    p_expiring = Product(
        name="Test AC",
        category="Air Conditioner",
        manufacturer="Daikin",
        model_number="AC-200",
        purchase_date=today - timedelta(days=350),
        warranty_expiry_date=today + timedelta(days=15),
    )
    status_expiring = warranty_status(p_expiring, today)
    assert status_expiring["status"] == "Expiring Soon"
    assert status_expiring["days_to_expiry"] == 15

    # Expired (expired 10 days ago)
    p_expired = Product(
        name="Test Fridge",
        category="Refrigerator",
        manufacturer="Samsung",
        model_number="FR-300",
        purchase_date=today - timedelta(days=400),
        warranty_expiry_date=today - timedelta(days=10),
    )
    status_expired = warranty_status(p_expired, today)
    assert status_expired["status"] == "Expired"
    assert status_expired["days_to_expiry"] == -10


def test_notification_generation(test_db):
    today = date.today()
    p1 = Product(
        name="Expiring Product",
        category="Washing Machine",
        manufacturer="LG",
        model_number="WM-1",
        purchase_date=today - timedelta(days=350),
        warranty_expiry_date=today + timedelta(days=5), # <= 7 days warning
    )
    test_db.add(p1)
    test_db.commit()

    created = regenerate_notifications(test_db)
    assert created > 0

    notifs = test_db.query(Notification).all()
    assert len(notifs) >= 1
    assert any("expires in" in n.message for n in notifs)


def test_settings_mode_toggle(test_db):
    # Default is live
    mode = get_mode(test_db)
    assert mode in ("live", "demo")

    # Switch to demo
    set_mode(test_db, "demo")
    assert get_mode(test_db) == "demo"

    # Switch back to live
    set_mode(test_db, "live")
    assert get_mode(test_db) == "live"


def test_tinyfish_demo_capabilities(test_db):
    # Ensure demo mode for test execution (free, no credits)
    set_mode(test_db, "demo")

    # 1. Search capability
    search_res = search.search_manufacturer_info(test_db, "Samsung", "RF28T5001SR", "Refrigerator", kind="warranty")
    assert search_res["capability"] == "search"
    assert search_res["mode"] == "demo"
    assert len(search_res["results"]) > 0

    # 2. Fetch capability
    fetch_res = fetch.fetch_url(test_db, "https://www.samsung.com/warranty/")
    assert fetch_res["capability"] == "fetch"
    assert fetch_res["mode"] == "demo"
    assert "DEMO WARRANTY TERMS" in fetch_res["result"]["text"]

    # 3. Agent capability
    agent_res = agent.investigate_issue(
        test_db,
        {"name": "Samsung Refrigerator", "manufacturer": "Samsung", "model_number": "RF28T5001SR"},
        "Freezer not cooling"
    )
    assert agent_res["capability"] == "agent"
    assert agent_res["mode"] == "demo"
    assert agent_res["result"]["status"] == "COMPLETED"
    assert len(agent_res["result"]["result"]["recommended_next_steps"]) > 0

    # 4. Browser capability
    browser_res = browser.open_portal(test_db, "https://www.samsung.com/support/")
    assert browser_res["capability"] == "browser"
    assert browser_res["mode"] == "demo"
    assert browser_res["session"]["simulated"] is True

    # 5. Monitor capability
    mon_res = monitor.create_monitor(
        test_db,
        name="Test Monitor",
        monitor_type="fetch",
        target="https://www.samsung.com/warranty/",
        schedule_cron="0 9 * * 1"
    )
    assert mon_res["mode"] == "demo"
    assert mon_res["monitor"]["status"] == "active"


def test_product_crud_and_deterministic_order(test_db):
    today = date.today()
    p1 = Product(name="Microwave", category="Microwave", manufacturer="Panasonic", model_number="NN-1", purchase_date=today)
    p2 = Product(name="Dishwasher", category="Dishwasher", manufacturer="Bosch", model_number="SMS-2", purchase_date=today)
    test_db.add(p1)
    test_db.add(p2)
    test_db.commit()

    rows = test_db.query(Product).order_by(Product.created_at.desc(), Product.id.desc()).all()
    assert len(rows) == 2
    assert rows[0].id == p2.id
    assert rows[1].id == p1.id


def test_service_request_workflow(test_db):
    p = Product(name="Oven", category="Other", manufacturer="IFB", model_number="OV-1", purchase_date=date.today())
    test_db.add(p)
    test_db.commit()

    sr = ServiceRequest(
        product_id=p.id,
        manufacturer="IFB",
        complaint_number="SR-9999",
        issue_description="Door seal loose",
        service_portal_url="https://www.ifbappliances.com/support",
        request_date=date.today(),
        status="Submitted"
    )
    test_db.add(sr)
    test_db.commit()
    test_db.refresh(sr)

    assert sr.id is not None
    assert sr.status == "Submitted"

    # Update status
    sr.status = "Technician Assigned"
    test_db.commit()
    assert sr.status == "Technician Assigned"


def test_recall_alert_lifecycle(test_db):
    alert = RecallAlert(
        title="Fire Hazard Recall",
        manufacturer="Samsung",
        affected_model="RF28T5001SR",
        description="Potential compressor wiring issue",
        severity="Critical",
        source_url="https://cpsc.gov/recalls/samsung"
    )
    test_db.add(alert)
    test_db.commit()
    test_db.refresh(alert)

    assert alert.id is not None
    assert alert.severity == "Critical"


def test_tinyfish_activity_provenance(test_db):
    from services.tinyfish.activity import start_activity, finish_activity, record_demo
    from models import TinyFishActivity

    # Test demo record
    record_demo(test_db, "search", "Demo search", "Demo summary", "https://example.com")
    demo_act = test_db.query(TinyFishActivity).filter(TinyFishActivity.mode == "demo").first()
    assert demo_act is not None
    assert demo_act.status == "demo"

    # Test live record
    act_id = start_activity(test_db, "fetch", "Live fetch test", "live")
    finish_activity(test_db, act_id, "completed", "Fetched terms successfully", "https://example.com/live")
    live_act = test_db.query(TinyFishActivity).filter(TinyFishActivity.id == act_id).first()
    assert live_act is not None
    assert live_act.status == "completed"
    assert live_act.mode == "live"


def test_ai_assistant_investigate_samsung_refrigerator(test_db):
    from routes.assistant import investigate, InvestigateIn

    set_mode(test_db, "demo")
    p = Product(
        name="Samsung Family Hub Refrigerator",
        category="Refrigerator",
        manufacturer="Samsung",
        model_number="RF28T5001SR",
        purchase_date=date.today() - timedelta(days=200),
    )
    test_db.add(p)
    test_db.commit()

    payload = InvestigateIn(
        product_id=p.id,
        issue="Refrigerator freezer temperature fluctuating, frost accumulating on air vents, compressor buzzing intermittently."
    )
    res = investigate(payload, test_db)

    assert "diagnosis" in res
    diag = res["diagnosis"]
    assert diag["status"] == "COMPLETED"
    assert "Samsung" in diag["issue_summary"]
    assert any("frost" in c.lower() or "evaporator" in c.lower() or "compressor" in c.lower() for c in diag["possible_causes"])
    assert any("gasket" in s.lower() or "clearance" in s.lower() or "service" in s.lower() for s in diag["recommended_next_steps"])
    assert "Sealed" in diag["may_be_covered"] or "Covered" in diag["may_be_covered"]


def test_ai_assistant_investigate_sony_tv(test_db):
    from routes.assistant import investigate, InvestigateIn

    set_mode(test_db, "demo")
    p = Product(
        name="Sony Bravia 4K TV",
        category="Television",
        manufacturer="Sony",
        model_number="XR-55A80J",
        purchase_date=date.today() - timedelta(days=100),
    )
    test_db.add(p)
    test_db.commit()

    payload = InvestigateIn(
        product_id=p.id,
        issue="TV screen flickering intermittently with occasional black screen."
    )
    res = investigate(payload, test_db)

    assert "diagnosis" in res
    diag = res["diagnosis"]
    assert diag["status"] == "COMPLETED"
    assert "Sony" in diag["issue_summary"]
    assert any("t-con" in c.lower() or "panel" in c.lower() or "backlight" in c.lower() or "hdmi" in c.lower() for c in diag["possible_causes"])
    assert any("reboot" in s.lower() or "test" in s.lower() or "service" in s.lower() for s in diag["recommended_next_steps"])
    assert "Panel" in diag["may_be_covered"] or "Covered" in diag["may_be_covered"]


def test_ai_assistant_appliance_separation(test_db):
    from routes.assistant import investigate, InvestigateIn

    set_mode(test_db, "demo")
    p_fridge = Product(name="Fridge", category="Refrigerator", manufacturer="Samsung", model_number="RF-1", purchase_date=date.today())
    p_tv = Product(name="TV", category="Television", manufacturer="Sony", model_number="TV-1", purchase_date=date.today())
    test_db.add(p_fridge)
    test_db.add(p_tv)
    test_db.commit()

    res_f = investigate(InvestigateIn(product_id=p_fridge.id, issue="Freezer frost buildup"), test_db)
    res_t = investigate(InvestigateIn(product_id=p_tv.id, issue="Display green lines"), test_db)

    # Check that diagnoses are completely distinct and appliance-tailored
    assert res_f["product"]["id"] != res_t["product"]["id"]
    assert "Samsung" in res_f["diagnosis"]["issue_summary"]
    assert "Sony" in res_t["diagnosis"]["issue_summary"]
    assert res_f["diagnosis"]["possible_causes"] != res_t["diagnosis"]["possible_causes"]


def test_ai_assistant_agent_failure_handling(test_db):
    from routes.assistant import _normalize_diagnosis

    failed_agent_res = {
        "capability": "agent",
        "mode": "live",
        "error": "Your account is not enabled for custom max steps yet. Join the beta program at /beta, then retry.",
        "summary": None,
    }
    product = {"id": 1, "name": "Fridge", "manufacturer": "Samsung", "model_number": "RF-1"}

    diag = _normalize_diagnosis(
        failed_agent_res,
        product,
        "Freezer not cooling",
        top_url="https://samsung.com/support",
        search_res={"results": []},
        fetch_res=None
    )

    # Must be marked as FAILED with zero fabricated causes
    assert diag["status"] == "FAILED"
    assert "custom max steps" in diag["error"]
    assert len(diag["possible_causes"]) == 0
    assert diag["is_simulated"] is False
    assert len(diag["recommended_next_steps"]) > 0



