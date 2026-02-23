# app/api/featured.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from sqlalchemy import asc, desc

from app.core.deps import get_db, get_current_user
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemList
from app.models.user import User
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/menu-items", tags=["Featured"])

# ---- Request schema (yalın ve lokal) ----
class FeaturedPatchIn(BaseModel):
    is_featured: bool = Field(..., description="Ürünün öne çıkan olup olmayacağı")

# ---- Yardımcılar ----
def _apply_sorting(query, sort_by: Optional[str], sort_dir: Optional[str], default_cols):
    direction = asc if (sort_dir or "asc") == "asc" else desc
    mapping = {
        "name": MenuItem.name,
        "price": MenuItem.price,
        "created_at": MenuItem.created_at,
    }
    if sort_by in mapping:
        return query.order_by(direction(mapping[sort_by]))
    if isinstance(default_cols, (list, tuple)):
        return query.order_by(*[direction(c) for c in default_cols])
    return query.order_by(direction(default_cols))

def _as_list(items):
    return [
        {
            "id": i.id,
            "name": i.name,
            "description": i.description,
            "price": i.price,
            "category_name": i.category.name if i.category else "",
            "is_available": i.is_available,
            "is_featured": i.is_featured,
            "image_url": i.image_url,
        }
        for i in items
    ]

# ---- GET: Featured listesi (public) ----
@router.get("/featured", response_model=List[MenuItemList])
def list_featured_items(
    limit: int = Query(10, ge=1, le=50),
    category_id: Optional[int] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, pattern="^(name|price|created_at)$"),
    sort_dir: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    q = (
        db.query(MenuItem)
        .options(joinedload(MenuItem.category))
        .filter(MenuItem.is_featured == True, MenuItem.is_available == True)

    )
    if category_id is not None:
        q = q.filter(MenuItem.category_id == category_id)
    if min_price is not None:
        q = q.filter(MenuItem.price >= min_price)
    if max_price is not None:
        q = q.filter(MenuItem.price <= max_price)

    # varsayılan: yeni eklenenler önce (created_at desc)
    q = _apply_sorting(q, sort_by, sort_dir, default_cols=[MenuItem.created_at])

    items = q.limit(limit).all()
    return _as_list(items)

# ---- POST: Bir ürünü featured yap ----
@router.post("/{item_id}/featured", status_code=status.HTTP_201_CREATED)
def mark_featured(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menü öğesi bulunamadı")
    if item.is_featured:
        # idempotent: zaten featured ise 200 döndürebiliriz ama 201 koruyoruz
        return {"status": "ok", "message": "Zaten öne çıkan"}
    item.is_featured = True
    db.add(item)
    db.commit()
    return {"status": "ok"}

# ---- DELETE: Bir üründen featured durumunu kaldır ----
@router.delete("/{item_id}/featured", status_code=status.HTTP_204_NO_CONTENT)
def unmark_featured(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menü öğesi bulunamadı")
    if not item.is_featured:
        return None
    item.is_featured = False
    db.add(item)
    db.commit()
    return None

# ---- PATCH: is_featured'i açıkça ayarla ----
@router.patch("/{item_id}/featured")
def set_featured(
    item_id: int,
    payload: FeaturedPatchIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menü öğesi bulunamadı")
    item.is_featured = payload.is_featured
    db.add(item)
    db.commit()
    return {"status": "ok", "is_featured": item.is_featured}
