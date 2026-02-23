from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

# Menü öğesi için base model
class MenuItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Ürün adı")
    description: Optional[str] = Field(None, description="Ürün açıklaması")
    price: float = Field(..., gt=0, description="Ürün fiyatı")
    category_id: int = Field(..., description="Kategori ID")
    image_url: Optional[str] = Field(None, max_length=500, description="Ürün görsel URL")
    calories: Optional[int] = Field(None, ge=0, description="Kalori değeri")
    preparation_time: Optional[int] = Field(None, ge=0, description="Hazırlama süresi (dakika)")
    is_vegetarian: bool = Field(False, description="Vejeteryan mı?")
    is_vegan: bool = Field(False, description="Vegan mı?")
    is_gluten_free: bool = Field(False, description="Glutensiz mi?")
    is_available: bool = Field(True, description="Stokta mevcut mu?")
    is_featured: bool = Field(False, description="Öne çıkan ürün mü?")

# Menü öğesi oluşturma modeli
class MenuItemCreate(MenuItemBase):
    pass

# Menü öğesi güncelleme modeli
class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    calories: Optional[int] = Field(None, ge=0)
    preparation_time: Optional[int] = Field(None, ge=0)
    is_vegetarian: Optional[bool] = None
    is_vegan: Optional[bool] = None
    is_gluten_free: Optional[bool] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None

# Kategori bilgisi için mini model
class CategoryInfo(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)

# Menü öğesi yanıt modeli
class MenuItemResponse(MenuItemBase):
    id: int
    category: CategoryInfo  # Kategori detayları
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[int]
    
    model_config = ConfigDict(from_attributes=True)

# Liste için basit yanıt modeli
class MenuItemList(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: float
    category_name: str
    is_available: bool
    is_featured: bool
    image_url: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)