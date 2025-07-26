from datetime import datetime, timedelta, timezone
from typing import Dict, List
from dataclasses import dataclass
import logging
import pandas as pd
from holidays import country_holidays
from sqlalchemy import func, and_, desc, Integer
from models import Transaction
from database import SessionLocal
from cachetools import TTLCache

@dataclass
class FraudRule:
    name: str
    weight: float
    category: str
    description: str

class AdvancedFraudDetector:
    def __init__(self):
        self.rules = {
            'amount_based': [
                self.high_amount_rule,
                self.round_amount_rule,
            ],
            'velocity_based': [
                self.transaction_velocity_rule,
                self.merchant_velocity_rule
            ],
            'behavioral': [
                self.time_pattern_rule,
                self.location_anomaly_rule,
            ]
        }
        self.user_profiles = TTLCache(ttl=600)
        self.merchant_profiles = TTLCache(ttl=600)

    async def analyze_transaction(self, transaction: Dict) -> Dict:
        """
        Comprehensive fraud analysis using multiple detection approaches
        """
        start_time = datetime.now(timezone.utc)

        # Initialize results - what the API will send back - declared in main.py
        analysis_result = {
            'transaction_id': transaction.get('transaction_id'),
            'is_fraud': False,
            'fraud_score': 0.0,
            'confidence': 0.0,
            'risk_level': 'LOW',
            'triggered_rules': [],
            'rule_details': {},
            'processing_time_ms': 0,
            'recommendation': 'APPROVE'
        }

        try:
            # Get user behavioral profile
            user_profile = await self.get_user_profile(transaction['user_id'])
            # Run all fraud detection rules
            for category, rule_list in self.rules.items():
                for rule_func in rule_list:
                    rule_result = await rule_func(transaction, user_profile)

                    if rule_result['triggered']:
                        analysis_result['triggered_rules'].append(rule_result)
                        analysis_result['fraud_score'] += rule_result['weight']
                        analysis_result['rule_details'][rule_result['rule_name']] = rule_result
            # Normalize fraud score
            analysis_result['fraud_score'] = min(analysis_result['fraud_score'], 1.0)
            # Calculate confidence based on rule agreement
            analysis_result['confidence'] = self.calculate_confidence(
                analysis_result['triggered_rules']
            )
            # Determine risk level and recommendation
            analysis_result['risk_level'] = self.calculate_risk_level(
                analysis_result['fraud_score']
            )
            analysis_result['recommendation'] = self.get_recommendation(
                analysis_result['fraud_score'],
                analysis_result['confidence']
            )
            analysis_result['is_fraud'] = analysis_result['fraud_score'] > 0.5
            # Calculate processing time
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            analysis_result['processing_time_ms'] = int(processing_time)
            # Log for monitoring
            logging.info(
                f"Fraud analysis completed: "
                f"Score={analysis_result['fraud_score']:.3f}, "
                f"Rules={len(analysis_result['triggered_rules'])}, "
                f"Time={processing_time:.1f}ms"
            )
            return analysis_result

        except Exception as e:
            logging.error(f"Fraud analysis failed: {e}")
            analysis_result['error'] = str(e)
            return analysis_result

    # ---------- RULE FUNCTIONS ----------
    async def high_amount_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """Detect transactions with unusually high amounts"""
        amount = transaction['amount']
        user_avg = user_profile.get('avg_transaction_amount', 100)
        user_max = user_profile.get('max_transaction_amount', 500)
        # Multiple thresholds for different risk levels
        absolute_threshold = 5000
        relative_threshold = user_avg * 10
        historical_threshold = user_max * 2
        # apply the rules
        risk_score = 0.0
        details = []
        if amount > absolute_threshold:
            risk_score += 0.4
            details.append(f"Above absolute threshold: ${amount} > ${absolute_threshold}")

        if amount > relative_threshold:
            risk_score += 0.3
            details.append(f"Above relative threshold: {amount / user_avg:.1f}x average")

        if amount > historical_threshold:
            risk_score += 0.3
            details.append(f"Above historical maximum: {amount / user_max:.1f}x previous max")

        return {
            'rule_name': 'High Amount Detection',
            'triggered': risk_score > 0,
            'weight': min(risk_score, 0.6),  # Cap at 0.6
            'category': 'amount_based',
            'details': details,
            'severity': 'HIGH' if risk_score > 0.5 else 'MEDIUM' if risk_score > 0.3 else 'LOW'
        }

    
    async def round_amount_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """Detect suspiciously round amounts"""
        amount = transaction['amount']

        risk_factors = []
        risk_score = 0.0

        # Check for round numbers
        if amount % 100 == 0 and amount >= 500:
            risk_score += 0.3
            risk_factors.append(f"Round hundred amount: ${amount}")
        elif amount % 50 == 0 and amount >= 200:
            risk_score += 0.2
            risk_factors.append(f"Round fifty amount: ${amount}")

        # Check for patterns like 9.99 or similar
        if str(amount).endswith('.99') and amount > 100:
            risk_score += 0.2
            risk_factors.append(f"Suspicious decimal pattern: ${amount}")

        return {
            'rule_name': 'Round Amount Detection',
            'triggered': len(risk_factors) > 0,
            'weight': min(risk_score, 0.4),
            'category': 'amount_based',
            'details': risk_factors,
            'severity': 'MEDIUM' if risk_score > 0.3 else 'LOW'
        }

    async def transaction_velocity_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """
        Detect high-velocity transaction patterns
        Check how many transactions a user has made in a short time window
        """
        user_id = transaction['user_id']
        current_time = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))

        # Check different time windows
        windows = [
            ('1_minute', 1, 2),  # Max 2 transactions per minute
            ('5_minutes', 5, 5),  # Max 5 transactions per 5 minutes
            ('15_minutes', 15, 10),  # Max 10 transactions per 15 minutes
            ('1_hour', 60, 25)  # Max 25 transactions per hour
        ]

        violations = []
        total_risk = 0.0

        for window_name, minutes, max_transactions in windows:
            window_start = current_time - timedelta(minutes=minutes)

            # Get transaction count in this window (simulate database query)
            recent_count = await self.get_transaction_count_in_window(
                user_id, window_start, current_time
            )

            if recent_count >= max_transactions:
                violation_severity = min((recent_count - max_transactions + 1) / max_transactions, 1.0)
                total_risk += violation_severity * 0.2  # Each window contributes up to 0.2
                violations.append(
                    f"{recent_count} transactions in {window_name} (limit: {max_transactions})"
                )

        return {
            'rule_name': 'Transaction Velocity',
            'triggered': len(violations) > 0,
            'weight': min(total_risk, 0.7),
            'category': 'velocity_based',
            'details': violations,
            'severity': 'CRITICAL' if total_risk > 0.6 else 'HIGH' if total_risk > 0.4 else 'MEDIUM'
        }

    async def merchant_velocity_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """Detect multiple transactions to same merchant in short time"""
        user_id = transaction['user_id']
        merchant_id = transaction.get('merchant_id')

        if not merchant_id:
            return {
                'rule_name': 'Merchant Velocity',
                'triggered': False,
                'weight': 0.0,
                'category': 'velocity_based',
                'details': [],
                'severity': 'LOW'
            }

        # Check transactions to same merchant in last hour
        current_time = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))
        hour_ago = current_time - timedelta(hours=1)

        merchant_transactions = await self.get_merchant_transactions_in_window(
            user_id, merchant_id, hour_ago, current_time
        )

        risk_factors = []
        risk_score = 0.0

        if len(merchant_transactions) >= 3:
            risk_score += 0.4
            risk_factors.append(f"{len(merchant_transactions)} transactions to same merchant in 1 hour")

        # Check for rapid-fire transactions (within 5 minutes)
        five_minutes_ago = current_time - timedelta(minutes=5)
        recent_merchant_transactions = [t for t in merchant_transactions
                                        if t['timestamp'] >= five_minutes_ago]

        if len(recent_merchant_transactions) >= 2:
            risk_score += 0.3
            risk_factors.append(f"{len(recent_merchant_transactions)} transactions to same merchant in 5 minutes")

        return {
            'rule_name': 'Merchant Velocity',
            'triggered': len(risk_factors) > 0,
            'weight': min(risk_score, 0.5),
            'category': 'velocity_based',
            'details': risk_factors,
            'severity': 'HIGH' if risk_score > 0.4 else 'MEDIUM'
        }

    async def time_pattern_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """Detect transactions at unusual times"""
        transaction_time = datetime.fromisoformat(transaction['timestamp'].replace('Z', '+00:00'))
        hour = transaction_time.hour
        day_of_week = transaction_time.weekday()
        # Get user common times
        user_common_hours = user_profile.get('common_hours', [])
        user_common_days = user_profile.get('common_days', [])
        # Check now the hours and days
        risk_factors = []
        risk_score = 0.0
        # Late night transactions (2 AM - 5 AM)
        if 2 <= hour <= 5 and hour not in user_common_hours:
            risk_score += 0.4
            risk_factors.append(f"Late night transaction: {hour:02d}:00")
        # Weekend transaction by a business-hours user
        if day_of_week in [5, 6] and user_common_days and day_of_week not in user_common_days:
            if all(day < 5 for day in user_common_days):
                risk_score += 0.3
                risk_factors.append("Weekend transaction for business-hours user")

        # Holiday transactions (simulate holiday database)
        if self.is_holiday(transaction_time.date(), transaction['location_country']):
            if len(user_common_days) > 0:  # Has established pattern
                risk_score += 0.2
                risk_factors.append("Holiday transaction")

        return {
            'rule_name': 'Time Pattern Analysis',
            'triggered': len(risk_factors) > 0,
            'weight': min(risk_score, 0.5),
            'category': 'behavioral',
            'details': risk_factors,
            'severity': 'MEDIUM' if risk_score > 0.3 else 'LOW'
        }

    
    async def location_anomaly_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """Detect transactions from unusual locations"""
        transaction_country = transaction.get('location_country', 'Unknown')
        transaction_city = transaction.get('location_city', 'Unknown')
        # get user countries
        user_countries = user_profile.get('common_countries', [])
        user_cities = user_profile.get('common_cities', [])
        # Check risk
        risk_factors = []
        risk_score = 0.0
        if transaction_country not in user_countries:
            if len(user_countries) > 0:  # User has transaction history
                risk_score += 0.4
                risk_factors.append(f"New country: {transaction_country}")
            else:
                risk_score += 0.1  # First-time user, less suspicious
        # New city check
        if transaction_city not in user_cities:
            if len(user_cities) > 5:  # User has established patterns
                risk_score += 0.3
                risk_factors.append(f"New city: {transaction_city}")
        # Check if it is a Placeholder
        high_risk_countries = ['Country_X', 'Country_Y']
        if transaction_country in high_risk_countries:
            risk_score += 0.5
            risk_factors.append(f"High-risk country: {transaction_country}")
        return {
            'rule_name': 'Location Anomaly',
            'triggered': len(risk_factors) > 0,
            'weight': min(risk_score, 0.8),
            'category': 'behavioral',
            'details': risk_factors,
            'severity': 'CRITICAL' if risk_score > 0.7 else 'HIGH' if risk_score > 0.4 else 'MEDIUM'
        }

    # ---------- PROFILE & UTILITIES ----------
    async def get_user_profile(self, user_id: str) -> Dict:
        """Get or create user behavioral profile"""
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]

        # Simulate database query for user transaction history
        profile = await self.build_user_profile(user_id)
        self.user_profiles[user_id] = profile
        return profile

    async def build_user_profile(self, user_id: str) -> Dict:
        """Build comprehensive user behavioral profile"""
        # Simulate querying user's transaction history
        user_transactions = await self.get_user_transaction_history(user_id)

        if not user_transactions:
            return {
                'transaction_count': 0,
                'avg_transaction_amount': 0,
                'max_transaction_amount': 0,
                'common_hours': [],
                'common_days': [],
                'common_countries': [],
                'common_cities': [],
                'common_categories': [],
                'risk_score': 0.5  # Neutral for new users
            }

        df = pd.DataFrame(user_transactions)

        profile = {
            'transaction_count': len(df),
            'avg_transaction_amount': df['amount'].mean(),
            'max_transaction_amount': df['amount'].max(),
            'std_transaction_amount': df['amount'].std(),
            'common_hours': df['hour'].mode().tolist()[:3],
            'common_days': df['day_of_week'].mode().tolist()[:3],
            'common_countries': df['country'].value_counts().head(3).index.tolist(),
            'common_cities': df['city'].value_counts().head(5).index.tolist(),
            'common_categories': df['category'].value_counts().head(5).index.tolist(),
            'last_location': (df.iloc[-1]['country'], df.iloc[-1]['city']),
            'last_transaction_time': df.iloc[-1]['timestamp'],
            'risk_score': self.calculate_user_risk_score(df)
        }

        return profile

    # ---------- DATABASE FETCHING ----------
    async def get_user_transaction_history(self, user_id: str, limit: int = 100) -> List[Dict]:
        """
        Fetch user transaction history from database
        """
        db = SessionLocal()
        try:
            # Query last 100 transactions for the user
            transactions = db.query(Transaction).filter(Transaction.user_id == user_id) \
                .order_by(desc(Transaction.timestamp)).limit(limit).all()

            # Convert to list of dictionaries for pandas processing
            transaction_list = []
            for txn in transactions:
                transaction_list.append({
                    'transaction_id': txn.id,
                    'user_id': txn.user_id,
                    'amount': txn.amount,
                    'timestamp': txn.timestamp,
                    'hour': txn.timestamp.hour,
                    'day_of_week': txn.timestamp.weekday(),
                    'country': self._extract_country_from_location(txn.location),
                    'city': self._extract_city_from_location(txn.location),
                    'category': txn.merchant_category,
                    'transaction_type': txn.transaction_type,
                    'card_present': txn.card_present
                })

            return transaction_list

        finally:
            db.close()

    
    async def get_transaction_count_in_window(self, user_id: str, start: datetime, end: datetime) -> int:
        """
        Count transactions for a user within a time window
        """
        db = SessionLocal()
        try:
            count = db.query(func.count(Transaction.id)) \
                .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.timestamp >= start,
                    Transaction.timestamp <= end
                )
            ) \
                .scalar()

            return count or 0

        finally:
            db.close()

    
    async def get_merchant_transactions_in_window(self, user_id: str, merchant_category: str,
                                                  start: datetime, end: datetime) -> List[Dict]:
        """
        Get all transactions for a user in a specific merchant category within time window
        Note: Using merchant_category as proxy for merchant_id since that's what's in your schema
        """
        db = SessionLocal()
        try:
            transactions = db.query(Transaction) \
                .filter(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.merchant_category == merchant_category,
                    Transaction.timestamp >= start,
                    Transaction.timestamp <= end
                )
            ) \
                .order_by(Transaction.timestamp) \
                .all()

            transaction_list = []
            for txn in transactions:
                transaction_list.append({
                    'transaction_id': txn.id,
                    'user_id': txn.user_id,
                    'merchant_category': txn.merchant_category,
                    'timestamp': txn.timestamp,
                    'amount': txn.amount
                })

            return transaction_list

        finally:
            db.close()

    async def get_merchant_profile(self, merchant_category: str) -> Dict:
        """
        Get merchant category statistics and profile
        Since your schema uses merchant_category instead of merchant_id
        """
        if merchant_category in self.merchant_profiles:
            return self.merchant_profiles[merchant_category]

        db = SessionLocal()
        try:
            # Get statistics for this merchant category
            stats = db.query(
                func.count(Transaction.id).label('transaction_count'),
                func.avg(Transaction.amount).label('avg_amount'),
                func.max(Transaction.amount).label('max_amount'),
                func.min(Transaction.amount).label('min_amount'),
                func.stddev(Transaction.amount).label('std_amount'),
                func.sum(Transaction.is_fraud.cast(Integer)).label('fraud_count')
            ).filter(Transaction.merchant_category == merchant_category).first()

            if stats.transaction_count == 0:
                # No transactions for this merchant category
                profile = {
                    'merchant_category': merchant_category,
                    'avg_transaction_amount': 0,
                    'transaction_count': 0,
                    'fraud_rate': 0.0,
                    'risk_category': 'UNKNOWN',
                    'std_amount': 0
                }
            else:
                fraud_rate = (stats.fraud_count or 0) / stats.transaction_count

                # Determine risk category based on fraud rate
                if fraud_rate > 0.05:  # >5%
                    risk_category = 'HIGH'
                elif fraud_rate > 0.02:  # >2%
                    risk_category = 'MEDIUM'
                else:
                    risk_category = 'LOW'

                profile = {
                    'merchant_category': merchant_category,
                    'avg_transaction_amount': float(stats.avg_amount or 0),
                    'max_transaction_amount': float(stats.max_amount or 0),
                    'min_transaction_amount': float(stats.min_amount or 0),
                    'std_transaction_amount': float(stats.std_amount or 0),
                    'transaction_count': stats.transaction_count,
                    'fraud_count': stats.fraud_count or 0,
                    'fraud_rate': fraud_rate,
                    'risk_category': risk_category
                }

            self.merchant_profiles[merchant_category] = profile
            return profile

        finally:
            db.close()

    
    def calculate_user_risk_score(self, df) -> float:
        """
        Calculate overall user risk score based on transaction history DataFrame
        """
        if df.empty:
            return 0.5  # Neutral for no history

        risk_factors = []

        # Amount variance (high variance = higher risk)
        if len(df) > 1:
            amount_std = df['amount'].std()
            amount_mean = df['amount'].mean()
            if amount_mean > 0:
                cv = amount_std / amount_mean  # Coefficient of variation
                if cv > 2.0:  # Very high variance
                    risk_factors.append(0.3)
                elif cv > 1.0:
                    risk_factors.append(0.1)

        # Time pattern irregularity
        hour_distribution = df['hour'].value_counts()
        unique_hours = len(hour_distribution)
        if unique_hours > 15:  # Active at many different hours (unusual)
            risk_factors.append(0.2)
        elif unique_hours < 3 and len(df) > 10:  # Very consistent timing (also unusual)
            risk_factors.append(0.1)

        # Geographic diversity
        unique_countries = df['country'].nunique()
        if unique_countries > 5:
            risk_factors.append(0.3)
        elif unique_countries > 3:
            risk_factors.append(0.1)

        # Transaction frequency
        if len(df) > 1:
            time_span = (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 86400  # days
            if time_span > 0:
                transactions_per_day = len(df) / time_span
                if transactions_per_day > 10:  # Very high frequency
                    risk_factors.append(0.4)
                elif transactions_per_day > 5:
                    risk_factors.append(0.2)

        # Card not present transactions (higher risk)
        if 'card_present' in df.columns:
            cnp_ratio = (~df['card_present']).sum() / len(df)
            if cnp_ratio > 0.8:  # >80% card not present
                risk_factors.append(0.3)
            elif cnp_ratio > 0.5:  # >50% card not present
                risk_factors.append(0.1)

        # Calculate final risk score
        base_risk = 0.2  # Base risk for all users
        additional_risk = sum(risk_factors)

        return min(base_risk + additional_risk, 1.0)

    
    def _extract_country_from_location(self, location: str) -> str:
        """
        Extract country from location string
        Assumes format like "New York, NY, US" or customize based on your format
        """
        if not location:
            return 'Unknown'

        parts = location.split(',')
        if len(parts) >= 3:
            return parts[-1].strip()  # Last part is usually country
        return 'Unknown'

    
    def _extract_city_from_location(self, location: str) -> str:
        """
        Extract city from location string
        """
        if not location:
            return 'Unknown'

        parts = location.split(',')
        if len(parts) >= 1:
            return parts[0].strip()  # First part is usually city
        return 'Unknown'

    # ---------- RESULTS FUNCTIONS ----------
    def calculate_confidence(self, triggered_rules: List[Dict]) -> float:
        """Calculate confidence based on rule agreement and weights"""
        if not triggered_rules:
            return 1.0  # High confidence in legitimate transactions

        total_weight = sum(rule['weight'] for rule in triggered_rules)
        rule_count = len(triggered_rules)

        # Confidence increases with more rules agreeing
        agreement_factor = min(rule_count / 3, 1.0)  # Max at 3 rules
        weight_factor = min(float(total_weight), 1.0)

        return (agreement_factor + weight_factor) / 2

    
    def calculate_risk_level(self, fraud_score: float) -> str:
        """Convert fraud score to risk level"""
        if fraud_score >= 0.8:
            return 'CRITICAL'
        elif fraud_score >= 0.6:
            return 'HIGH'
        elif fraud_score >= 0.3:
            return 'MEDIUM'
        return 'LOW'

    def get_recommendation(self, fraud_score: float, confidence: float) -> str:
        """Get action recommendation based on score and confidence"""
        if fraud_score >= 0.8 and confidence >= 0.7:
            return 'BLOCK'
        elif fraud_score >= 0.6:
            return 'REVIEW'
        elif fraud_score >= 0.4:
            return 'MONITOR'
        else:
            return 'APPROVE'
    
    def is_holiday(self, transaction_date, country='US'):
        holidays = country_holidays(country)
        return transaction_date in holidays