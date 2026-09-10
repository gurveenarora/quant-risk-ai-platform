import React, { useState } from 'react';
import { Globe, Cpu, RefreshCw, CheckCircle, Database } from 'lucide-react';

export const ScraperModule: React.FC = () => {
  const [ticker, setTicker] = useState<string>('AAPL');
  const [usePlaywright, setUsePlaywright] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(false);
  const [scrapeResult, setScrapeResult] = useState<any>(null);

  const runScraper = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/data/scrape', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ticker, use_playwright: usePlaywright })
      });
      const json = await response.json();
      setScrapeResult(json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Globe className="text-blue-400 w-7 h-7" />
            Playwright Automated Market Scraper & ETL Pipeline
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Async headless browser data extraction with BeautifulSoup and HTTP fallbacks.
          </p>
        </div>
        <button
          onClick={runScraper}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white font-medium shadow-lg glow-cyan flex items-center justify-center gap-2 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Scraping Live Data...' : 'Trigger Playwright Scraper'}
        </button>
      </div>

      {/* Control Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-5 rounded-xl">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Target Stock Symbol / Ticker
          </label>
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg px-4 py-2.5 text-white font-mono uppercase focus:outline-none focus:border-blue-500"
          />
        </div>
        <div className="glass-card p-5 rounded-xl flex items-center justify-between">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">
              Automation Engine
            </label>
            <span className="text-sm text-slate-300">
              {usePlaywright ? 'Playwright Headless Browser (Chromium)' : 'HTTPX Fast REST API'}
            </span>
          </div>
          <button
            onClick={() => setUsePlaywright(!usePlaywright)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition ${
              usePlaywright
                ? 'bg-blue-500/20 text-blue-400 border-blue-500/40'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            Toggle Engine
          </button>
        </div>
      </div>

      {/* Scrape Output Card */}
      {scrapeResult && (
        <div className="glass-card p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              Scraped Market Indicators: {scrapeResult.ticker}
            </h3>
            <span className="px-3 py-1 rounded-full bg-blue-500/20 text-blue-400 text-xs font-mono border border-blue-500/30">
              {scrapeResult.source || scrapeResult.scraped_with}
            </span>
          </div>

          <pre className="bg-slate-950 p-4 rounded-xl text-xs font-mono text-cyan-300 overflow-x-auto border border-slate-800">
            {JSON.stringify(scrapeResult, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};
