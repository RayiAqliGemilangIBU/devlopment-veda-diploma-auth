import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# 1. Connection address to your database
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

def get_ssl_args():
    """Determine SSL arguments based on environment."""
    if not SQLALCHEMY_DATABASE_URL:
        return {}
        
    # Standard CA paths for common Linux distros (Render/Ubuntu)
    ca_paths = [
        "/etc/ssl/certs/ca-certificates.crt",                  # Ubuntu/Debian/Render
        "/etc/pki/tls/certs/ca-bundle.crt",                   # CentOS/Fedora
        os.path.join(os.getcwd(), "veda_backend", "ca.pem"),  # Local project file
    ]
    
    for path in ca_paths:
        if os.path.exists(path):
            return {"ssl": {"ca": path}}
            
    # If no CA file found but SSL is required by URL (Aiven)
    # This fallback might work on some systems or with certain mysql drivers
    return {"ssl": {"ssl_mode": "REQUIRED"}}

if SQLALCHEMY_DATABASE_URL:
    # Convert mysql:// to mysql+pymysql:// for SQLAlchemy
    if SQLALCHEMY_DATABASE_URL.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args=get_ssl_args()
    )
else:
    # Fallback to local MySQL
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost:3306/veda"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        pool_pre_ping=True,
        pool_recycle=3600
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()