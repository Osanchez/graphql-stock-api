import os
import asyncio
import asyncpg
from faker import Faker

# Load environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "default")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_PORT = os.getenv("DB_PORT", "5432")
# Faker instance for generating fake data
fake = Faker()

# SQL statements
CREATE_TABLES_SQL = """

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(10) NOT NULL,
    shares INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_transactions_stock_symbol_shares ON transactions(stock_symbol, shares);
"""

CHECK_IF_DATA_EXISTS = "SELECT COUNT(*) FROM transactions;"
INSERT_FAKE_USER = "INSERT INTO users (name, email) VALUES ($1, $2) RETURNING id;"
INSERT_FAKE_TRANSACTION = "INSERT INTO transactions (user_id, stock_symbol, shares, price) VALUES ($1, $2, $3, $4);"


async def setup_database():
    """Connects to PostgreSQL, verifies tables exist, and inserts fake data if needed."""
    conn = await asyncpg.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )

    print("Connected to the database.")

    # Create tables if they do not exist
    await conn.execute(CREATE_TABLES_SQL)
    print("Tables verified/created.")

    # Check if transactions already have data
    result = await conn.fetchval(CHECK_IF_DATA_EXISTS)

    if result == 0:
        print("No transaction data found. Populating with fake data...")

        # Insert fake users
        user_ids = []
        for _ in range(10):
            name = fake.name()
            email = fake.email()
            user_id = await conn.fetchval(INSERT_FAKE_USER, name, email)
            user_ids.append(user_id)

        # Insert fake transactions
        stock_symbols = [
            "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NFLX", "META", "NVDA", "BABA", "AMD",
            "INTC", "PYPL", "CSCO", "ADBE", "ORCL", "DIS", "V", "JPM", "WMT", "BA"
        ]
        for _ in range(200):
            user_id = fake.random_element(user_ids)
            stock_symbol = fake.random_element(stock_symbols)
            shares = fake.random_int(min=1, max=100)
            price = round(fake.pyfloat(left_digits=3, right_digits=2, positive=True), 2)
            await conn.execute(INSERT_FAKE_TRANSACTION, user_id, stock_symbol, shares, price)

        print("Fake data added successfully!")

    else:
        print("Database already contains transaction data. No fake data needed.")

    await conn.close()
    print("Database setup complete!")


# Run the async function
if __name__ == "__main__":
    asyncio.run(setup_database())
