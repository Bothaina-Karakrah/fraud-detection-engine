from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    registration_date: datetime
    risk_profile: str
    lifetime_value: float

class Merchant(BaseModel):
    merchant_id: str
    name: str
    category: str
    risk_level: str
    country: str
    avg_transaction_amount: float

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    merchant_id: str
    amount: float
    currency: str
    location_country: str
    location_city: str
    timestamp: datetime
    is_fraud: bool
    ip_address: str
    user_agent: str

class FraudAlert(BaseModel):
    transaction_id: str
    alert_type: str
    severity: str
    confidence_score: float
    triggered_rules: Optional[List[str]]
    investigation_status: str