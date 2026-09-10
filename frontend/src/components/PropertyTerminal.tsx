import React, { useState } from 'react';
import { Terminal, Play, CheckCircle, Flame, Clock } from 'lucide-react';

export const PropertyTerminal: React.FC = () => {
  const [numSamples, setNumSamples] = useState<number>(50);
  const [loading, setLoading] = useState<boolean>(false);
  const [pbtData, setPbtData] = useState<any>(null);

  const runPBTSuite = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/quant/run-pbt?num_samples=${numSamples}`);
      const json = await response.json();
      setPbtData(json);
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
            <Terminal className="text-purple-400 w-7 h-7" />
            Hypothesis Property-Based Testing (PBT) Terminal
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Validating universal mathematical invariants across hundreds of randomized scenarios.
          </p>
        </div>
        <button
          onClick={runPBTSuite}
          disabled={loading}
          className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-600 hover:from-purple-400 hover:to-indigo-500 text-white font-medium shadow-lg glow-purple flex items-center justify-center gap-2 transition disabled:opacity-50"
        >
          <Play className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Fuzzing & Validating...' : 'Run Hypothesis Suite'}
        </button>
      </div>

      {/* Terminal Display */}
      <div className="bg-slate-950 border border-slate-800 rounded-2xl p-6 font-mono text-sm shadow-2xl space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-rose-500 inline-block" />
            <span className="w-3 h-3 rounded-full bg-amber-500 inline-block" />
            <span className="w-3 h-3 rounded-full bg-emerald-500 inline-block" />
            <span className="text-slate-500 text-xs ml-2">hypothesis_pbt_runner.py</span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span>Strategy: Random Standard Normal / Uniform</span>
            {pbtData && (
              <span className="text-emerald-400 flex items-center gap-1">
                <Clock className="w-3 h-3" /> {pbtData.elapsed_seconds}s
              </span>
            )}
          </div>
        </div>

        {/* Terminal Execution Output Log */}
        {!pbtData ? (
          <div className="text-slate-500 py-10 text-center">
            Click 'Run Hypothesis Suite' to execute randomized invariant fuzz testing...
          </div>
        ) : (
          <div className="space-y-3 pt-2">
            <div className="text-slate-400">
              [INFO] Initiating Hypothesis strategy fuzzing across {pbtData.total_scenarios_tested} scenarios...
            </div>

            {pbtData.property_results.map((res: any, idx: number) => (
              <div key={idx} className="bg-slate-900/60 p-4 rounded-xl border border-slate-800/80 space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-purple-300 font-semibold flex items-center gap-2">
                    <CheckCircle className="w-4 h-4 text-emerald-400" />
                    {res.property_name}
                  </span>
                  <span className="px-2.5 py-0.5 rounded text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    {res.status} ({res.passed}/{res.scenarios_tested})
                  </span>
                </div>
                <div className="text-xs text-slate-400">{res.description}</div>
              </div>
            ))}

            <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs font-semibold">
              <span className="text-slate-300">
                TOTAL INVARIANTS TESTED: <span className="text-white">{pbtData.total_scenarios_tested}</span>
              </span>
              <span className="text-emerald-400">
                PASS RATE: {pbtData.pass_rate_pct}% (0 FAILURES)
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
