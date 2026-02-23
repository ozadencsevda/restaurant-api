from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Kategori için base model
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Kategori adı")
    description: Optional[str] = Field(None, max_length=500, description="Kategori açıklaması")
    is_active: bool = Field(True, description="Kategori aktif mi?")
    display_order: int = Field(0, ge=0, description="Görüntüleme sırası")

# Kategori oluşturma için model
class CategoryCreate(CategoryBase):
    pass

# Kategori güncelleme için model
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)

# Kategori yanıt modeli
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    menu_items_count: Optional[int] = 0  # Kategorideki ürün sayısı
    
    class Config:
        from_attributes = True