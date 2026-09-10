"""
Portfolio Risk Engine: Historical & Parametric Value at Risk (VaR)
Based on published quantitative finance research:
"Calculating Portfolio Risk: Historical vs. Parametric Value at Risk (VaR) in Python"
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Dict, Any, Tuple, List

def calculate_log_returns(prices_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily log returns of asset prices."""
    if prices_df.empty:
        return pd.DataFrame()
    return np.log(prices_df / prices_df.shift(1)).dropna()

def calculate_portfolio_returns(returns_df: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """Calculate weighted portfolio daily returns."""
    if returns_df.empty or len(weights) == 0:
        return pd.Series(dtype=np.float64)
    # Normalize weights so they sum to 1
    weights_norm = weights / np.sum(weights)
    return (returns_df * weights_norm).sum(axis=1)

def calculate_historical_var(portfolio_returns: pd.Series, confidence_level: float = 0.95, time_horizon_days: int = 1) -> float:
    """
    Calculate Historical VaR (as a positive loss fraction).
    VaR_Hist(c, N-day) = -Percentile_{1-c}(R_p) * sqrt(N)
    """
    if len(portfolio_returns) == 0:
        raise ValueError("Portfolio returns series cannot be empty")
    if not (0.0 < confidence_level < 1.0):
        raise ValueError("Confidence level must be between 0 and 1")
    
    historical_percentile = np.percentile(portfolio_returns, (1 - confidence_level) * 100)
    var_1day = float(-historical_percentile)
    return var_1day * np.sqrt(time_horizon_days)

def calculate_parametric_var(portfolio_returns: pd.Series, confidence_level: float = 0.95, time_horizon_days: int = 1) -> Tuple[float, float, float]:
    """
    Calculate Parametric (Variance-Covariance) VaR using sample mean mu and std sigma.
    VaR_Param(c, N-day) = -(mu + z_{1-c} * sigma) * sqrt(N)
    Returns (parametric_var_pct, mu, sigma).
    """
    if len(portfolio_returns) == 0:
        raise ValueError("Portfolio returns series cannot be empty")
    if not (0.0 < confidence_level < 1.0):
        raise ValueError("Confidence level must be between 0 and 1")
    
    mu = float(np.mean(portfolio_returns))
    sigma = float(np.std(portfolio_returns))
    z_score = float(norm.ppf(1 - confidence_level))
    
    var_1day = float(-(mu + z_score * sigma))
    parametric_var_pct = var_1day * np.sqrt(time_horizon_days)
    return parametric_var_pct, mu, sigma

def analyze_portfolio_risk(
    prices_df: pd.DataFrame,
    weights: np.ndarray,
    portfolio_value: float = 100000.0,
    confidence_level: float = 0.95,
    time_horizon_days: int = 1,
    data_source_description: str = "Seeded Student-t Fat-Tails Simulated Return Series (250 Days) with Live Scraping Capability"
) -> Dict[str, Any]:
    """
    Full quantitative portfolio risk calculation comparing Historical & Parametric VaR.
    Includes time horizon scaling (sqrt(N)), statistical histogram data, and data provenance.
    """
    returns_df = calculate_log_returns(prices_df)
    port_returns = calculate_portfolio_returns(returns_df, weights)
    
    hist_var_pct = calculate_historical_var(port_returns, confidence_level, time_horizon_days)
    param_var_pct, mu, sigma = calculate_parametric_var(port_returns, confidence_level, time_horizon_days)
    
    # Statistical higher moments
    skewness = float(port_returns.skew())
    kurtosis = float(port_returns.kurtosis()) # Excess kurtosis (>0 indicates fat tails)
    
    # Covariance Matrix
    cov_matrix = returns_df.cov().to_dict()
    
    # Generate 25-bin empirical return distribution histogram for visualization
    counts, bin_edges = np.histogram(port_returns, bins=25)
    histogram_bins = []
    z_score = float(norm.ppf(1 - confidence_level))
    
    for i in range(len(counts)):
        mid_val = float((bin_edges[i] + bin_edges[i+1]) / 2.0)
        # Fitted normal PDF value
        pdf_val = float(norm.pdf(mid_val, loc=mu, scale=sigma)) * len(port_returns) * (bin_edges[1] - bin_edges[0])
        histogram_bins.append({
            "bin_min": round(float(bin_edges[i]), 4),
            "bin_max": round(float(bin_edges[i+1]), 4),
            "bin_center": round(mid_val, 4),
            "count": int(counts[i]),
            "normal_pdf": round(pdf_val, 2)
        })
        
    hist_cutoff = float(np.percentile(port_returns, (1 - confidence_level) * 100))
    param_cutoff = float(mu + z_score * sigma)

    return {
        "portfolio_value": portfolio_value,
        "confidence_level": confidence_level,
        "time_horizon_days": time_horizon_days,
        "horizon_label": f"{time_horizon_days}-Day Holding Horizon" if time_horizon_days > 1 else "1-Day Holding Horizon",
        "mean_daily_return": round(mu, 6),
        "daily_volatility": round(sigma, 6),
        "skewness": round(skewness, 4),
        "excess_kurtosis": round(kurtosis, 4),
        "has_fat_tails": kurtosis > 0.5,
        "data_provenance": {
            "origin": data_source_description,
            "observations_count": len(port_returns),
            "lookback_window": f"{len(port_returns)} Business Trading Days"
        },
        "methodology_formulas": {
            "historical_var_formula": f"VaR_Hist = -Percentile_{int((1-confidence_level)*100)}%(R_p) × √{time_horizon_days}",
            "parametric_var_formula": f"VaR_Param = -[μ + ({z_score:.4f}) × σ] × Portfolio Value × √{time_horizon_days}",
            "z_score_used": round(z_score, 4)
        },
        "historical_var": {
            "percentage": round(hist_var_pct, 6),
            "dollar_loss": round(hist_var_pct * portfolio_value, 2),
            "cutoff_return": round(hist_cutoff, 4)
        },
        "parametric_var": {
            "percentage": round(param_var_pct, 6),
            "dollar_loss": round(param_var_pct * portfolio_value, 2),
            "cutoff_return": round(param_cutoff, 4)
        },
        "divergence_pct": round(abs(hist_var_pct - param_var_pct) / param_var_pct * 100, 2),
        "covariance_matrix": cov_matrix,
        "returns_distribution": port_returns.tolist()[-100:],
        "histogram": histogram_bins
    }
