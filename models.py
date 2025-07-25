from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, DECIMAL, ARRAY, Date
from database import Base
from datetime import datetime, timezone


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    registration_date = Column(Date)
    risk_profile = Column(String(20), default='NORMAL')
    lifetime_value = Column(DECIMAL(12, 2), default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc))

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    risk_level = Column(String(20), default='LOW')
    country = Column(String(50))
    avg_transaction_amount = Column(DECIMAL(10, 2))

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, nullable=False)
    user_id = Column(String(50), index=True)
    merchant_id = Column(String(50))
    amount = Column(DECIMAL(12, 2), nullable=False)
    currency = Column(String(3), default='USD')
    transaction_type = Column(String(50))
    location_country = Column(String(50))
    location_city = Column(String(100))
    ip_address = Column(String)
    user_agent = Column(Text)
    timestamp = Column(DateTime, nullable=False, index=True)
    processing_time_ms = Column(Integer)
    is_fraud = Column(Boolean, default=False)
    fraud_score = Column(DECIMAL(5, 4), default=0.0, index=True)
    fraud_reason = Column(ARRAY(Text))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class FraudAlert(Base):
    __tablename__ = "fraud_alerts"
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    confidence_score = Column(DECIMAL(3, 2))
    triggered_rules = Column(ARRAY(Text))
    investigation_status = Column(String(20), default='PENDING')
    false_positive = Column(Boolean)
    created_at = Column(DateTime, default=datetime.now(timezone.utc), index=True)
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))