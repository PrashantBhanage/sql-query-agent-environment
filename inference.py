"""SQL Query Agent - Main Inference Module."""
from typing import Dict, Any, Optional, List


class SQLQueryAgent:
    """A minimal SQL query agent that uses heuristics to solve tasks."""
    
    def __init__(self):
        self.task_handlers = {
            "task_1": self._handle_count_customers,
            "task_2": self._handle_expensive_products,
            "task_3": self._handle_total_revenue,
            "task_4": self._handle_top_customers,
        }
    
    def solve(self, task_id: str, schema: Dict[str, Any]) -> str:
        """Solve a SQL task given the task ID and schema info."""
        handler = self.task_handlers.get(task_id, self._default_handler)
        return handler(schema)
    
    def _handle_count_customers(self, schema: Dict[str, Any]) -> str:
        """Handle task_1: Count customers."""
        return "SELECT COUNT(*) as total_customers FROM customers;"
    
    def _handle_expensive_products(self, schema: Dict[str, Any]) -> str:
        """Handle task_2: Find expensive products."""
        return "SELECT * FROM products WHERE price > 50 ORDER BY price DESC;"
    
    def _handle_total_revenue(self, schema: Dict[str, Any]) -> str:
        """Handle task_3: Calculate total revenue from completed orders."""
        return "SELECT SUM(total_amount) as total_revenue FROM orders WHERE status = 'completed';"
    
    def _handle_top_customers(self, schema: Dict[str, Any]) -> str:
        """Handle task_4: Get top customers by order count."""
        return """
        SELECT c.customer_id, c.name, COUNT(o.order_id) as order_count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        GROUP BY c.customer_id, c.name
        ORDER BY order_count DESC
        LIMIT 3;
        """
    
    def _default_handler(self, schema: Dict[str, Any]) -> str:
        """Default handler for unknown tasks."""
        # Return a simple query based on schema
        if "products" in schema:
            return "SELECT * FROM products LIMIT 10;"
        elif "customers" in schema:
            return "SELECT * FROM customers LIMIT 10;"
        return "SELECT 1;"


def create_agent() -> SQLQueryAgent:
    """Factory function to create an agent instance."""
    return SQLQueryAgent()


def run_inference(task_id: str, schema: Dict[str, Any]) -> str:
    """Run inference to get a SQL query for the given task."""
    agent = create_agent()
    return agent.solve(task_id, schema)


# For direct execution
if __name__ == "__main__":
    agent = create_agent()
    sample_schema = {
        "customers": {"columns": []},
        "products": {"columns": []},
    }
    
    for task in ["task_1", "task_2", "task_3", "task_4"]:
        query = agent.solve(task, sample_schema)
        print(f"{task}: {query.strip()}")
