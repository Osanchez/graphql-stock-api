from ariadne import ObjectType, QueryType, gql, make_executable_schema
from ariadne.asgi import GraphQL
import asyncpg
from fastapi import FastAPI
import os


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "default")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_PORT = os.getenv("DB_PORT", "5432")

# Define types using Schema Definition Language (https://graphql.org/learn/schema/)
# Wrapping string in gql function provides validation and better error traceback

"""
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(10) NOT NULL,
    shares INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""

type_defs = gql("""
    type Query {
        transactions(limit: Int, offset: Int): [Transaction!]!
        transactionsByUser(user_id: Int!, limit: Int, offset: Int): [Transaction!]!
        transaction(id: ID!): Transaction
        topStocks: [TopStock!]!
    }
                
    type TopStock {
        stock_symbol: String!
        total_shares: Int!
    }
                

    type Transaction {
        id: ID!
        user_id: Int!
        stock_symbol: String!
        shares: Int!
        price: Float!
        timestamp: String!
    }
                
    type TransactionResponse {
        message: String!
        transaction_id: ID
    }
                
    type Mutation {
        createTransaction(user_id: Int!, stock_symbol: String!, shares: Int!, price: Float!): TransactionResponse!
    }
""")

async def get_db():
    return await asyncpg.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        host=DB_HOST,
        port=DB_PORT
    )

query = QueryType()
mutation = ObjectType("Mutation")

@query.field("transactions")
async def resolve_transactions(_, info, limit: int = 10, offset: int = 0):
    db = await get_db()
    query= "SELECT id, user_id, stock_symbol, shares, price, timestamp FROM transactions"
    params = []
    query += " ORDER BY timestamp DESC LIMIT $1 OFFSET $2"
    params.extend([limit, offset])
    rows = await db.fetch(query, *params)
    await db.close()
    return [dict(row) for row in rows]


@query.field("transaction")
async def resolve_transaction(_, info, id):
    db = await get_db()
    id = int(id)  # Ensure id is an integer
    row = await db.fetchrow("SELECT id, user_id, stock_symbol, shares, price, timestamp FROM transactions WHERE id = $1", id)
    await db.close()
    return dict(row) if row else None

@query.field("transactionsByUser")
async def resolve_transaction_by_user(_, info, user_id: int, limit: int = 10, offset: int = 0):
    db = await get_db()
    query = "SELECT id, user_id, stock_symbol, shares, price, timestamp FROM transactions WHERE user_id = $1"
    params = [user_id]
    query += " ORDER BY timestamp DESC LIMIT $2 OFFSET $3"
    params.extend([limit, offset])
    rows = await db.fetch(query, *params)
    await db.close()
    return [dict(row) for row in rows]

@query.field("topStocks")
async def resolve_top_stocks(*_):
    db = await get_db()
    rows = await db.fetch("""
                          SELECT 
                          stock_symbol, 
                          sum(shares) as total_shares 
                          FROM transactions
                          WHERE timestamp >= NOW() - INTERVAL '24 HOURS' 
                          GROUP BY stock_symbol 
                          ORDER BY SUM(shares) DESC LIMIT 5""")
    await db.close()
    return [dict(row) for row in rows]

@mutation.field("createTransaction")
async def resolve_add_transaction(_, info, user_id, stock_symbol, shares, price):
    db = await get_db()
    row = await db.fetchrow("""
        INSERT INTO transactions (user_id, stock_symbol, shares, price, timestamp) 
        VALUES ($1, $2, $3, $4, NOW()) 
        RETURNING id, user_id, stock_symbol, shares, price, timestamp
    """, user_id, stock_symbol, shares, price)
    
    await db.close()

    return {
        "message": "Transaction recorded successfully",
        "transaction_id": row["id"] if row else None
    }
    
schema = make_executable_schema(type_defs, query, mutation)

# Set up FastAPI and Ariadne
app = FastAPI()
app.add_route("/graphql", GraphQL(schema, debug=True))