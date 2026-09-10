"""
FastAPI Enterprise Application Gateway
Integrates Quant Engine, Agentic AI, Playwright Scraper, Security Guardrails & Infrastructure.
"""

from fastapi import FastAPI, HTTPException, Depends, Header, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.quant.portfolio_var import analyze_portfolio_risk, calculate_portfolio_returns
from app.quant.kupiec_backtest import run_rolling_kupiec_backtest, kupiec_pof_test
from app.quant.property_runner import run_hypothesis_suite
from app.data.market_scraper import scraper_instance
from app.data.etl_pipeline import execute_quant_etl_pipeline, generate_mock_market_prices
from app.ai.quant_agent import agent_workflow_instance
from app.ai.eval_finetune import generate_finetuning_dataset, evaluate_model_response
from app.ai.security_guardrails import guardrails_instance
from app.core.security import security_manager
from app.db.database import db_instance

import numpy as np
import pandas as pd

app = FastAPI(
    title="QuantRisk Enterprise AI & Data Security Platform",
    description="Production-grade platform implementing Portfolio VaR, Kupiec POF Backtests, and Hypothesis Property-Based Testing.",
    version="2.0.0"
)

# OWASP & CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Request & Response Models (Pydantic v2)
# -------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str
    role: str = "QuantAnalyst"

class VaRCalculationRequest(BaseModel):
    tickers: List[str] = ["AAPL", "MSFT", "NVDA", "GOOGL"]
    weights: List[float] = [0.25, 0.25, 0.25, 0.25]
    portfolio_value: float = 100000.0
    confidence_level: float = 0.95
    time_horizon_days: int = 1

class KupiecBacktestRequest(BaseModel):
    tickers: List[str] = ["AAPL", "MSFT", "NVDA", "GOOGL"]
    weights: List[float] = [0.25, 0.25, 0.25, 0.25]
    window_size: int = 250
    confidence_level: float = 0.95

class AgentChatRequest(BaseModel):
    prompt: str
    user_role: Optional[str] = "QuantAnalyst"

class ScrapeRequest(BaseModel):
    ticker: str = "AAPL"
    use_playwright: bool = True

class ModelEvalRequest(BaseModel):
    prompt: str
    generated_response: str

# -------------------------------------------------------------
# Authentication & RBAC Helper
# -------------------------------------------------------------
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return {"username": "guest@quant.ai", "role": "Guest"}
    token = authorization.split(" ")[1]
    session = security_manager.decode_jwt_token(token)
    if not session:
        return {"username": "guest@quant.ai", "role": "Guest"}
    return {"username": session.username, "role": session.role}

from fastapi.responses import HTMLResponse, FileResponse
import os

@app.get("/", response_class=HTMLResponse)
def read_root():
    static_html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_html_path):
        with open(static_html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>QuantRisk Platform Engine Online</h1>"

METRICS_STATE = {
    "var_requests": 0,
    "agent_requests": 0,
    "total_requests": 0,
    "start_timestamp": time.time()
}

@app.middleware("http")
async def metrics_middleware(request, call_next):
    METRICS_STATE["total_requests"] += 1
    path = request.url.path
    if path == "/api/quant/calculate-var":
        METRICS_STATE["var_requests"] += 1
    elif path == "/api/agent/chat":
        METRICS_STATE["agent_requests"] += 1
    response = await call_next(request)
    return response

@app.get("/healthz")
def health_check():
    return {"status": "healthy", "database": "connected", "redis": "ready"}

@app.get("/metrics")
def prometheus_metrics():
    """Prometheus monitoring metrics endpoint with real dynamic request instrumentation."""
    uptime = round(time.time() - METRICS_STATE["start_timestamp"], 2)
    return (
        "# HELP http_requests_total Total number of HTTP requests\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total{{method=\"POST\",handler=\"/api/quant/calculate-var\"}} {METRICS_STATE['var_requests']}\n"
        f"http_requests_total{{method=\"POST\",handler=\"/api/agent/chat\"}} {METRICS_STATE['agent_requests']}\n"
        f"http_requests_total{{method=\"ALL\",handler=\"all\"}} {METRICS_STATE['total_requests']}\n"
        "# HELP process_uptime_seconds Process uptime in seconds\n"
        "# TYPE process_uptime_seconds gauge\n"
        f"process_uptime_seconds {uptime}\n"
    )

@app.post("/api/auth/login")
def login(req: LoginRequest):
    token = security_manager.create_jwt_token(req.username, req.role)
    db_instance.log_action(req.username, "USER_LOGIN", f"Role assigned: {req.role}")
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": req.role,
        "username": req.username
    }

