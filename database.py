from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float)
    merchant_category = Column(String)
    location = Column(String)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    card_present = Column(Boolean)
    transaction_type = Column(String)  # online, pos, atm
    is_fraud = Column(Boolean, default=False)
    fraud_score = Column(Float, default=0.0)
    processed_at = Column(DateTime)


class FraudAlert(Base):
    __tablename__ = "fraud_alerts"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, index=True)
    alert_type = Column(String)
    severity = Column(String)  # low, medium, high, critical
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    resolved = Column(Boolean, default=False)


# Create tables
Base.metadata.create_all(bind=engine)