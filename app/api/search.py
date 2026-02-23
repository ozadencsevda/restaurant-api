# app/api/search.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, desc
from typing import List, Optional

from app.core.deps import get_db
from app.models.menu_item import MenuItem
from app.schemas.menu_item import MenuItemList

router = APIRouter(prefix="/api/v1/menu-items", tags=["Search"])

def _apply_filters(q, *,
                   category_id: Optional[int],
                   is_available: Optional[bool],
                   is_vegetarian: Optional[bool],
                   is_vegan: Optional[bool],
                   is_gluten_free: Optional[bool],
                   min_price: Optional[float],
                   max_price: Optional[float],
                   search: Optional[str]):
    if category_id is not None:
        q = q.filter(MenuItem.category_id == category_id)
    if is_available is not None:
        q = q.filter(MenuItem.is_available == is_available)
    if is_vegetarian is not None:
        q = q.filter(MenuItem.is_vegetarian == is_vegetarian)
    if is_vegan is not None:
        q = q.filter(MenuItem.is_vegan == is_vegan)
    if is_gluten_free is not None:
        q = q.filter(MenuItem.is_gluten_free == is_gluten_free)
    if min_price is not None:
        q = q.filter(MenuItem.price >= min_price)
    if max_price is not None:
        q = q.filter(MenuItem.price <= max_price)
    if search:
        like = f"%{search}%"
        q = q.filter((MenuItem.name.ilike(like)) | (MenuItem.description.ilike(like)))
    return q

def _apply_sort(q, sort_by: Optional[str], sort_dir: Optional[str]):
    direction = asc if (sort_dir or "asc") == "asc" else desc
    mapping = {
        "name": MenuItem.name,
        "price": MenuItem.price,
        "created_at": MenuItem.created_at,
    }
    if sort_by in mapping:
        return q.order_by(direction(mapping[sort_by]))
    # varsayılan: isim
    return q.order_by(direction(MenuItem.name))

def _to_list(items):
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

@router.get("/search", response_model=List[MenuItemList])
def search_items(
    q: str = Query(..., min_length=2, max_length=100, description="Arama terimi"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category_id: Optional[int] = None,
    is_available: Optional[bool] = None,
    is_vegetarian: Optional[bool] = None,
    is_vegan: Optional[bool] = None,
    is_gluten_free: Optional[bool] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    sort_by: Optional[str] = Query(None, pattern="^(name|price|created_at)$"),
    sort_dir: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
):
    query = db.query(MenuItem).options(joinedload(MenuItem.category))
    query = _apply_filters(
        query,
        category_id=category_id,
        is_available=is_available,
        is_vegetarian=is_vegetarian,
        is_vegan=is_vegan,
        is_gluten_free=is_gluten_free,
        min_price=min_price,
        max_price=max_price,
        search=q,
    )
    query = _apply_sort(query, sort_by, sort_dir)
    items = query.offset(skip).limit(limit).all()
    return _to_list(items)
