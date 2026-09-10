"""
Multi-Agent Agentic AI Engine with Tool Calling & Multi-Step Workflows
"""

import json
import asyncio
from typing import Dict, Any, List

from app.quant.portfolio_var import analyze_portfolio_risk, calculate_portfolio_returns
from app.quant.kupiec_backtest import run_rolling_kupiec_backtest
from app.quant.property_runner import run_hypothesis_suite
from app.data.market_scraper import scraper_instance
from app.data.etl_pipeline import generate_mock_market_prices
from app.ai.rag_engine import rag_engine_instance
from app.ai.security_guardrails import guardrails_instance

class AgenticQuantWorkflow:
    def __init__(self):
        self.agent_name = "QuantRisk Agentic Copilot"
        
    async def process_user_query(self, user_prompt: str, user_role: str = "QuantAnalyst") -> Dict[str, Any]:
        """
        Multi-step Agentic AI loop:
        Step 1: Security Guardrail Check (Prompt Injection Defense)
        Step 2: Intent Classification & Tool Selection
        Step 3: Tool Execution (VaR calculation, Kupiec backtest, PBT suite, Scraping, RAG)
        Step 4: Synthesis & Output Generation
        """
        # Step 1: Security Inspection
        sec_check = guardrails_instance.inspect_prompt(user_prompt)
        if sec_check["is_malicious"]:
            return {
                "agent_name": self.agent_name,
                "status": "SECURITY_BLOCK",
                "security_alert": sec_check,
                "response": "⚠️ Security Alert: Prompt injection or unauthorized payload detected and blocked by AI Security Guardrails."
            }
            
        prompt_lower = user_prompt.lower()
        tool_calls_executed = []
        context_data = {}
        
        # Step 2 & 3: Multi-Step Tool Decision Engine
        if "backtest" in prompt_lower or "kupiec" in prompt_lower:
            tool_calls_executed.append("Tool: run_rolling_kupiec_backtest")
            prices_df = generate_mock_market_prices(num_days=400)
            port_returns = calculate_portfolio_returns(np.log(prices_df / prices_df.shift(1)).dropna(), np.array([0.25, 0.25, 0.25, 0.25]))
            backtest_res = run_rolling_kupiec_backtest(port_returns, window_size=250, confidence_level=0.95)
            context_data["backtest_results"] = backtest_res
            
        if "var" in prompt_lower or "risk" in prompt_lower or "loss" in prompt_lower:
            tool_calls_executed.append("Tool: analyze_portfolio_risk")
            prices_df = generate_mock_market_prices(num_days=300)
            weights = np.array([0.25, 0.25, 0.25, 0.25])
            var_res = analyze_portfolio_risk(prices_df, weights, portfolio_value=100000, confidence_level=0.95)
            context_data["var_analysis"] = var_res
            
        if "property" in prompt_lower or "hypothesis" in prompt_lower or "pbt" in prompt_lower or "test" in prompt_lower:
            tool_calls_executed.append("Tool: run_hypothesis_suite")
            pbt_res = run_hypothesis_suite(num_samples=30)
            context_data["pbt_results"] = pbt_res

        if "scrape" in prompt_lower or "live" in prompt_lower or "market" in prompt_lower or "aapl" in prompt_lower:
            tool_calls_executed.append("Tool: scrape_ticker_financials")
            scrape_res = await scraper_instance.scrape_ticker_financials_httpx("AAPL")
            context_data["live_market_scrape"] = scrape_res

        # Always retrieve RAG Knowledge
        tool_calls_executed.append("Tool: vector_rag_search")
        rag_docs = rag_engine_instance.search(user_prompt, top_k=2)
        context_data["rag_sources"] = rag_docs

        # Step 4: Synthesize structured natural language response
        if not tool_calls_executed:
            tool_calls_executed.append("Tool: vector_rag_search")
            
        response_text = f"Analyzed query: '{user_prompt}'.\n"
        if "var_analysis" in context_data:
            v = context_data["var_analysis"]
            response_text += f"\n📊 **Portfolio VaR (95% 1-Day)**: Historical VaR is **${v['historical_var']['dollar_loss']:,.2f}** ({v['historical_var']['percentage']:.2%}) while Parametric VaR is **${v['parametric_var']['dollar_loss']:,.2f}** ({v['parametric_var']['percentage']:.2%}). "
            if v["has_fat_tails"]:
                response_text += f"The portfolio exhibits **excess kurtosis ({v['excess_kurtosis']:.2f})**, confirming fat-tail risk."
                
        if "backtest_results" in context_data:
            b = context_data["backtest_results"]
            response_text += f"\n\n🧪 **Kupiec POF Backtest**: Historical VaR Status: `{b['historical_var_backtest']['status']}` (p-value: {b['historical_var_backtest']['p_value']}). Parametric VaR Status: `{b['parametric_var_backtest']['status']}` (p-value: {b['parametric_var_backtest']['p_value']})."
            
        if "pbt_results" in context_data:
            p = context_data["pbt_results"]
            response_text += f"\n\n🔬 **Hypothesis PBT Suite**: Tested {p['total_scenarios_tested']} randomized scenarios with a **{p['pass_rate_pct']}% pass rate** in {p['elapsed_seconds']}s."

        return {
            "agent_name": self.agent_name,
            "status": "COMPLETED",
            "user_role": user_role,
            "tool_calls_executed": tool_calls_executed,
            "context_data": context_data,
            "rag_references": rag_docs,
            "response": response_text
        }

agent_workflow_instance = AgenticQuantWorkflow()
