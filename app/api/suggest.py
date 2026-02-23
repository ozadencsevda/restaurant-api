# app/api/suggest.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc
from typing import List
from pydantic import BaseModel, Field

from app.core.deps import get_db
from app.models.menu_item import MenuItem

router = APIRouter(prefix="/api/v1/menu-items", tags=["Suggest"])

# Minimal çıktı şeması (autocomplete için hafif payload)
class SuggestItemOut(BaseModel):
    id: int = Field(..., description="Ürün ID")
    name: str = Field(..., description="Ürün adı")

@router.get("/suggest", response_model=List[SuggestItemOut])
def suggest_items(
    q: str = Query(..., min_length=1, max_length=100, description="Öneri metni"),
    limit: int = Query(10, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """
    Autocomplete/suggestion ucu:
    - Önce 'q%' (prefix) eşleşmeleri alır (alfabetik)
    - Kalan hakkı '%q%' eşleşmeleriyle tamamlar
      (ama prefix'te gelen ID'leri hariç tutar → duplicate olmaz)
    - Hafif döner: sadece {id, name}
    """
    term = q.strip()
    if not term:
        return []

    q_like_prefix = f"{term}%"
    q_like_any = f"%{term}%"

    # 1) Prefix eşleşmeleri
    prefix_results = (
        db.query(MenuItem.id, MenuItem.name)
        .filter(MenuItem.name.ilike(q_like_prefix))
        .order_by(asc(MenuItem.name))
        .limit(limit)
        .all()
    )

    # Limit dolduysa direkt dön
    if len(prefix_results) >= limit:
        return [{"id": r.id, "name": r.name} for r in prefix_results]

    # 2) Kalan hakkı, prefix'te gelen id'leri hariç tutarak, içerir eşleşmeleriyle doldur
    picked_ids = [r.id for r in prefix_results]
    remaining = limit - len(prefix_results)

    any_query = (
        db.query(MenuItem.id, MenuItem.name)
        .filter(MenuItem.name.ilike(q_like_any))
    )

    # NOT IN filtresi mutlaka LIMIT'ten ÖNCE uygulanmalı (SQLAlchemy gereği)
    if picked_ids:
        any_query = any_query.filter(~MenuItem.id.in_(picked_ids))

    any_results = (
        any_query
        .order_by(asc(MenuItem.name))
        .limit(remaining)
        .all()
    )

    combined = prefix_results + any_results
    return [{"id": r.id, "name": r.name} for r in combined]
