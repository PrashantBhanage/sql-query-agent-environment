"""Baseline SQL Query Agent - Simple Heuristic-based Solution."""
from typing import Dict, Any


class BaselineAgent:
    """Simple baseline agent that uses predefined queries."""
    
    def __init__(self):
        self.queries = {
            "task_1": "SELECT COUNT(*) as total_customers FROM customers;",
            "task_2": "SELECT * FROM products WHERE price > 50;",
            "task_3": "SELECT SUM(total_amount) as total_revenue FROM orders WHERE status = 'completed';",
            "task_4": "SELECT c.customer_id, c.name, COUNT(*) as order_count FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id, c.name ORDER BY order_count DESC LIMIT 3;",
        }
    
    def get_query(self, task_id: str) -> str:
        """Get the predefined query for a task."""
        return self.queries.get(task_id, "SELECT 1;")
    
    def solve(self, task_id: str) -> str:
        """Return the query for the given task."""
        return self.get_query(task_id)


def create_baseline_agent() -> BaselineAgent:
    """Create a baseline agent instance."""
    return BaselineAgent()


def run_baseline(task_id: str) -> str:
    """Run baseline inference for a task."""
    agent = create_baseline_agent()
    return agent.solve(task_id)


# For direct execution
if __name__ == "__main__":
    agent = create_baseline_agent()
    for task in ["task_1", "task_2", "task_3", "task_4"]:
        print(f"{task}: {agent.get_query(task)}")
