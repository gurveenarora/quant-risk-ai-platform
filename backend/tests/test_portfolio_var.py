import numpy as np
import pandas as pd
import pytest
from hypothesis import given, strategies as st
from hypothesis.extra.numpy import arrays

from app.quant.portfolio_var import (
    calculate_log_returns,
    calculate_portfolio_returns,
    calculate_historical_var,
    calculate_parametric_var
)

@st.composite
def prices_df_strategy(draw):
    num_rows = draw(st.integers(min_value=10, max_value=50))
    num_cols = draw(st.integers(min_value=2, max_value=4))
    price_matrix = draw(arrays(
        dtype=np.float64,
        shape=(num_rows, num_cols),
        elements=st.floats(min_value=1.0, max_value=1000.0, allow_nan=False, allow_infinity=False)
    ))
    return pd.DataFrame(price_matrix, columns=[f"Asset_{i}" for i in range(num_cols)])

returns_series_strategy = arrays(
    dtype=np.float64,
    shape=st.integers(min_value=15, max_value=100),
    elements=st.floats(min_value=-0.5, max_value=0.5, allow_nan=False, allow_infinity=False)
)

confidence_strategy = st.floats(min_value=0.01, max_value=0.999)

@given(prices_df_strategy())
def test_calculate_log_returns_properties(df):
    returns = calculate_log_returns(df)
    assert len(returns) == len(df) - 1
    assert not returns.isna().any().any()

@given(returns_series_strategy, confidence_strategy)
def test_historical_var_invariants(returns_arr, confidence):
    series = pd.Series(returns_arr)
    var_pct = calculate_historical_var(series, confidence)
    
    # 1. Monotonicity Invariant: Higher confidence -> higher or equal VaR
    higher_confidence = confidence + (1.0 - confidence) / 2.0
    var_pct_higher = calculate_historical_var(series, higher_confidence)
    assert var_pct_higher >= var_pct - 1e-9
    
    # 2. Empirical boundaries: VaR must lie within returns range
    assert -series.max() - 1e-6 <= var_pct <= -series.min() + 1e-6

@given(returns_series_strategy, confidence_strategy)
def test_parametric_var_invariants(returns_arr, confidence):
    series = pd.Series(returns_arr)
    var_pct, mu, sigma = calculate_parametric_var(series, confidence)
    
    # Non-negative volatility invariant
    assert sigma >= 0.0
    
    # Monotonicity
    higher_confidence = confidence + (1.0 - confidence) / 2.0
    var_pct_higher, _, _ = calculate_parametric_var(series, higher_confidence)
    assert var_pct_higher >= var_pct - 1e-9
