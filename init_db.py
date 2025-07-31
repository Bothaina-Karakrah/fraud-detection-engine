"""
Ran it using "python init_db.py"
Check the database using "psql -U bothainakarakrah -d fraud_db"
then "dt"
"""
import asyncio
import asyncpg
from config import DATABASE_URL

async def create_tables():
    conn = await asyncpg.connect(DATABASE_URL)
    with open("schema.sql", "r") as f:
        sql = f.read()
    await conn.execute(sql)
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tables())