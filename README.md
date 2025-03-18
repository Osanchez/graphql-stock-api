# 🚀 Backend Engineer Coding Challenge (GraphQL)

## **Objective**

Build a **stock transaction API** using **Python (FastAPI + Ariadne GraphQL) and PostgreSQL/MySQL**.

## **Requirements**

Design a **GraphQL API** that supports the following queries and mutations:

### ✅ **GraphQL API Functionalities**

1. **Mutation:** `createTransaction(userId: Int!, stockSymbol: String!, shares: Int!, price: Float!): Transaction!`
   - Adds a new stock transaction.
2. **Query:** `transactions(userId: Int): [Transaction!]!`
   - Retrieves **all transactions** (or transactions for a specific user if `userId` is provided).
3. **Query:** `transaction(id: ID!): Transaction`

   - Fetches a **single transaction by ID**.

4. **Query:** `topStocks: [TopStock!]!`
   - Returns **the top 5 most traded stocks** (by total shares) in the last **24 hours**.

---

## **📋 Database Schema (PostgreSQL/MySQL)**

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    stock_symbol VARCHAR(10) NOT NULL,
    shares INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## **📋 Example GraphQL Requests**

### **1️⃣ Create a New Stock Transaction**

#### **Mutation Request:**

```graphql
mutation ($userId: Int!, $stockSymbol: String!, $shares: Int!, $price: Float!) {
  createTransaction(
    userId: $userId
    stockSymbol: $stockSymbol
    shares: $shares
    price: $price
  ) {
    id
    user_id
    stock_symbol
    shares
    price
    timestamp
  }
}
```

#### **Variables:**

```json
{
  "userId": 101,
  "stockSymbol": "AAPL",
  "shares": 10,
  "price": 150.5
}
```

#### **Expected Response:**

```json
{
  "data": {
    "createTransaction": {
      "message": "Transaction recorded successfully",
      "transaction_id": "207"
    }
  }
}
```

---

### **2️⃣ Get All Transactions (or Filter by `userId`)**

#### **Query Request:**

```graphql
query ($userId: Int) {
  transactions(userId: $userId) {
    id
    user_id
    stock_symbol
    shares
    price
    timestamp
  }
}
```

#### **Variables (Optional, Pass `null` to get all transactions):**

```json
{
  "userId": 101
}
```

#### **Expected Response:**

```json
{
  "data": {
    "transactions": [
      {
        "id": 1,
        "user_id": 101,
        "stock_symbol": "AAPL",
        "shares": 10,
        "price": 150.5,
        "timestamp": "2024-03-17T12:30:00"
      }
    ]
  }
}
```

---

### **3️⃣ Get a Single Transaction by ID**

#### **Query Request:**

```graphql
query ($id: ID!) {
  transaction(id: $id) {
    id
    user_id
    stock_symbol
    shares
    price
    timestamp
  }
}
```

#### **Variables:**

```json
{
  "id": 1
}
```

#### **Expected Response:**

```json
{
  "data": {
    "transaction": {
      "id": 1,
      "user_id": 101,
      "stock_symbol": "AAPL",
      "shares": 10,
      "price": 150.5,
      "timestamp": "2024-03-17T12:30:00"
    }
  }
}
```

---

## **💪 Bonus Points**

✅ Implement **pagination** for transaction retrieval (e.g., `limit`, `offset`).  
✅ Use **async programming** (`asyncpg`) for better performance.  
✅ Optimize SQL queries using **indexes**.

---

## **🚀 Why Use GraphQL Instead of REST?**

🚀 **Flexible Queries** – Clients can request only the fields they need.  
🚀 **Single Endpoint** – Instead of multiple REST routes, one `/graphql` handles all queries & mutations.  
🚀 **Reduced Overfetching** – No more extra data in responses.

---
