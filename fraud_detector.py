# advanced_fraud_detector.py
from datetime import datetime, timedelta, timezone
from typing import Dict, List
from dataclasses import dataclass
import logging
from holidays import country_holidays

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
                self.amount_progression_rule
            ],
            'velocity_based': [
                self.transaction_velocity_rule,
                self.amount_velocity_rule,
                self.merchant_velocity_rule
            ],
            'behavioral': [
                self.time_pattern_rule,
                self.location_anomaly_rule,
                self.merchant_category_rule,
                self.device_fingerprint_rule
            ],
            'network': [
                self.ip_reputation_rule,
                self.geolocation_mismatch_rule,
                self.proxy_detection_rule
            ]
        }

        self.user_profiles = {}
        self.merchant_profiles = {}

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
    @staticmethod
    async def high_amount_rule(transaction: Dict, user_profile: Dict) -> Dict:
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
        pass

    async def amount_progression_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

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

    async def amount_velocity_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        """
        how much money was spent recently — and how that compares to the user’s usual spending behavior.
        """
        pass

    async def merchant_velocity_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

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
        if self.is_holiday(transaction_time.date()):
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

    @staticmethod
    async def location_anomaly_rule(transaction: Dict, user_profile: Dict) -> Dict:
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

    async def merchant_category_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

    async def device_fingerprint_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

    async def ip_reputation_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

    async def geolocation_mismatch_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

    async def proxy_detection_rule(self, transaction: Dict, user_profile: Dict) -> Dict:
        pass

    # ---------- PROFILE & UTILITIES ----------
    async def get_user_profile(self, user_id: str) -> Dict:
        pass

    async def build_user_profile(self, user_id: str) -> Dict:
        pass

    async def get_user_transaction_history(self, user_id: str) -> List[Dict]:
        pass

    async def get_transaction_count_in_window(self, user_id: str, start: datetime, end: datetime) -> int:
        pass

    async def get_merchant_profile(self, merchant_id: str) -> Dict:
        pass

    def calculate_user_risk_score(self, df) -> float:
        pass

    @staticmethod
    def calculate_confidence(triggered_rules: List[Dict]) -> float:
        """Calculate confidence based on rule agreement and weights"""
        if not triggered_rules:
            return 1.0  # High confidence in legitimate transactions

        total_weight = sum(rule['weight'] for rule in triggered_rules)
        rule_count = len(triggered_rules)

        # Confidence increases with more rules agreeing
        agreement_factor = min(rule_count / 3, 1.0)  # Max at 3 rules
        weight_factor = min(float(total_weight), 1.0)

        return (agreement_factor + weight_factor) / 2
    @staticmethod
    def calculate_risk_level(fraud_score: float) -> str:
        """Convert fraud score to risk level"""
        if fraud_score >= 0.8:
            return 'CRITICAL'
        elif fraud_score >= 0.6:
            return 'HIGH'
        elif fraud_score >= 0.3:
            return 'MEDIUM'
        else:
            return 'LOW'
    @staticmethod
    def get_recommendation(fraud_score: float, confidence: float) -> str:
        """Get action recommendation based on score and confidence"""
        if fraud_score >= 0.8 and confidence >= 0.7:
            return 'BLOCK'
        elif fraud_score >= 0.6:
            return 'REVIEW'
        elif fraud_score >= 0.4:
            return 'MONITOR'
        else:
            return 'APPROVE'
    @staticmethod
    def is_holiday(transaction_date, country='US'):
        holidays = country_holidays(country)
        return transaction_date in holidays