import numpy as np
import pandas as pd
import pytest
from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays
from app.quant.kupiec_backtest import kupiec_pof_test, run_rolling_kupiec_backtest

confidence_strategy = st.floats(min_value=0.5, max_value=0.999)

@st.composite
def backtest_inputs_strategy(draw):
    length = draw(st.integers(min_value=20, max_value=300))
    returns = draw(arrays(dtype=np.float64, shape=(length,), elements=st.floats(min_value=-0.1, max_value=0.1)))
    var_series = draw(arrays(dtype=np.float64, shape=(length,), elements=st.floats(min_value=0.005, max_value=0.08)))
    return returns, var_series

@given(backtest_inputs_strategy(), confidence_strategy)
def test_kupiec_output_invariants(inputs, confidence):
    returns, var_series = inputs
    result = kupiec_pof_test(returns, var_series, confidence)
    
    # Statistical bounds invariants
    assert 0.0 <= result["p_value"] <= 1.0
    assert result["LR_statistic"] >= 0.0
    assert result["n_obs"] == len(returns)
    assert 0 <= result["n_exceptions"] <= len(returns)

def test_kupiec_perfect_fit():
    """Verify that a perfect model fit yields a p-value close to 1."""
    returns = np.zeros(100)
    var_series = np.full(100, 0.02)
    
    # Exactly 10% exceptions for 90% confidence model
    returns[:10] = -0.05
    returns[10:] = 0.01
    
    result = kupiec_pof_test(returns, var_series, confidence_level=0.90)
    assert np.isclose(result["LR_statistic"], 0.0, atol=1e-4)
    assert np.isclose(result["p_value"], 1.0, atol=1e-4)
    assert not result["reject_model"]

def test_run_rolling_kupiec_backtest_z_score():
    """Verify that rolling Kupiec uses correct standard normal z-score (~1.64485 for 95%)."""
    np.random.seed(42)
    series = pd.Series(np.random.normal(0.0005, 0.015, size=400))
    
    res = run_rolling_kupiec_backtest(series, window_size=250, confidence_level=0.95)
    
    assert res["z_score_used"] == 1.6449
    assert "historical_var_backtest" in res
    assert "parametric_var_backtest" in res
    assert res["historical_var_backtest"]["n_obs"] == 150
