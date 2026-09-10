"""
Vector RAG (Retrieval-Augmented Generation) Engine
Indexed knowledge base over published quantitative research papers:
1. "Calculating Portfolio Risk: Historical vs. Parametric Value at Risk (VaR) in Python"
2. "Bulletproofing Quantitative Risk Models: Property-Based Testing for Portfolio VaR & Kupiec Backtests in Python"
"""

import numpy as np
from typing import List, Dict, Any

KNOWLEDGE_BASE = [
    {
        "id": "doc_1",
        "title": "Historical Value at Risk (Non-Parametric)",
        "content": "Historical VaR does not assume any underlying probability distribution for asset returns. Given portfolio daily returns R_p, Historical VaR at confidence level c (e.g. 95%) is the negative (1-c)-th percentile of empirical returns: VaR_Hist(c) = -Percentile_{1-c}(R_p). It naturally captures fat tails, skewness, and kurtosis.",
        "category": "VaR Theory"
    },
    {
        "id": "doc_2",
        "title": "Parametric Value at Risk (Variance-Covariance)",
        "content": "Parametric VaR assumes returns follow a normal distribution. It calculates VaR analytically using sample mean mu and standard deviation sigma: VaR_Param(c) = -(mu + z_{1-c} * sigma) where z_{1-c} is standard normal PPF. It tends to understate tail risk due to thin tails of normal distribution.",
        "category": "VaR Theory"
    },
    {
        "id": "doc_3",
        "title": "Kupiec Proportion-of-Failures (POF) Backtest",
        "content": "The Kupiec POF backtest evaluates VaR model accuracy using a Likelihood Ratio test: LR_POF = -2 * ln[ ((1-p)^(n-x) * p^x) / ((1-p_hat)^(n-x) * p_hat^x) ]. Under the null hypothesis that the VaR model is correct, LR_POF follows a Chi-Square distribution with 1 degree of freedom (df=1). Rejection occurs if p-value < 0.05.",
        "category": "Model Validation"
    },
    {
        "id": "doc_4",
        "title": "Property-Based Testing with Hypothesis",
        "content": "Property-Based Testing (PBT) using the Hypothesis library tests code against hundreds of randomized valid scenarios to assert universal invariants rather than hand-crafted test cases. Key invariants include monotonicity (higher confidence -> higher VaR), empirical bounds, and non-negative volatility.",
        "category": "Testing & QA"
    },
    {
        "id": "doc_5",
        "title": "Fat Tails and Excess Kurtosis in Quant Finance",
        "content": "Real asset returns exhibit leptokurtosis (Excess Kurtosis > 0), meaning extreme market crashes occur much more frequently than normal bell curve predictions. Parametric VaR understates loss severity during market panics.",
        "category": "Market Microstructure"
    }
]

class QuantVectorRAG:
    def __init__(self):
        self.documents = KNOWLEDGE_BASE

    def _simple_embedding(self, text: str) -> np.ndarray:
        """Lightweight character frequency embedding for fast vector similarity search."""
        arr = np.zeros(128, dtype=np.float32)
        for char in text.lower():
            idx = ord(char) % 128
            arr[idx] += 1.0
        norm = np.linalg.norm(arr)
        return arr / (norm + 1e-9)

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Vector similarity search returning top-k relevant research chunks."""
        q_vec = self._simple_embedding(query)
        scored_docs = []
        for doc in self.documents:
            d_vec = self._simple_embedding(doc["content"] + " " + doc["title"])
            similarity = float(np.dot(q_vec, d_vec))
            scored_docs.append((similarity, doc))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_docs[:top_k]:
            item = dict(doc)
            item["relevance_score"] = round(score, 4)
            results.append(item)
            
        return results

rag_engine_instance = QuantVectorRAG()
