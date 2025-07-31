from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import asyncpg
import fraud_detector
from datetime import datetime, timezone
from typing import List, Optional
import logging
import asyncio

from pydantic import BaseModel
DATABASE_URL = "postgresql://bothainakarakrah@localhost/fraud_db"
# Configure logging - see info/errors in the terminal during API usage.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Fraud Detection API",
    description="High-Performance Real-Time Fraud Detection System",
    version="2.0.0"
)

"""
Middleware for performance.
GZipMiddleware - Compresses responses larger than 1000 bytes.
CORSMiddleware - Allows access from frontend apps
"""
allow_origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DatabaseManager:
    def __init__(self):
        self.pool = None
    # sets up a pool with 10–50 connections.
    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=10,
            max_size=50,
            command_timeout=60
        )
    # runs a query using an available connection from the pool.
    async def execute_query(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)


db_manager = DatabaseManager()


@app.on_event("startup")
async def startup_event():
    await db_manager.create_pool()
    logger.info("Database connection pool created")

# what the client sends.
class TransactionRequest(BaseModel):
    user_id: str
    merchant_id: str
    amount: float
    currency: str = "USD"
    location_country: str
    location_city: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

# what the API returns
class FraudAnalysisResponse(BaseModel):
    transaction_id: str
    is_fraud: bool
    fraud_score: float
    confidence: float
    risk_level: str
    triggered_rules: List[str]
    processing_time_ms: int
    recommendation: str


@app.post("/api/transactions/analyze", response_model=FraudAnalysisResponse)
async def analyze_transaction(
        transaction: TransactionRequest,
        background_tasks: BackgroundTasks
):
    start_time = datetime.now(timezone.utc)

    try:
        # Generate unique transaction ID
        transaction_id = f"txn_{int(start_time.timestamp())}_{hash(transaction.user_id) % 10000}"

        # Perform fraud analysis
        fraud_detector_instance = fraud_detector.AdvancedFraudDetector()
        fraud_result = await fraud_detector_instance.analyze_transaction(transaction.model_dump())

        # Store transaction in database
        background_tasks.add_task(store_transaction, transaction_id, transaction, fraud_result)

        # Calculate processing time
        processing_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

        return FraudAnalysisResponse(
            transaction_id=transaction_id,
            is_fraud=fraud_result['is_fraud'],
            fraud_score=fraud_result['fraud_score'],
            confidence=fraud_result['confidence'],
            risk_level=fraud_result['risk_level'],
            triggered_rules=fraud_result['triggered_rules'],
            processing_time_ms=processing_time,
            recommendation=fraud_result['recommendation']
        )

    except Exception as e:
        logger.error(f"Transaction analysis failed: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

"""
SQL query calculates:
    1. Total transactions
	2. Total fraud cases
	3. Average fraud score
	4. Transactions in last hour/day
	5. Stats for the last 7 days only

Returns them in a simple JSON format, useful for a React dashboard frontend.
"""
@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Real-time dashboard statistics"""
    try:
        stats_query = """
        SELECT 
            COUNT(*) as total_transactions,
            COUNT(*) FILTER (WHERE is_fraud = true) as fraud_count,
            AVG(fraud_score) FILTER (WHERE fraud_score IS NOT NULL) as avg_fraud_score,
            COUNT(*) FILTER (WHERE timestamp > NOW() - INTERVAL '1 hour') as hourly_transactions,
            COUNT(*) FILTER (WHERE timestamp > NOW() - INTERVAL '1 day') as daily_transactions
        FROM transactions 
        WHERE timestamp > NOW() - INTERVAL '7 days'
        """

        result = await db_manager.execute_query(stats_query)

        return {
            "total_transactions": result[0]['total_transactions'],
            "fraud_detected": result[0]['fraud_count'],
            "fraud_rate": result[0]['fraud_count'] / max(result[0]['total_transactions'], 1) * 100,
            "avg_fraud_score": float(result[0]['avg_fraud_score'] or 0),
            "transactions_per_hour": result[0]['hourly_transactions'],
            "transactions_per_day": result[0]['daily_transactions'],
            "system_health": "OPERATIONAL"
        }

    except Exception as e:
        logger.error(f"Dashboard stats failed: {e}")
        return {"error": "Unable to fetch statistics"}

@app.websocket("/ws")
async def websocket_dashboard(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            stats = await get_dashboard_stats()
            await websocket.send_json({
                "type": "dashboard_update",
                "payload": stats
            })
            await asyncio.sleep(10)  # Update every 10 seconds
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")

async def store_transaction(transaction_id: str, transaction: TransactionRequest, fraud_result: dict):
    try:
        insert_query = """
        INSERT INTO transactions (
            transaction_id, user_id, merchant_id, amount, currency,
            location_country, location_city, ip_address, user_agent,
            is_fraud, fraud_score, confidence, risk_level,
            triggered_rules, recommendation, timestamp
        ) VALUES (
            $1, $2, $3, $4, $5,
            $6, $7, $8, $9,
            $10, $11, $12, $13,
            $14, $15, NOW()
        )
        """

        await db_manager.execute_query(
            insert_query,
            transaction_id,
            transaction.user_id,
            transaction.merchant_id,
            transaction.amount,
            transaction.currency,
            transaction.location_country,
            transaction.location_city,
            transaction.ip_address,
            transaction.user_agent,
            fraud_result['is_fraud'],
            fraud_result['fraud_score'],
            fraud_result['confidence'],
            fraud_result['risk_level'],
            fraud_result['triggered_rules'],  # JSON list
            fraud_result['recommendation']
        )

        logger.info(f"Transaction {transaction_id} stored successfully.")

    except Exception as e:
        logger.error(f"Failed to store transaction {transaction_id}: {e}")