import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lấy đường dẫn tuyệt đối đến thư mục hiện tại (ExpenseManager/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ghép thành đường dẫn tới file .db trong ExpenseManager/
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'expenses.db')}"

engine = create_engine(DATABASE_URL, echo=True)  # echo=True để in log SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_session():
    return SessionLocal()

def init_db():
    # Import models để SQLAlchemy biết đến
    import ExpenseManager.models
    Base.metadata.create_all(bind=engine)
