from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.db.database import SessionLocal
from app.models.menu_item import MenuItem
from app.models.category import Category
from app.schemas.menu_item import MenuItemCreate, MenuItemUpdate, MenuItemResponse, MenuItemList
from app.core.deps import get_current_user, get_db,require_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1/menu-items", tags=["Menu Items"])

# Tüm menü öğelerini listele (GET)
@router.get("/", response_model=List[MenuItemList])
def get_menu_items(
    skip: int = Query(0, ge=0, description="Kaç kayıt atlanacak"),
    limit: int = Query(100, ge=1, le=500, description="Max kayıt sayısı"),
    category_id: Optional[int] = Query(None, description="Kategori ID'ye göre filtrele"),
    is_available: Optional[bool] = Query(None, description="Stok durumuna göre filtrele"),
    is_featured: Optional[bool] = Query(None, description="Öne çıkan ürünleri filtrele"),
    is_vegetarian: Optional[bool] = Query(None, description="Vejeteryan ürünleri filtrele"),
    is_vegan: Optional[bool] = Query(None, description="Vegan ürünleri filtrele"),
    is_gluten_free: Optional[bool] = Query(None, description="Glutensiz ürünleri filtrele"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum fiyat"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum fiyat"),
    search: Optional[str] = Query(None, description="İsim veya açıklamada ara"),
    db: Session = Depends(get_db)
):
    """
    Menüdeki tüm ürünleri listeler.
    - Çeşitli filtreleme seçenekleri sunar
    - Sayfalama destekler
    - Arama yapılabilir
    """
    query = db.query(MenuItem).join(Category)
    
    # Filtreleme
    if category_id is not None:
        query = query.filter(MenuItem.category_id == category_id)
    
    if is_available is not None:
        query = query.filter(MenuItem.is_available == is_available)
    
    if is_featured is not None:
        query = query.filter(MenuItem.is_featured == is_featured)
    
    if is_vegetarian is not None:
        query = query.filter(MenuItem.is_vegetarian == is_vegetarian)
    
    if is_vegan is not None:
        query = query.filter(MenuItem.is_vegan == is_vegan)
    
    if is_gluten_free is not None:
        query = query.filter(MenuItem.is_gluten_free == is_gluten_free)
    
    if min_price is not None:
        query = query.filter(MenuItem.price >= min_price)
    
    if max_price is not None:
        query = query.filter(MenuItem.price <= max_price)
    
    # Arama
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (MenuItem.name.ilike(search_term)) | 
            (MenuItem.description.ilike(search_term))
        )
    
    # Sıralama ve sayfalama
    items = query.order_by(MenuItem.id.asc()).offset(skip).limit(limit).all()

    
    # Response formatı
    result = []
    for item in items:
        result.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "category_name": item.category.name,
            "is_available": item.is_available,
            "is_featured": item.is_featured,
            "image_url": item.image_url
        })
    
    return result

# Tek bir menü öğesini getir (GET)
@router.get("/{item_id}", response_model=MenuItemResponse)
def get_menu_item(
    item_id: int,
    db: Session = Depends(get_db)
):
    """
    Belirli bir menü öğesini ID ile getirir.
    - Kategori bilgilerini de içerir
    """
    item = db.query(MenuItem).options(joinedload(MenuItem.category)).filter(MenuItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menü öğesi bulunamadı: ID={item_id}"
        )
    
    return item

# Yeni menü öğesi ekle (POST) - Sadece giriş yapmış kullanıcılar
@router.post("/", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item(
    item_data: MenuItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    Yeni bir menü öğesi oluşturur.
    - Authentication gereklidir
    - Kategori ID'si geçerli olmalıdır
    """
    # Kategori var mı kontrol et
    category = db.query(Category).filter(Category.id == item_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Geçersiz kategori ID: {item_data.category_id}"
        )
    
    # Aynı isimde ürün var mı kontrol et (aynı kategoride)
    existing = db.query(MenuItem).filter(
        MenuItem.name == item_data.name,
        MenuItem.category_id == item_data.category_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu kategoride aynı isimde bir ürün zaten mevcut: {item_data.name}"
        )
    
    # Yeni ürün oluştur
    new_item = MenuItem(
        **item_data.dict(),
        created_by=current_user.id
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    
    # Kategori bilgileriyle birlikte döndür
    return db.query(MenuItem).options(joinedload(MenuItem.category)).filter(MenuItem.id == new_item.id).first()

# Menü öğesini güncelle (PUT) - Sadece giriş yapmış kullanıcılar
@router.put("/{item_id}", response_model=MenuItemResponse)
def update_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    Mevcut bir menü öğesini günceller.
    - Authentication gereklidir
    - Sadece gönderilen alanlar güncellenir (PATCH benzeri)
    """
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menü öğesi bulunamadı: ID={item_id}"
        )
    
    # Kategori değişiyorsa, yeni kategorinin geçerli olduğunu kontrol et
    if item_data.category_id and item_data.category_id != item.category_id:
        category = db.query(Category).filter(Category.id == item_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Geçersiz kategori ID: {item_data.category_id}"
            )
    
    # İsim değişiyorsa, aynı kategoride başka ürün var mı kontrol et
    if item_data.name and item_data.name != item.name:
        category_id = item_data.category_id if item_data.category_id else item.category_id
        existing = db.query(MenuItem).filter(
            MenuItem.name == item_data.name,
            MenuItem.category_id == category_id,
            MenuItem.id != item_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu kategoride aynı isimde başka bir ürün mevcut: {item_data.name}"
            )
    
    # Güncelleme yap
    update_dict = item_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    
    # Kategori bilgileriyle birlikte döndür
    return db.query(MenuItem).options(joinedload(MenuItem.category)).filter(MenuItem.id == item.id).first()

# Menü öğesini sil (DELETE) - Sadece giriş yapmış kullanıcılar
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    Bir menü öğesini siler.
    - Authentication gereklidir
    """
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Menü öğesi bulunamadı: ID={item_id}"
        )
    
    db.delete(item)
    db.commit()
    
    return None

# PATCH endpoint'i (kısmi güncelleme için alternatif)
@router.patch("/{item_id}", response_model=MenuItemResponse)
def patch_menu_item(
    item_id: int,
    item_data: MenuItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    PATCH metodu ile menü öğesini günceller.
    PUT ile aynı işlevi görür, sadece HTTP metodu farklıdır.
    """
    return update_menu_item(item_id, item_data, db, current_user)