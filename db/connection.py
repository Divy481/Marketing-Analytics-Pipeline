import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

def get_database_url() -> str:
    """
    Constructs database URL from environment variables.
    Supports PostgreSQL default, or SQLite fallback for isolated unit testing / local runs.
    """
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    db_user = os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("POSTGRES_DB", "marketing_db")
    
    if db_host:
        return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    
    return "sqlite:///./marketing.db"

def get_db_engine(db_url: str = None):
    url = db_url or get_database_url()
    if url.startswith("sqlite"):
        return create_engine(url, connect_args={"check_same_thread": False})
    return create_engine(url, pool_pre_ping=True)

def get_session_factory(engine=None):
    if engine is None:
        engine = get_db_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_sql_file(file_path: str, engine=None):
    """Executes a .sql schema script line by line / statement by statement."""
    if engine is None:
        engine = get_db_engine()
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"SQL file not found at: {file_path}")
        
    with open(file_path, "r", encoding="utf-8") as f:
        sql_script = f.read()

    with engine.connect() as connection:
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
        for stmt in statements:
            connection.execute(text(stmt))
        connection.commit()
