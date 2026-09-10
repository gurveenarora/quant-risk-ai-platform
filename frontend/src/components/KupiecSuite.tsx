import React, { useState } from 'react';
import { ShieldCheck, ShieldAlert, Play, CheckCircle2, XCircle, Info } from 'lucide-react';

export const KupiecSuite: React.FC = () => {
  const [windowSize, setWindowSize] = useState<number>(250);
  const [confidenceLevel, setConfidenceLevel] = useState<number>(0.95);
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<any>(null);

  const runBacktest = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/quant/kupiec-backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: ['AAPL', 'MSFT', 'NVDA', 'GOOGL'],
          weights: [0.25, 0.25, 0.25, 0.25],
          window_size: windowSize,
          confidence_level: confidenceLevel
        })
      });
      const json = await response.json();
      setResults(json);
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
            <ShieldCheck className="text-emerald-400 w-7 h-7" />
            Kupiec POF Statistical Model Validation Suite
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Likelihood Ratio (LR) Chi-Square test assessing VaR exception frequency without look-ahead bias.
          </p>
        </div>
        <button
          onClick={runBacktest}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-white font-medium shadow-lg glow-emerald flex items-center justify-center gap-2 transition disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Running Backtest...' : 'Execute Kupiec Test'}
        </button>
      </div>

      {/* Control Inputs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="glass-card p-5 rounded-xl">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Rolling Window Size (n observations)
          </label>
          <input
            type="number"
            value={windowSize}
            onChange={(e) => setWindowSize(Number(e.target.value))}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg px-4 py-2.5 text-white font-mono focus:outline-none focus:border-emerald-500"
          />
        </div>
        <div className="glass-card p-5 rounded-xl">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-2">
            Target Confidence (1 - p)
          </label>
          <select
            value={confidenceLevel}
            onChange={(e) => setConfidenceLevel(Number(e.target.value))}
            className="w-full bg-slate-900/80 border border-slate-700/60 rounded-lg px-4 py-2.5 text-white font-mono focus:outline-none focus:border-emerald-500"
          >
            <option value={0.95}>95% Confidence (5% Expected Exception Rate)</option>
            <option value={0.99}>99% Confidence (1% Expected Exception Rate)</option>
          </select>
        </div>
      </div>

      {/* Backtest Output Grid */}
      {results && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Historical VaR Backtest Results */}
            <div className="glass-card p-6 rounded-2xl border border-slate-800 relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Historical VaR Backtest</h3>
                {results.historical_var_backtest.reject_model ? (
                  <span className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-400 text-xs font-semibold border border-rose-500/30 flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> REJECTED
                  </span>
                ) : (
                  <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-semibold border border-emerald-500/30 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> PASSED
                  </span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm font-mono bg-slate-900/60 p-4 rounded-xl">
                <div>
                  <span className="text-slate-500 text-xs block">Observed Exceptions</span>
                  <span className="text-white text-lg font-bold">
                    {results.historical_var_backtest.n_exceptions} / {results.historical_var_backtest.n_obs}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 text-xs block">Expected Exceptions</span>
                  <span className="text-slate-300 text-lg font-bold">
                    {results.historical_var_backtest.expected_exceptions}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 text-xs block">LR Statistic</span>
                  <span className="text-cyan-400 text-lg font-bold">
                    {results.historical_var_backtest.LR_statistic}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 text-xs block">p-value (df=1)</span>
                  <span className="text-emerald-400 text-lg font-bold">
                    {results.historical_var_backtest.p_value}
                  </span>
                </div>
              </div>
            </div>

            {/* Parametric VaR Backtest Results */}
            <div className="glass-card p-6 rounded-2xl border border-slate-800 relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Parametric VaR Backtest</h3>
                {results.parametric_var_backtest.reject_model ? (
                  <span className="px-3 py-1 rounded-full bg-rose-500/20 text-rose-400 text-xs font-semibold border border-rose-500/30 flex items-center gap-1">
                    <XCircle className="w-3.5 h-3.5" /> REJECTED
                  </span>
                ) : (
                  <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-400 text-xs font-semibold border border-emerald-500/30 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> PASSED
                  </span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm font-mono bg-slate-900/60 p-4 rounded-xl">
                <div>
                  <span className="text-slate-500 text-xs block">Observed Exceptions</span>
                  <span className="text-white text-lg font-bold">
                    {results.parametric_var_backtest.n_exceptions} / {results.parametric_var_backtest.n_obs}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 text-xs block">Expected Exceptions</span>
                  <span className="text-slate-300 text-lg font-bold">
                    {results.parametric_var_backtest.expected_exceptions}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 text-xs block">LR Statistic</span>
                  <span className="text-cyan-400 text-lg font-bold">
                    {results.parametric_var_backtest.LR_statistic}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 text-xs block">p-value (df=1)</span>
                  <span className="text-emerald-400 text-lg font-bold">
                    {results.parametric_var_backtest.p_value}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Model Recommendation Banner */}
          <div className="glass-panel p-5 rounded-xl border border-cyan-500/30 text-slate-300 text-sm flex items-start gap-3">
            <Info className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold text-white">Quant Validation Verdict: </span>
              {results.recommendation}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
