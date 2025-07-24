"""
Ran it using "python insert_sample_data.py"
"""
import asyncio
import asyncpg
from data_generator import TransactionGenerator
from config import DATABASE_URL

async def insert_sample_data():
    gen = TransactionGenerator()
    # Generate data
    users = gen.generate_users()
    merchants = gen.generate_merchants()
    transactions_df = gen.generate_realistic_transactions(count=5000)  # 5k transactions for example

    conn = await asyncpg.connect(DATABASE_URL)

    # Insert users
    for u in users:
        await conn.execute("""
            INSERT INTO users (user_id, name, email, phone, registration_date, risk_profile, lifetime_value)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (user_id) DO NOTHING
        """, u['user_id'], u['name'], u.get('email'), u.get('phone'), u.get('registration_date'), u.get('risk_profile', 'NORMAL'), u.get('lifetime_value', 0))

    # Insert merchants
    for m in merchants:
        await conn.execute("""
            INSERT INTO merchants (merchant_id, name, category, risk_level, country, avg_transaction_amount)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (merchant_id) DO NOTHING
        """, m['merchant_id'], m['name'], m.get('category'), m.get('risk_level', 'LOW'), m.get('country'), m.get('avg_transaction_amount'))

    # Insert transactions
    for _, t in transactions_df.iterrows():
        await conn.execute("""
            INSERT INTO transactions (transaction_id, user_id, merchant_id, amount, currency, location_country, location_city, ip_address, user_agent, timestamp, is_fraud)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (transaction_id) DO NOTHING
        """, t['transaction_id'], t['user_id'], t['merchant_id'], t['amount'], t['currency'], t['location_country'], t['location_city'], t['ip_address'], t['user_agent'], t['timestamp'], t['is_fraud'])

    await conn.close()
    print("Sample data inserted successfully!")

if __name__ == "__main__":
    asyncio.run(insert_sample_data())