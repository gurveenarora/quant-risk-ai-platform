import React, { useState } from 'react';
import { Bot, Send, Wrench, Shield, Sparkles, BookOpen, User } from 'lucide-react';

export const AgentCopilot: React.FC = () => {
  const [prompt, setPrompt] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [messages, setMessages] = useState<any[]>([
    {
      sender: 'agent',
      text: 'Hello! I am your Agentic Quant AI Copilot. Ask me to calculate VaR, execute Kupiec POF backtests, run Hypothesis property-based tests, or search your published research papers!',
      tools: ['Tool: vector_rag_search'],
      rag: []
    }
  ]);

  const sendQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || loading) return;

    const userText = prompt;
    setPrompt('');
    setMessages((prev) => [...prev, { sender: 'user', text: userText }]);
    setLoading(true);

    try {
      const response = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: userText, user_role: 'QuantAnalyst' })
      });
      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: data.response,
          tools: data.tool_calls_executed || [],
          rag: data.rag_references || [],
          security: data.security_alert
        }
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass-panel p-6 rounded-2xl flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Bot className="text-cyan-400 w-7 h-7" />
            Agentic Quant Copilot & Vector RAG Workbench
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Multi-step tool calling, scratchpad memory, and AI Security Guardrails.
          </p>
        </div>
        <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1.5">
          <Shield className="w-4 h-4" /> AI Security Active
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="glass-card rounded-2xl p-6 h-[480px] flex flex-col justify-between border border-slate-800">
        <div className="overflow-y-auto space-y-4 pr-2">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.sender === 'agent' && (
                <div className="w-9 h-9 rounded-xl bg-cyan-600/30 border border-cyan-500/40 flex items-center justify-center shrink-0">
                  <Bot className="w-5 h-5 text-cyan-400" />
                </div>
              )}
              <div
                className={`max-w-2xl rounded-2xl p-4 space-y-3 ${
                  msg.sender === 'user'
                    ? 'bg-cyan-600 text-white rounded-tr-none'
                    : 'bg-slate-900/90 border border-slate-800 text-slate-200 rounded-tl-none'
                }`}
              >
                {/* Text Message */}
                <div className="whitespace-pre-line text-sm leading-relaxed">{msg.text}</div>

                {/* Executed Tools Chips */}
                {msg.tools && msg.tools.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 flex flex-wrap gap-1.5">
                    {msg.tools.map((t: string, tIdx: number) => (
                      <span
                        key={tIdx}
                        className="px-2.5 py-0.5 rounded-md bg-cyan-950/80 border border-cyan-800/60 text-cyan-300 text-[11px] font-mono flex items-center gap-1"
                      >
                        <Wrench className="w-3 h-3 text-cyan-400" /> {t}
                      </span>
                    ))}
                  </div>
                )}

                {/* RAG Reference Sources */}
                {msg.rag && msg.rag.length > 0 && (
                  <div className="pt-2 border-t border-slate-800 space-y-1.5">
                    <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
                      <BookOpen className="w-3 h-3 text-purple-400" /> RAG Knowledge Base Sources:
                    </span>
                    {msg.rag.map((r: any, rIdx: number) => (
                      <div key={rIdx} className="bg-slate-950/60 p-2 rounded border border-slate-800/60 text-xs">
                        <span className="font-semibold text-purple-300 block">{r.title}</span>
                        <span className="text-slate-400 line-clamp-2 mt-0.5">{r.content}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {msg.sender === 'user' && (
                <div className="w-9 h-9 rounded-xl bg-purple-600/30 border border-purple-500/40 flex items-center justify-center shrink-0">
                  <User className="w-5 h-5 text-purple-400" />
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Input Form */}
        <form onSubmit={sendQuery} className="pt-4 border-t border-slate-800 flex gap-2">
          <input
            type="text"
            placeholder="Ask me to calculate VaR, run Kupiec backtests, or search papers..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="flex-1 bg-slate-900 border border-slate-700/60 rounded-xl px-4 py-3 text-white text-sm focus:outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-medium flex items-center gap-2 transition disabled:opacity-50"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};
