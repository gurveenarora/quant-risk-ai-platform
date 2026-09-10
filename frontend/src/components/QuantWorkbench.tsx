import React, { useState } from 'react';
import { TrendingDown, ShieldAlert, BarChart3, RefreshCw, Layers } from 'lucide-react';

interface QuantWorkbenchProps {
  onAnalyze?: (data: any) => void;
}

export const QuantWorkbench: React.FC<QuantWorkbenchProps> = () => {
  const [portfolioValue, setPortfolioValue] = useState<number>(100000);
  const [confidenceLevel, setConfidenceLevel] = useState<number>(0.95);
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<any>(null);

  const runCalculation = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/quant/calculate-var', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: ['AAPL', 'MSFT', 'NVDA', 'GOOGL'],
          weights: [0.25, 0.25, 0.25, 0.25],
          portfolio_value: portfolioValue,
          confidence_level: confidenceLevel
        })
      });
      const json = await response.json();
      setData(json);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header Card */}
      <div className="glass-panel p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="text-cyan-400 w-7 h-7" />
            Portfolio Value at Risk (VaR) Engine
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Historical empirical percentile vs. Parametric variance-covariance tail risk modeling.
          </p>
        </div>
        <button
          onClick={runCalculation}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium shadow-lg glow-cyan flex items-center justify-center gap-2 transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Calculating...' : 'Run Risk Analysis'}
        </button>
      </div>

      {/* Input Parameters Control */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-5 rounded-xl">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Portfolio Value ($)
          </label>
          <input
            type="number"
            value={portfolioValue}
            onChange={(e) => setPortfolioValue(Number(e.target.value))}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg px-4 py-2.5 text-white font-mono focus:outline-none focus:border-cyan-500"
          />
        </div>
        <div className="glass-card p-5 rounded-xl">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Confidence Level (c)
          </label>
          <select
            value={confidenceLevel}
            onChange={(e) => setConfidenceLevel(Number(e.target.value))}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg px-4 py-2.5 text-white font-mono focus:outline-none focus:border-cyan-500"
          >
            <option value={0.90}>90% Confidence Level (Working monitoring)</option>
            <option value={0.95}>95% Confidence Level (Standard benchmark)</option>
            <option value={0.99}>99% Confidence Level (Regulatory / Tail risk)</option>
          </select>
        </div>
      </div>

      {/* Analytical Results Grid */}
      {data && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Historical VaR Card */}
            <div className="glass-card p-6 rounded-2xl border-l-4 border-l-cyan-500 glow-cyan">
              <div className="text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1">
                Historical VaR ({data.confidence_level * 100}%)
              </div>
              <div className="text-3xl font-extrabold text-white font-mono">
                ${data.historical_var.dollar_loss.toLocaleString()}
              </div>
              <div className="text-sm text-slate-400 mt-2 font-mono">
                {(data.historical_var.percentage * 100).toFixed(2)}% of portfolio
              </div>
              <p className="text-xs text-slate-500 mt-3">
                Non-parametric percentile method directly capturing historical empirical shocks.
              </p>
            </div>

            {/* Parametric VaR Card */}
            <div className="glass-card p-6 rounded-2xl border-l-4 border-l-amber-500 glow-amber">
              <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">
                Parametric VaR ({data.confidence_level * 100}%)
              </div>
              <div className="text-3xl font-extrabold text-white font-mono">
                ${data.parametric_var.dollar_loss.toLocaleString()}
              </div>
              <div className="text-sm text-slate-400 mt-2 font-mono">
                {(data.parametric_var.percentage * 100).toFixed(2)}% of portfolio
              </div>
              <p className="text-xs text-slate-500 mt-3">
                Variance-covariance method using exact sample mean (μ) and standard deviation (σ).
              </p>
            </div>

            {/* Statistical Moments Card */}
            <div className="glass-card p-6 rounded-2xl border-l-4 border-l-purple-500">
              <div className="text-xs font-semibold text-purple-400 uppercase tracking-wider mb-1">
                Fat-Tail Risk Indicator
              </div>
              <div className="flex items-center justify-between mt-1">
                <div>
                  <div className="text-2xl font-bold text-white font-mono">
                    {data.excess_kurtosis}
                  </div>
                  <div className="text-xs text-slate-400">Excess Kurtosis</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-white font-mono">
                    {data.skewness}
                  </div>
                  <div className="text-xs text-slate-400">Skewness</div>
                </div>
              </div>
              <div className="mt-4 px-3 py-1.5 rounded-lg bg-purple-950/50 border border-purple-800/40 text-xs text-purple-300 flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-purple-400 shrink-0" />
                {data.has_fat_tails
                  ? 'Leptokurtic distribution detected (Excess Kurtosis > 0.5).'
                  : 'Normal bell curve assumption holds.'}
              </div>
            </div>
          </div>

          {/* Graphical Returns Distribution Simulation */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
              <Layers className="w-5 h-5 text-cyan-400" />
              Empirical Portfolio Return Distribution (Last 100 Trading Days)
            </h3>
            <div className="h-44 flex items-end gap-1 pt-6 px-2 border-b border-slate-800">
              {data.returns_distribution.map((val: number, idx: number) => {
                const height = Math.min(100, Math.max(10, Math.abs(val) * 2000));
                const isLoss = val < 0;
                const isBreach = val < -data.historical_var.percentage;
                return (
                  <div
                    key={idx}
                    className={`flex-1 rounded-t transition-all ${
                      isBreach
                        ? 'bg-rose-500 shadow-lg shadow-rose-500/50'
                        : isLoss
                        ? 'bg-amber-500/70'
                        : 'bg-emerald-500/70'
                    }`}
                    style={{ height: `${height}%` }}
                    title={`Day ${idx + 1}: ${(val * 100).toFixed(2)}%`}
                  />
                );
              })}
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500 mt-3 font-mono">
              <span>← Day -100</span>
              <span className="text-rose-400 flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-500 inline-block" /> Red bars indicate VaR breaches
              </span>
              <span>Latest →</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
