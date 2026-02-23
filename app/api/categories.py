from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import SessionLocal
from app.models.category import Category
from app.models.menu_item import MenuItem
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.core.deps import get_current_user, get_db,require_admin
from app.models.user import User

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

# Tüm kategorileri listele (GET)
@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0, description="Kaç kayıt atlanacak"),
    limit: int = Query(100, ge=1, le=500, description="Max kayıt sayısı"),
    is_active: Optional[bool] = Query(None, description="Sadece aktif kategoriler"),
    db: Session = Depends(get_db)
):
    query = db.query(Category)

    if is_active is not None:
        query = query.filter(Category.is_active == is_active)

    # 🔹 ID’ye göre sıralama eklendi
    query = query.order_by(Category.id.asc())

    # 🔹 skip ve limit uygulandı
    categories = query.offset(skip).limit(limit).all()

    return categories

    """
    Tüm kategorileri listeler.
    - Sayfalama destekler (skip, limit)
    - Aktif/pasif filtreleme yapılabilir
    - Her kategorideki ürün sayısını döndürür
    """
    query = db.query(Category)
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    query = query.order_by(Category.display_order, Category.name)
    categories = query.offset(skip).limit(limit).all()
    
    # Her kategori için ürün sayısını ekle
    result = []
    for cat in categories:
        cat_dict = {
            "id": cat.id,
            "name": cat.name,
            "description": cat.description,
            "is_active": cat.is_active,
            "display_order": cat.display_order,
            "created_at": cat.created_at,
            "updated_at": cat.updated_at,
            "menu_items_count": db.query(MenuItem).filter(MenuItem.category_id == cat.id).count()
        }
        result.append(CategoryResponse(**cat_dict))
    
    return result

# Tek bir kategoriyi getir (GET)
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Belirli bir kategoriyi ID ile getirir.
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kategori bulunamadı: ID={category_id}"
        )
    
    # Ürün sayısını ekle
    menu_items_count = db.query(MenuItem).filter(MenuItem.category_id == category.id).count()
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        is_active=category.is_active,
        display_order=category.display_order,
        created_at=category.created_at,
        updated_at=category.updated_at,
        menu_items_count=menu_items_count
    )

# Yeni kategori ekle (POST) - Sadece giriş yapmış kullanıcılar
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    Yeni bir kategori oluşturur.
    - Authentication gereklidir
    - Aynı isimde kategori varsa hata döner
    """
    # Aynı isimde kategori var mı kontrol et
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu isimde bir kategori zaten mevcut: {category_data.name}"
        )
    
    # Yeni kategori oluştur
    new_category = Category(**category_data.dict())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return CategoryResponse(
        id=new_category.id,
        name=new_category.name,
        description=new_category.description,
        is_active=new_category.is_active,
        display_order=new_category.display_order,
        created_at=new_category.created_at,
        updated_at=new_category.updated_at,
        menu_items_count=0
    )

# Kategori güncelle (PUT) - Sadece giriş yapmış kullanıcılar
@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    Mevcut bir kategoriyi günceller.
    - Authentication gereklidir
    - Sadece gönderilen alanlar güncellenir (PATCH benzeri)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kategori bulunamadı: ID={category_id}"
        )
    
    # İsim değişiyorsa, yeni ismin benzersiz olduğunu kontrol et
    if category_data.name and category_data.name != category.name:
        existing = db.query(Category).filter(
            Category.name == category_data.name,
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bu isimde başka bir kategori mevcut: {category_data.name}"
            )
    
    # Güncelleme yap
    update_dict = category_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    menu_items_count = db.query(MenuItem).filter(MenuItem.category_id == category.id).count()
    
    return CategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        is_active=category.is_active,
        display_order=category.display_order,
        created_at=category.created_at,
        updated_at=category.updated_at,
        menu_items_count=menu_items_count
    )

# Kategori sil (DELETE) - Sadece giriş yapmış kullanıcılar
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # Authentication gerekli
):
    """
    Bir kategoriyi siler.
    - Authentication gereklidir
    - Kategoriye ait ürünler varsa hata verir (güvenlik için)
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kategori bulunamadı: ID={category_id}"
        )
    
    # Kategoride ürün var mı kontrol et
    items_count = db.query(MenuItem).filter(MenuItem.category_id == category_id).count()
    if items_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bu kategoriye ait {items_count} ürün bulunmaktadır. Önce ürünleri silin veya başka kategoriye taşıyın."
        )
    
    db.delete(category)
    db.commit()
    
    return None