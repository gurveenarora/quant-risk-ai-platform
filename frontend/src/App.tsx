import React, { useState } from 'react';
import { BarChart3, ShieldCheck, Terminal, Bot, Globe, Lock, Shield, Cpu } from 'lucide-react';
import { QuantWorkbench } from './components/QuantWorkbench';
import { KupiecSuite } from './components/KupiecSuite';
import { PropertyTerminal } from './components/PropertyTerminal';
import { AgentCopilot } from './components/AgentCopilot';
import { ScraperModule } from './components/ScraperModule';
import { SecurityAudit } from './components/SecurityAudit';

export default function App() {
  const [activeTab, setActiveTab] = useState<'quant' | 'kupiec' | 'pbt' | 'copilot' | 'scraper' | 'security'>('quant');

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg glow-cyan">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
              QuantRisk <span className="text-cyan-400 text-xs px-2 py-0.5 rounded-full bg-cyan-950 border border-cyan-800">v2.0 Enterprise</span>
            </h1>
            <p className="text-xs text-slate-400">Full-Stack AI, Data, Infra & Security Engineer Portfolio Platform</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden lg:flex items-center gap-1 bg-slate-900/80 p-1.5 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('quant')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'quant' ? 'bg-cyan-500 text-white shadow-md glow-cyan' : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-4 h-4" /> VaR Engine
          </button>
          <button
            onClick={() => setActiveTab('kupiec')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'kupiec' ? 'bg-emerald-500 text-white shadow-md glow-emerald' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-4 h-4" /> Kupiec Backtest
          </button>
          <button
            onClick={() => setActiveTab('pbt')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'pbt' ? 'bg-purple-500 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Terminal className="w-4 h-4" /> Hypothesis PBT
          </button>
          <button
            onClick={() => setActiveTab('copilot')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'copilot' ? 'bg-blue-500 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Bot className="w-4 h-4" /> Agentic Copilot
          </button>
          <button
            onClick={() => setActiveTab('scraper')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'scraper' ? 'bg-indigo-500 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Globe className="w-4 h-4" /> Playwright Scraper
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition ${
              activeTab === 'security' ? 'bg-rose-500 text-white shadow-md' : 'text-slate-400 hover:text-white'
            }`}
          >
            <Lock className="w-4 h-4" /> Security & IAM
          </button>
        </nav>

        <div className="flex items-center gap-2">
          <a
            href="https://the-applied-quant.hashnode.dev/"
            target="_blank"
            rel="noreferrer"
            className="px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700/60 text-slate-300 hover:text-white text-xs font-medium transition flex items-center gap-2"
          >
            <Shield className="w-4 h-4 text-cyan-400" /> Published Research
          </a>
        </div>
      </header>

      {/* Main Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6">
        {activeTab === 'quant' && <QuantWorkbench />}
        {activeTab === 'kupiec' && <KupiecSuite />}
        {activeTab === 'pbt' && <PropertyTerminal />}
        {activeTab === 'copilot' && <AgentCopilot />}
        {activeTab === 'scraper' && <ScraperModule />}
        {activeTab === 'security' && <SecurityAudit />}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 px-6 text-center text-xs text-slate-500 font-mono">
        QuantRisk Platform • Based on published research at{' '}
        <a href="https://the-applied-quant.hashnode.dev/" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">
          the-applied-quant.hashnode.dev
        </a>
      </footer>
    </div>
  );
}
