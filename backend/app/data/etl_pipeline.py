"""
ETL Data Pipeline: Data Cleaning, Normalization & Feature Extraction
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple

def generate_mock_market_prices(
    tickers: List[str] = ["AAPL", "MSFT", "NVDA", "GOOGL"],
    num_days: int = 500,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates reproducible multi-asset price time series simulating market regimes
    (including volatility clustering and fat-tailed shocks).
    """
    np.random.seed(seed)
    dates = pd.date_range(end=pd.Timestamp.today(), periods=num_days, freq="B")
    
    initial_prices = {"AAPL": 150.0, "MSFT": 310.0, "NVDA": 450.0, "GOOGL": 135.0}
    annual_vols = {"AAPL": 0.25, "MSFT": 0.22, "NVDA": 0.40, "GOOGL": 0.24}
    
    price_dict = {}
    for t in tickers:
        p0 = initial_prices.get(t, 100.0)
        vol = annual_vols.get(t, 0.25) / np.sqrt(252) # Daily volatility
        
        # Student-t distribution shocks to create real fat tails (Kurtosis > 3)
        shocks = np.random.standard_t(df=4, size=num_days) * vol * 0.7
        # Add small drift
        log_rets = 0.0003 + shocks
        price_path = p0 * np.exp(np.cumsum(log_rets))
        price_dict[t] = price_path
        
    return pd.DataFrame(price_dict, index=dates)

def execute_quant_etl_pipeline(
    tickers: List[str],
    weights: List[float],
    lookback_days: int = 250
) -> Dict[str, Any]:
    """
    Full ETL Workflow:
    1. Extract: Ingest multi-asset raw prices
    2. Transform: Compute Log-Returns, Correlation & Covariance Matrices, Kurtosis & Skewness
    3. Load: Structured JSON ready for VaR calculations & API responses
    """
    prices_df = generate_mock_market_prices(tickers, num_days=lookback_days + 50)
    prices_df = prices_df.iloc[-lookback_days:]
    
    log_returns = np.log(prices_df / prices_df.shift(1)).dropna()
    
    corr_matrix = log_returns.corr().to_dict()
    cov_matrix = log_returns.cov().to_dict()
    
    stats_by_ticker = {}
    for t in tickers:
        s = log_returns[t]
        stats_by_ticker[t] = {
            "mean": round(float(s.mean()), 6),
            "std": round(float(s.std()), 6),
            "skewness": round(float(s.skew()), 4),
            "kurtosis": round(float(s.kurtosis()), 4),
            "min_return": round(float(s.min()), 6),
            "max_return": round(float(s.max()), 6)
        }
        
    return {
        "status": "ETL_COMPLETED",
        "lookback_days": lookback_days,
        "tickers": tickers,
        "weights": weights,
        "statistics_by_asset": stats_by_ticker,
        "correlation_matrix": corr_matrix,
        "covariance_matrix": cov_matrix,
        "prices_df": prices_df
    }
