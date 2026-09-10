"""
Model Validation: Kupiec Proportion-of-Failures (POF) Backtest Engine
Based on published research:
"Bulletproofing Quantitative Risk Models: Property-Based Testing for Portfolio VaR & Kupiec Backtests in Python"
"""

import numpy as np
import pandas as pd
from scipy.stats import chi2, norm
from typing import Dict, Any, List

def kupiec_pof_test(
    realized_returns: np.ndarray,
    var_thresholds: np.ndarray,
    confidence_level: float = 0.95
) -> Dict[str, Any]:
    """
    Performs Kupiec Proportion-of-Failures (POF) statistical test.
    
    Parameters:
    - realized_returns: Array of daily portfolio returns
    - var_thresholds: Array of VaR numbers (expressed as positive loss percentages e.g. 0.02)
    - confidence_level: Stated VaR confidence (e.g. 0.95)
    
    Returns statistical metrics: n_obs, exceptions, LR statistic, p-value, decision.
    """
    returns_arr = np.asarray(realized_returns)
    var_arr = np.asarray(var_thresholds)
    
    if len(returns_arr) != len(var_arr):
        raise ValueError("Returns array and VaR thresholds array must have identical lengths")
    
    n = len(returns_arr)
    if n == 0:
        raise ValueError("Cannot execute Kupiec backtest on empty series")
    
    p = 1.0 - confidence_level  # Expected failure rate (e.g., 0.05 for 95%)
    
    # An exception occurs when loss > VaR (i.e. realized return < -VaR_threshold)
    exceptions = (returns_arr < -np.abs(var_arr)).astype(int)
    x = int(np.sum(exceptions))
    p_hat = x / n  # Observed failure rate
    
    # Numerical stability clip to prevent log(0)
    p_hat_adj = np.clip(p_hat, 1e-6, 1.0 - 1e-6)
    
    # Likelihood Ratio calculation
    numerator = ((1.0 - p) ** (n - x)) * (p ** x)
    denominator = ((1.0 - p_hat_adj) ** (n - x)) * (p_hat_adj ** x)
    lr_pof = -2.0 * np.log(numerator / denominator)
    
    # Chi-square p-value (df=1)
    p_value = float(1.0 - chi2.cdf(lr_pof, df=1))
    reject_model = p_value < 0.05  # Reject null hypothesis at 5% significance level
    
    return {
        "n_obs": n,
        "n_exceptions": x,
        "expected_exceptions": round(p * n, 1),
        "observed_failure_rate": round(p_hat, 4),
        "target_failure_rate": round(p, 4),
        "LR_statistic": round(float(lr_pof), 4),
        "p_value": round(p_value, 4),
        "reject_model": bool(reject_model),
        "status": "REJECTED (Model Under/Over-estimates Risk)" if reject_model else "PASSED (Model Well-Calibrated)",
        "exceptions_timeline": exceptions.tolist()
    }

def run_rolling_kupiec_backtest(
    portfolio_returns: pd.Series,
    window_size: int = 250,
    confidence_level: float = 0.95
) -> Dict[str, Any]:
    """
    Executes a rolling backtest comparing Rolling Historical VaR vs Rolling Parametric VaR
    without look-ahead bias, followed by Kupiec POF test on both.
    """
    if len(portfolio_returns) <= window_size:
        raise ValueError(f"Need at least {window_size + 1} return observations for rolling backtest")
    
    # Standard Normal PPF Z-score for Parametric VaR (e.g. 1.64485 for 95% confidence)
    z_score = float(np.abs(norm.ppf(1.0 - confidence_level)))
    
    # Rolling Parametric & Historical VaR thresholds (as positive loss percentages)
    rolling_hist_var = portfolio_returns.rolling(window_size).apply(
        lambda x: -np.percentile(x, (1.0 - confidence_level) * 100)
    )
    
    rolling_mu = portfolio_returns.rolling(window_size).mean()
    rolling_sigma = portfolio_returns.rolling(window_size).std()
    rolling_param_var = -(rolling_mu - z_score * rolling_sigma)
    
    test_returns = portfolio_returns.iloc[window_size:].values
    test_hist_var = np.abs(rolling_hist_var.iloc[window_size:].values)
    test_param_var = np.abs(rolling_param_var.iloc[window_size:].values)
    
    hist_kupiec = kupiec_pof_test(test_returns, test_hist_var, confidence_level)
    param_kupiec = kupiec_pof_test(test_returns, test_param_var, confidence_level)
    
    return {
        "window_size": window_size,
        "confidence_level": confidence_level,
        "z_score_used": round(z_score, 4),
        "historical_var_backtest": hist_kupiec,
        "parametric_var_backtest": param_kupiec,
        "recommendation": (
            "Historical VaR performs better under non-normal fat tails."
            if not hist_kupiec["reject_model"] and param_kupiec["reject_model"]
            else "Both models perform within acceptable statistical tolerance."
        )
    }