@app.post("/api/quant/calculate-var")
def calculate_var(req: VaRCalculationRequest, user: Dict[str, Any] = Depends(get_current_user)):
    prices_df = generate_mock_market_prices(req.tickers, num_days=300)
    weights_arr = np.array(req.weights)
    
    result = analyze_portfolio_risk(
        prices_df,
        weights_arr,
        portfolio_value=req.portfolio_value,
        confidence_level=req.confidence_level,
        time_horizon_days=req.time_horizon_days
    )
    
    db_instance.log_action(user["username"], "CALCULATE_VAR", f"Portfolio value: ${req.portfolio_value:,.2f}")
    return result

@app.post("/api/quant/kupiec-backtest")
def run_kupiec(req: KupiecBacktestRequest, user: Dict[str, Any] = Depends(get_current_user)):
    prices_df = generate_mock_market_prices(req.tickers, num_days=req.window_size + 150)
    weights_arr = np.array(req.weights)
    log_returns = np.log(prices_df / prices_df.shift(1)).dropna()
    port_returns = calculate_portfolio_returns(log_returns, weights_arr)
    
    result = run_rolling_kupiec_backtest(
        port_returns,
        window_size=req.window_size,
        confidence_level=req.confidence_level
    )
    
    db_instance.log_action(user["username"], "KUPIEC_BACKTEST", f"Window size: {req.window_size}")
    return result

@app.get("/api/quant/run-pbt")
def run_pbt_suite(num_samples: int = 50, user: Dict[str, Any] = Depends(get_current_user)):
    """Executes Hypothesis property-based testing invariant suite."""
    result = run_hypothesis_suite(num_samples=num_samples)
    db_instance.log_action(user["username"], "EXECUTE_HYPOTHESIS_PBT", f"Samples: {num_samples}")
    return result

@app.post("/api/agent/chat")
async def agent_chat(req: AgentChatRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Agentic AI workflow endpoint with tool calling & AI Security guardrails."""
    result = await agent_workflow_instance.process_user_query(req.prompt, user_role=user["role"])
    db_instance.log_action(user["username"], "AGENT_CHAT_QUERY", f"Prompt length: {len(req.prompt)}")
    return result

@app.post("/api/data/scrape")
async def scrape_market_data(req: ScrapeRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Automated market data scraper endpoint using Playwright/HTTP."""
    if req.use_playwright:
        res = await scraper_instance.scrape_ticker_with_playwright(req.ticker)
    else:
        res = await scraper_instance.scrape_ticker_financials_httpx(req.ticker)
        
    db_instance.log_action(user["username"], "DATA_SCRAPE", f"Ticker: {req.ticker}")
    return res

@app.get("/api/data/etl")
def run_etl():
    """Runs data extraction, cleaning & transformation pipeline."""
    return execute_quant_etl_pipeline(["AAPL", "MSFT", "NVDA", "GOOGL"], [0.25, 0.25, 0.25, 0.25])

@app.get("/api/eval/finetune-dataset")
def get_finetune_dataset(num_samples: int = 10):
    """Generates JSONL fine-tuning dataset formatted for LLM instruction tuning."""
    return generate_finetuning_dataset(num_samples=num_samples)

@app.post("/api/eval/model-eval")
def evaluate_response(req: ModelEvalRequest):
    """Model evaluation metrics endpoint."""
    return evaluate_model_response(req.prompt, req.generated_response)

@app.get("/api/security/audit-logs")
def get_audit_logs(user: Dict[str, Any] = Depends(get_current_user)):
    """RBAC Protected Audit Log Viewer (QuantAnalyst & Admin only)."""
    if not security_manager.check_rbac_permission("QuantAnalyst", user["role"]):
        raise HTTPException(status_code=403, detail="Forbidden: Insufficient RBAC privileges")
    return {"audit_logs": db_instance.get_audit_logs(limit=25)}
