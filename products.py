"""Product registration, editing, deletion, invoice upload/download."""
from __future__ import annotations

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from config import (
    ALLOWED_INVOICE_EXTENSIONS,
    ALLOWED_INVOICE_TYPES,
    MAX_INVOICE_BYTES,
    PRODUCT_CATEGORIES,
    SERVICE_REQUEST_STATUSES,
    UPLOAD_DIR,
)
from database import get_db
from models import Product
from notification_service import regenerate_notifications
from schemas import MessageOut, ProductCreate, ProductOut, ProductUpdate
from serialize import product_to_out

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return [product_to_out(p) for p in db.query(Product).order_by(Product.created_at.desc(), Product.id.desc()).all()]


@router.post("", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    p = Product(**payload.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    regenerate_notifications(db)
    return product_to_out(p)


@router.get("/categories", response_model=list[str])
def categories():
    return PRODUCT_CATEGORIES


@router.get("/statuses", response_model=list[str])
def statuses():
    return SERVICE_REQUEST_STATUSES


@router.get("/{pid}", response_model=ProductOut)
def get_product(pid: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return product_to_out(p)


@router.put("/{pid}", response_model=ProductOut)
def update_product(pid: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    regenerate_notifications(db)
    return product_to_out(p)


@router.delete("/{pid}", response_model=MessageOut)
def delete_product(pid: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    if p.invoice_filename:
        fp = UPLOAD_DIR / p.invoice_filename
        if fp.exists():
            fp.unlink()
    db.delete(p)
    db.commit()
    return MessageOut(message="deleted")


@router.post("/{pid}/invoice", response_model=ProductOut)
def upload_invoice(pid: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_INVOICE_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_INVOICE_EXTENSIONS))}")
    if file.content_type and file.content_type not in ALLOWED_INVOICE_TYPES and ext not in ALLOWED_INVOICE_EXTENSIONS:
        raise HTTPException(400, "Unsupported file content type")

    data = file.file.read()
    if not data:
        raise HTTPException(400, "Empty file")
    if len(data) > MAX_INVOICE_BYTES:
        raise HTTPException(413, f"File too large (max {MAX_INVOICE_BYTES // 1024 // 1024} MB)")

    if p.invoice_filename:
        old = UPLOAD_DIR / p.invoice_filename
        if old.exists():
            old.unlink()

    safe = f"invoice_{p.id}_{uuid.uuid4().hex[:8]}{ext}"
    (UPLOAD_DIR / safe).write_bytes(data)
    p.invoice_filename = safe
    db.commit()
    db.refresh(p)
    return product_to_out(p)


@router.delete("/{pid}/invoice", response_model=ProductOut)
def remove_invoice(pid: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Product not found")
    if p.invoice_filename:
        fp = UPLOAD_DIR / p.invoice_filename
        if fp.exists():
            fp.unlink()
        p.invoice_filename = None
        db.commit()
        db.refresh(p)
    return product_to_out(p)


@router.get("/{pid}/invoice")
def download_invoice(pid: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == pid).first()
    if not p or not p.invoice_filename:
        raise HTTPException(404, "No invoice on file")
    fp = UPLOAD_DIR / p.invoice_filename
    if not fp.exists():
        raise HTTPException(404, "Invoice file missing")
    return FileResponse(path=str(fp), filename=p.invoice_filename)
