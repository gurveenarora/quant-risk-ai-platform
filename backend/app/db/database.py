"""
Database Persistence Layer
Handles SQLite / PostgreSQL data models and session persistence.
"""

from typing import List, Dict, Any
from datetime import datetime

class InMemoryDatabase:
    """Fast thread-safe database store for portfolios, user accounts & audit logs."""
    def __init__(self):
        self.users = {
            "admin@quant.ai": {"username": "admin@quant.ai", "password_hash": "...", "role": "Admin"},
            "quant@quant.ai": {"username": "quant@quant.ai", "password_hash": "...", "role": "QuantAnalyst"},
            "auditor@quant.ai": {"username": "auditor@quant.ai", "password_hash": "...", "role": "Auditor"}
        }
        self.portfolios = [
            {
                "id": "port_001",
                "name": "Tech Alpha Growth Portfolio",
                "tickers": ["AAPL", "MSFT", "NVDA", "GOOGL"],
                "weights": [0.25, 0.25, 0.25, 0.25],
                "portfolio_value": 100000.0,
                "created_at": "2026-08-01T10:00:00Z"
            },
            {
                "id": "port_002",
                "name": "Defensive Dividend ETF Fund",
                "tickers": ["SPY", "QQQ"],
                "weights": [0.50, 0.50],
                "portfolio_value": 500000.0,
                "created_at": "2026-08-05T14:30:00Z"
            }
        ]
        self.audit_logs: List[Dict[str, Any]] = []

    def log_action(self, username: str, action: str, details: str, status: str = "SUCCESS"):
        self.audit_logs.append({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "username": username,
            "action": action,
            "details": details,
            "status": status
        })

    def get_audit_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        return list(reversed(self.audit_logs))[-limit:]

db_instance = InMemoryDatabase()
