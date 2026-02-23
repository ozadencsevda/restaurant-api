from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import ping_db, Base, engine
from app.core.config import settings
from app.core.deps import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.search import router as search_router
from app.api.suggest import router as suggest_router

# Router'ları import et
from app.api.auth import router as auth_router
from app.api.me import router as me_router
from app.api.categories import router as categories_router
from app.api.menu_items import router as menu_items_router
from app.api.featured import router as featured_router

# Model'leri import et
from app.models.user import User
from app.models.category import Category
from app.models.menu_item import MenuItem

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Restaurant Menu Management API with JWT Authentication"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları ekle
app.include_router(auth_router)
app.include_router(me_router, prefix="/api/v1")
app.include_router(categories_router)
app.include_router(featured_router)

app.include_router(search_router)
app.include_router(suggest_router)

app.include_router(menu_items_router)

# Uygulama başlangıcında tabloları oluştur
@app.on_event("startup")
def on_startup():
    """Uygulama başladığında çalışır"""
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Veritabanı tabloları kontrol edildi/oluşturuldu")
        
        # İlk kategori ekle
        from app.db.database import SessionLocal
        db = SessionLocal()
        try:
            if db.query(Category).count() == 0:
                sample_categories = [
                    Category(name="Başlangıçlar", description="Çorbalar ve mezeler", display_order=1),
                    Category(name="Ana Yemekler", description="Et, tavuk ve balık yemekleri", display_order=2),
                    Category(name="Salatalar", description="Taze salatalar", display_order=3),
                    Category(name="İçecekler", description="Sıcak ve soğuk içecekler", display_order=4),
                    Category(name="Tatlılar", description="Tatlılar ve dessert'ler", display_order=5),
                ]
                for cat in sample_categories:
                    db.add(cat)
                db.commit()
                print("✅ Örnek kategoriler eklendi")
        finally:
            db.close()
    except Exception as e:
        print(f"⚠️ Startup hatası: {e}")

# Health Check Endpoint
@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    API ve veritabanı durumunu kontrol eder
    """
    health_status = {
        "api": "ok",
        "database": "down",
        "database_type": "SQL Server",
        "database_tables": [],
        "total_users": 0,
        "total_categories": 0,
        "total_menu_items": 0
    }
    
    try:
        # Veritabanı bağlantısını test et
        db_ok = ping_db()
        health_status["database"] = "ok" if db_ok else "down"
        
        if db_ok:
            # SQL Server için tablo listesi
            result = db.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                AND TABLE_CATALOG = DB_NAME()
            """))
            health_status["database_tables"] = [row[0] for row in result]
            
            # İstatistikler
            health_status["total_users"] = db.query(User).count()
            health_status["total_categories"] = db.query(Category).count()
            health_status["total_menu_items"] = db.query(MenuItem).count()
            
    except Exception as e:
        health_status["database"] = "down"
        health_status["error"] = str(e)
    
    return health_status

# Ana Endpoint
@app.get("/", tags=["System"])
def root():
    """API ana endpoint'i"""
    return {
        "message": "🍴 Restaurant Menu API",
        "version": settings.APP_VERSION,
        "database": "SQL Server",
        "documentation": "/docs",
        "health": "/health"
    }

# API Bilgileri
@app.get("/api/info", tags=["System"])
def api_info():
    """API hakkında detaylı bilgi"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "database": "Microsoft SQL Server",
        "endpoints": {
            "auth": {
                "register": "POST /auth/register",
                "login": "POST /auth/login"
            },
            "user": {
                "profile": "GET /api/v1/me"
            },
            "categories": {
                "list": "GET /api/v1/categories",
                "get": "GET /api/v1/categories/{id}",
                "create": "POST /api/v1/categories",
                "update": "PUT /api/v1/categories/{id}",
                "delete": "DELETE /api/v1/categories/{id}"
            },
            "menu_items": {
                "list": "GET /api/v1/menu-items",
                "get": "GET /api/v1/menu-items/{id}",
                "create": "POST /api/v1/menu-items",
                "update": "PUT /api/v1/menu-items/{id}",
                "patch": "PATCH /api/v1/menu-items/{id}",
                "delete": "DELETE /api/v1/menu-items/{id}"
            },
            "system": {
                "health": "GET /health",
                "info": "GET /api/info",
                "docs": "GET /docs"
            }
        }
    }

