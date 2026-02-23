from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import urllib

# SQL Server için connection string düzenleme
def get_connection_string():
    """SQL Server connection string'ini düzenle"""
    if "mssql" in settings.DATABASE_URL:
        # URL'i parse et ve gerekli düzenlemeleri yap
        return settings.DATABASE_URL
    else:
        # PostgreSQL (eski hal)
        return settings.DATABASE_URL

# Engine oluştur
engine = create_engine(
    get_connection_string(),
    echo=False,  # SQL sorgularını görmek için True yapabilirsiniz
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def ping_db() -> bool:
    """Veritabanı bağlantısını test et"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def get_db():
    """Dependency injection için database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

