from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class MenuItem(Base):
    """Menüdeki yemekler/içecekler"""
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    
    # Kategori ilişkisi
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    category = relationship("Category", back_populates="menu_items")
    
    # Ek özellikler
    image_url = Column(String(500))
    calories = Column(Integer)
    preparation_time = Column(Integer)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_available = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    # SQL Server için DateTime düzenlemesi
    created_at = Column(DateTime, server_default=func.getdate())
    updated_at = Column(DateTime, onupdate=func.getdate())
    
    # Ekleyen kullanıcı
    created_by = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")