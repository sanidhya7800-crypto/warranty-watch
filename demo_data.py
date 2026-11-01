"""Seed clearly-labelled demo data so the app is never empty.

Demo data is realistic but only sample data; the UI always tags results by mode
(live vs demo) so demo content is never shown as live.
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy.orm import sessionmaker

from config import has_tinyfish_key
from models import Product, RecallAlert, ServiceRequest, Setting


def seed_if_empty(SessionLocal: sessionmaker) -> None:
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            today = date.today()
            products = [
                Product(
                    name="Samsung Family Hub Refrigerator",
                    category="Refrigerator",
                    manufacturer="Samsung",
                    model_number="RF28T5001SR",
                    serial_number="SN-DEMO-0001",
                    purchase_date=today - timedelta(days=400),
                    warranty_duration_months=12,
                    warranty_expiry_date=today + timedelta(days=20),  # expiring soon
                    notes="Demo product",
                ),
                Product(
                    name="LG Front Load Washing Machine",
                    category="Washing Machine",
                    manufacturer="LG",
                    model_number="WM3900HWA",
                    serial_number="SN-DEMO-0002",
                    purchase_date=today - timedelta(days=700),
                    warranty_duration_months=24,
                    warranty_expiry_date=today + timedelta(days=25),  # expiring soon
                    notes="Demo product",
                ),
                Product(
                    name="Daikin Inverter Split AC",
                    category="Air Conditioner",
                    manufacturer="Daikin",
                    model_number="FTKM50UVMA",
                    serial_number="SN-DEMO-0003",
                    purchase_date=today - timedelta(days=500),
                    warranty_duration_months=12,
                    warranty_expiry_date=today - timedelta(days=10),  # expired
                    amc_expiry_date=today + timedelta(days=60),       # AMC active
                    notes="Demo product",
                ),
                Product(
                    name="Sony Bravia 4K TV",
                    category="Television",
                    manufacturer="Sony",
                    model_number="XR-55A80J",
                    serial_number="SN-DEMO-0004",
                    purchase_date=today - timedelta(days=200),
                    warranty_duration_months=12,
                    warranty_expiry_date=today + timedelta(days=165),  # active
                    notes="Demo product",
                ),
            ]
            for p in products:
                db.add(p)
            db.flush()

            db.add(
                ServiceRequest(
                    product_id=products[0].id,
                    manufacturer="Samsung",
                    issue_description="Refrigerator not cooling properly; freezer temperature fluctuating.",
                    complaint_number="SR-DEMO-1001",
                    service_portal_url="https://www.samsung.com/in/support/",
                    request_date=today - timedelta(days=5),
                    status="Pending",
                    notes="Demo service request",
                )
            )
            db.add(
                RecallAlert(
                    title="Demo: Safety notice for select refrigerator models",
                    manufacturer="Samsung",
                    affected_model="RF28T5001SR",
                    description=(
                        "Sample recall notice for demonstration only \u2014 NOT a real recall. "
                        "Always verify on the official Samsung support page before acting."
                    ),
                    source_url="https://www.samsung.com/in/support/",
                    date_detected=today,
                    severity="High",
                    related_product_ids="1",
                )
            )
            db.commit()

        if not db.query(Setting).filter(Setting.key == "mode").first():
            db.add(Setting(key="mode", value="live" if has_tinyfish_key() else "demo"))
            db.commit()
    finally:
        db.close()
