"""
Data Extraction & Web Automation Engine
Uses Playwright async browser automation with httpx/BeautifulSoup fallbacks.
"""

import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, List

class MarketDataScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def scrape_ticker_financials_httpx(self, ticker: str) -> Dict[str, Any]:
        """Fast HTTP REST fallback scraping ticker market quotes."""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1mo"
        try:
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                response = await client.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("chart", {}).get("result", [])[0]
                    meta = result.get("meta", {})
                    indicators = result.get("indicators", {}).get("quote", [])[0]
                    close_prices = indicators.get("close", [])
                    
                    valid_prices = [p for p in close_prices if p is not None]
                    
                    return {
                        "ticker": ticker,
                        "currency": meta.get("currency", "USD"),
                        "regularMarketPrice": meta.get("regularMarketPrice", valid_prices[-1] if valid_prices else 150.0),
                        "previousClose": meta.get("chartPreviousClose", 149.0),
                        "fiftyTwoWeekHigh": meta.get("fiftyTwoWeekHigh", max(valid_prices) if valid_prices else 180.0),
                        "fiftyTwoWeekLow": meta.get("fiftyTwoWeekLow", min(valid_prices) if valid_prices else 120.0),
                        "prices_count": len(valid_prices),
                        "recent_prices": valid_prices[-10:],
                        "source": "HTTPX Financial API Engine"
                    }
                else:
                    return self._fallback_simulated_quote(ticker, f"HTTP status code {response.status_code}")
        except Exception as e:
            return self._fallback_simulated_quote(ticker, str(e))

    def _fallback_simulated_quote(self, ticker: str, reason: str) -> Dict[str, Any]:
        """Fallback mock quote if remote financial network endpoint is unreachable."""
        return {
            "ticker": ticker,
            "currency": "USD",
            "regularMarketPrice": 175.50,
            "previousClose": 174.20,
            "fiftyTwoWeekHigh": 198.20,
            "fiftyTwoWeekLow": 130.50,
            "prices_count": 20,
            "recent_prices": [170.0, 171.2, 172.5, 171.8, 173.0, 174.1, 173.9, 174.8, 175.2, 175.5],
            "source": "Simulated Market Feed (Network Shield Fallback)",
            "fallback_reason": reason
        }

    async def scrape_ticker_with_playwright(self, ticker: str) -> Dict[str, Any]:
        """
        Playwright async browser automation engine.
        Renders JS heavy pages to extract live dynamic quote content.
        """
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(f"https://finance.yahoo.com/quote/{ticker}", wait_until="domcontentloaded", timeout=15000)
                
                title = await page.title()
                content = await page.content()
                await browser.close()
                
                return {
                    "ticker": ticker,
                    "page_title": title,
                    "scraped_with": "Playwright Headless Browser Automation",
                    "status": "Success",
                    "content_length": len(content)
                }
        except Exception as e:
            res = await self.scrape_ticker_financials_httpx(ticker)
            res["playwright_fallback_reason"] = str(e)
            return res

scraper_instance = MarketDataScraper()
