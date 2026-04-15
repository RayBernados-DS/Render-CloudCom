from fastapi import FastAPI, Form, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from reportlab.pdfgen import canvas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

DATABASE_URL = "sqlite:///./kreamy_koffee.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    quantity = Column(Integer)

Base.metadata.create_all(bind=engine)

ADMIN_USERNAME = "KKAdmin"
ADMIN_PASSWORD = "KKAdmin123"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return {"status": "success"}
    return {"status": "failed"}

@app.get("/stocks")
def get_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()

@app.post("/add-stock")
def add_stock(name: str = Form(...), quantity: int = Form(...), db: Session = Depends(get_db)):
    stock = Stock(name=name, quantity=quantity)
    db.add(stock)
    db.commit()
    return {"status": "added"}

@app.post("/send-report")
def send_report(db: Session = Depends(get_db)):
    file_path = "report.pdf"
    c = canvas.Canvas(file_path)
    c.drawString(100, 800, "Kreamy Koffee Stock Report")

    y = 750
    for stock in db.query(Stock).all():
        c.drawString(100, y, f"{stock.name}: {stock.quantity}")
        y -= 20

    c.save()
    return {"status": "report generated"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "App deployed successfully!"}