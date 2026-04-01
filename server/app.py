"""SQL Query Agent Environment - FastAPI Application."""
import sqlite3
import os
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    Observation,
    StateResponse,
    HealthResponse,
    RootResponse,
    ResetRequest,
    StepRequest,
)

# Database configuration
DB_PATH = "ecommerce.db"

# Global state management
class EnvironmentState:
    """Simple state manager for the environment."""
    
    def __init__(self):
        self.current_task_id: str = "task_1"
        self.step_count: int = 0
        self.episode_active: bool = False
    
    def reset(self, task_id: str):
        self.current_task_id = task_id
        self.step_count = 0
        self.episode_active = True
    
    def increment_step(self):
        self.step_count += 1
    
    def get_state(self) -> Dict[str, Any]:
        return {
            "current_task_id": self.current_task_id,
            "step_count": self.step_count,
            "episode_active": self.episode_active,
        }


# Global state instance
env_state = EnvironmentState()

# FastAPI app
app = FastAPI(
    title="SQL Query Agent Environment",
    description="A minimal SQL environment for agent training with OpenEnv-compatible API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    """Create a database connection."""
    return sqlite3.connect(DB_PATH)


def init_database():
    """Initialize the SQLite database with schema and seed data."""
    if os.path.exists(DB_PATH):
        return
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript("""
        -- Categories table
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            description TEXT
        );
        
        -- Customers table
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Products table
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category_id INTEGER,
            price REAL NOT NULL,
            stock_quantity INTEGER DEFAULT 0,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        );
        
        -- Orders table
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            total_amount REAL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        
        -- Order items table
        CREATE TABLE IF NOT EXISTS order_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
    """)
    
    # Insert seed data
    # Categories
    cursor.executemany(
        "INSERT INTO categories (category_name, description) VALUES (?, ?)",
        [
            ("Electronics", "Electronic devices and accessories"),
            ("Clothing", "Apparel and fashion items"),
            ("Books", "Books and publications"),
            ("Home & Garden", "Home improvement and garden items"),
        ]
    )
    
    # Customers
    cursor.executemany(
        "INSERT INTO customers (email, name, country) VALUES (?, ?, ?)",
        [
            ("alice@example.com", "Alice Smith", "USA"),
            ("bob@example.com", "Bob Johnson", "Canada"),
            ("charlie@example.com", "Charlie Brown", "UK"),
            ("diana@example.com", "Diana Prince", "Australia"),
            ("eve@example.com", "Eve Wilson", "Germany"),
        ]
    )
    
    # Products
    cursor.executemany(
        "INSERT INTO products (product_name, category_id, price, stock_quantity) VALUES (?, ?, ?, ?)",
        [
            ("Laptop Pro", 1, 999.99, 50),
            ("Wireless Mouse", 1, 29.99, 200),
            ("USB-C Cable", 1, 12.99, 500),
            ("T-Shirt Basic", 2, 19.99, 300),
            ("Denim Jeans", 2, 49.99, 150),
            ("Python Programming", 3, 39.99, 100),
            ("SQL Mastery", 3, 44.99, 80),
            ("Garden Hose", 4, 24.99, 75),
            ("LED Lights", 4, 34.99, 120),
        ]
    )
    
    # Orders
    cursor.executemany(
        "INSERT INTO orders (customer_id, status, total_amount) VALUES (?, ?, ?)",
        [
            (1, "completed", 1029.98),
            (2, "completed", 69.98),
            (3, "pending", 49.99),
            (1, "shipped", 39.99),
            (4, "completed", 64.98),
        ]
    )
    
    # Order items
    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        [
            (1, 1, 1, 999.99),
            (1, 2, 1, 29.99),
            (2, 2, 1, 29.99),
            (2, 3, 3, 12.99),
            (3, 5, 1, 49.99),
            (4, 6, 1, 39.99),
            (5, 2, 2, 29.99),
            (5, 8, 1, 24.99),
        ]
    )
    
    conn.commit()
    conn.close()


def get_schema_info() -> Dict[str, Any]:
    """Get database schema information."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    schema = {}
    tables = ["customers", "categories", "products", "orders", "order_items"]
    
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        schema[table] = {
            "columns": [
                {"name": col[1], "type": col[2], "nullable": not col[3], "pk": col[5]}
                for col in columns
            ]
        }
    
    conn.close()
    return schema


def execute_read_only_query(query: str) -> tuple[List[Dict[str, Any]], Optional[str]]:
    """Execute a SELECT query safely. Returns (results, error)."""
    query = query.strip()
    
    # Validate it's a SELECT query
    if not query.upper().startswith("SELECT"):
        return [], "Only SELECT queries are allowed"
    
    # Block dangerous keywords
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE", "TRUNCATE"]
    for keyword in dangerous:
        if keyword in query.upper():
            return [], f"Query contains forbidden keyword: {keyword}"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Fetch results
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        return results, None
    except sqlite3.Error as e:
        return [], f"SQL Error: {str(e)}"


def get_task_description(task_id: str) -> str:
    """Get task description for a given task ID."""
    tasks = {
        "task_1": "Count the total number of customers in the database",
        "task_2": "Find all products with price above 50",
        "task_3": "Get total revenue from completed orders",
        "task_4": "List top 3 customers by order count",
    }
    return tasks.get(task_id, "SQL query task")


# Initialize database on module load
init_database()


@app.get("/", response_model=RootResponse)
async def root():
    """Root endpoint - simple JSON response."""
    return RootResponse()


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse()


@app.get("/state", response_model=StateResponse)
async def state():
    """Get current environment state."""
    return StateResponse(**env_state.get_state())


@app.post("/reset", response_model=Observation)
async def reset(request: ResetRequest):
    """Reset the environment for a new task."""
    env_state.reset(request.task_id)
    
    schema_info = get_schema_info()
    task_description = get_task_description(request.task_id)
    
    return Observation(
        task_id=request.task_id,
        task_description=task_description,
        schema_info=schema_info,
        query_result=[],
        error=None,
        reward=0.0,
        done=False,
        feedback=None,
        step_count=0,
    )


@app.post("/step", response_model=Observation)
async def step(request: StepRequest):
    """Execute a SQL query step."""
    env_state.increment_step()
    
    schema_info = get_schema_info()
    task_description = get_task_description(request.task_id)
    
    # Execute query
    results, error = execute_read_only_query(request.query)
    
    # Calculate reward based on results
    reward = 0.0
    feedback = None
    done = False
    
    if error:
        reward = -0.1
        feedback = error
    elif results:
        reward = 1.0
        feedback = f"Query executed successfully. {len(results)} row(s) returned."
        done = True
    else:
        reward = 0.5
        feedback = "Query executed successfully. No rows returned."
        done = True
    
    return Observation(
        task_id=request.task_id,
        task_description=task_description,
        schema_info=schema_info,
        query_result=results,
        error=error,
        reward=reward,
        done=done,
        feedback=feedback,
        step_count=env_state.step_count,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
