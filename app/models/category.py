from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.db.database import Base

class Category(Base):
    """Menü kategorileri (Örnek: Başlangıçlar, Ana Yemekler, İçecekler)"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(500))
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    
    # SQL Server için DateTime düzenlemesi
    created_at = Column(DateTime, server_default=func.getdate())
    updated_at = Column(DateTime, onupdate=func.getdate())
    
    # İlişkiler
    menu_items = relationship("MenuItem", back_populates="category", cascade="all, delete-orphan")