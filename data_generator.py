"""
Generate realistic synthetic transaction data for testing fraud detection systems.
Run it using `python data_generator.py`
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict

import pandas as pd
import numpy as np
from faker import Faker

# === Constants ===
FRAUD_TYPES = ['high_amount', 'velocity', 'unusual_time', 'location']
FRAUD_PROBABILITY = 0.05
CURRENCY = 'USD'
HOURS_PROB_DISTRIBUTION = np.array([
    0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05,
    0.08, 0.10, 0.12, 0.15, 0.12, 0.10, 0.08, 0.05,
    0.03, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01
])
HOURS_PROB_DISTRIBUTION = HOURS_PROB_DISTRIBUTION / HOURS_PROB_DISTRIBUTION.sum()
# print(sum(HOURS_PROB_DISTRIBUTION))  # Should be 1.0

class TransactionGenerator:
    def __init__(self):
        self.fake = Faker()
        self.merchants = self.generate_merchants()
        self.users = self.generate_users()

    def generate_realistic_transactions(self, count: int = 10000) -> pd.DataFrame:
        """Generate a realistic batch of transaction records with some fraud cases."""
        transactions = []

        for i in range(count):
            user = random.choice(self.users)
            merchant = random.choice(self.merchants)

            is_fraud = random.random() < FRAUD_PROBABILITY
            fraud_type = random.choice(FRAUD_TYPES) if is_fraud else None
            amount = self._generate_amount(fraud_type)

            timestamp = self._generate_timestamp(is_fraud, fraud_type)

            transactions.append({
                'transaction_id': f"txn_{i:08d}",
                'user_id': user['user_id'],
                'merchant_id': merchant['merchant_id'],
                'amount': round(amount, 2),
                'currency': CURRENCY,
                'location_country': merchant['country'],
                'location_city': merchant['city'],
                'timestamp': timestamp,
                'is_fraud': is_fraud,
                'ip_address': self.fake.ipv4(),
                'user_agent': self.fake.user_agent()
            })

        return pd.DataFrame(transactions)

    @staticmethod
    def _generate_amount(fraud_type: str = None) -> float:
        """Generate transaction amount based on fraud type."""
        if fraud_type == 'high_amount':
            return random.uniform(5000, 50000)
        elif fraud_type == 'velocity':
            return random.uniform(100, 1000)
        elif fraud_type == 'unusual_time':
            return random.uniform(200, 2000)
        elif fraud_type == 'location':
            return random.uniform(500, 5000)
        else:
            # Normal transaction with log-normal distribution
            return np.random.lognormal(mean=np.log(50), sigma=1.2)

    @staticmethod
    def _generate_timestamp(is_fraud: bool, fraud_type: str = None) -> datetime:
        """Generate realistic transaction timestamps with temporal fraud simulation."""
        base_time = datetime.now() - timedelta(days=30)
        days_ago = random.randint(0, 29)

        if is_fraud and fraud_type == 'unusual_time':
            hour = random.choice(range(1, 6))  # Late night hours
        else:
            hour = np.random.choice(range(24), p=HOURS_PROB_DISTRIBUTION)

        return base_time + timedelta(
        days=int(days_ago),
        hours=int(hour),
        minutes=int(random.randint(0, 59)),
        seconds=int(random.randint(0, 59))
    )

    @staticmethod
    def truncate_str(s, max_len):
        if s is None:
            return None
        return s[:max_len]

    def generate_users(self) -> List[Dict]:
        """Generate a list of realistic fake users"""
        users = []
        for i in range(1000):
            users.append({
                'user_id': f"user_{i:04d}",
                'name': self.truncate_str(self.fake.name(), 100),
                'email': self.truncate_str(self.fake.unique.email(), 100),
                'phone': self.truncate_str(self.fake.phone_number(), 20),
                'registration_date': self.fake.date_between(start_date='-5y', end_date='today'),
                'risk_profile': self.truncate_str(random.choices(['LOW', 'NORMAL', 'HIGH'], weights=[0.1, 0.8, 0.1])[0], 20),
                'lifetime_value': round(random.uniform(100, 10000), 2)
            })
        return users

    def generate_merchants(self) -> List[Dict]:
        """Generate a list of realistic fake merchants"""
        categories = ['Electronics', 'Clothing', 'Food', 'Travel', 'Entertainment', 'Health']
        countries = ['USA', 'UK', 'Germany', 'India', 'Japan', 'Canada']

        merchants = []
        for i in range(200):
            merchants.append({
                'merchant_id': f"merchant_{i:04d}",
                'name': self.truncate_str(self.fake.company(), 200),  # your schema allows 200 chars
                'category': self.truncate_str(random.choice(categories), 50),
                'risk_level': self.truncate_str(random.choices(['LOW', 'MEDIUM', 'HIGH'], weights=[0.7, 0.2, 0.1])[0], 20),
                'country': self.truncate_str(random.choice(countries), 50),
                'city': self.truncate_str(self.fake.city(), 100),
                'avg_transaction_amount': round(random.uniform(20, 500), 2)
            })
        return merchants