import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# 1. Connection address to your database
# Use environment variable DATABASE_URL for production (Aiven MySQL)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

if SQLALCHEMY_DATABASE_URL:
    # Aiven MySQL URL usually starts with mysql://
    # SQLAlchemy requires mysql+pymysql://
    if SQLALCHEMY_DATABASE_URL.startswith("mysql://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    
    # Engine for Aiven MySQL with SSL requirements
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"ssl": {"ca": "/etc/ssl/certs/ca-certificates.crt"}} if os.name != 'nt' else {}
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