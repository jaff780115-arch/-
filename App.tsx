
import React, { useState, useRef } from 'react';
import { ChartImage, PROMPT_CATEGORIES, PromptItem } from './types';
import { analyzeCharts } from './services/geminiService';
import { 
  Sparkles, 
  Upload, 
  Trash2, 
  Send, 
  Loader2, 
  Image as ImageIcon,
  History,
  Info,
  ChevronRight,
  BrainCircuit,
  Settings2
} from 'lucide-react';

const App: React.FC = () => {
  const [images, setImages] = useState<ChartImage[]>([]);
  const [customPrompt, setCustomPrompt] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<string>('');
  const [history, setHistory] = useState<{ prompt: string, result: string, date: string }[]>([]);
  
  // 變數狀態
  const [vars, setVars] = useState({
    current_job: '',
    strength_a: '',
    strength_b: ''
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const resultEndRef = useRef<HTMLDivElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files).map((file: File) => ({
        id: Math.random().toString(36).substring(2, 11),
        file,
        preview: URL.createObjectURL(file)
      }));
      setImages(prev => [...prev, ...newFiles]);
    }
  };

  const removeImage = (id: string) => {
    setImages(prev => {
      const filtered = prev.filter(img => img.id !== id);
      const removed = prev.find(img => img.id === id);
      if (removed) URL.revokeObjectURL(removed.preview);
      return filtered;
    });
  };

  const startAnalysis = async () => {
    if (images.length === 0) {
      alert('請先上傳命盤截圖');
      return;
    }
    
    let finalPrompt = customPrompt.trim() || PROMPT_CATEGORIES[0].items[0].template;
    
    // 處理變數替換
    finalPrompt = finalPrompt
      .replace(/{current_job}/g, vars.current_job || "[未填寫]")
      .replace(/{strength_a}/g, vars.strength_a || "[未填寫]")
      .replace(/{strength_b}/g, vars.strength_b || "[未填寫]");

    setIsAnalyzing(true);
    setResult('');
    
    try {
      const fullResult = await analyzeCharts(images, finalPrompt, (chunk) => {
        setResult(prev => prev + chunk);
        resultEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      });
      
      setHistory(prev => [{
        prompt: finalPrompt,
        result: fullResult,
        date: new Date().toLocaleString()
      }, ...prev].slice(0, 10));

    } catch (error: any) {
      setResult(`錯誤: ${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const useTemplate = (item: PromptItem) => {
    setCustomPrompt(item.template);
  };

  const updateVar = (key: keyof typeof vars, val: string) => {
    setVars(prev => ({ ...prev, [key]: val }));
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200 selection:bg-amber-500/30">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/40 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-gradient-to-tr from-amber-500 to-orange-600 p-1.5 rounded-xl shadow-lg shadow-orange-900/20">
              <BrainCircuit className="w-5 h-5 text-slate-950" />
            </div>
            <h1 className="text-xl font-bold font-serif tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-500 bg-clip-text text-transparent">
              CelestialLens <span className="text-xs font-normal text-slate-500 ml-1">Pro Thinking</span>
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setHistory([])}
              className="p-2 text-slate-500 hover:text-slate-300 transition-colors"
            >
              <History className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Data & Setup */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Step 1: Chart Upload */}
          <section className="bg-slate-900/30 border border-slate-800/60 rounded-3xl p-6 backdrop-blur-sm shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2">
                <ImageIcon className="w-4 h-4 text-amber-500" />
                命盤截圖
              </h2>
              <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded-full text-slate-400">{images.length} 份資料</span>
            </div>
            
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer hover:border-amber-500/30 hover:bg-slate-800/20 transition-all group"
            >
              <Upload className="w-8 h-8 text-slate-700 mb-2 group-hover:text-amber-500 transition-colors" />
              <p className="text-xs text-slate-500">上傳八字、紫微、或合婚截圖</p>
              <input 
                type="file" multiple accept="image/*" className="hidden" 
                ref={fileInputRef} onChange={handleFileChange}
              />
            </div>

            {images.length > 0 && (
              <div className="mt-4 flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
                {images.map((img) => (
                  <div key={img.id} className="relative shrink-0 w-20 aspect-square rounded-xl overflow-hidden border border-slate-800 ring-1 ring-white/5">
                    <img src={img.preview} alt="preview" className="w-full h-full object-cover" />
                    <button 
                      onClick={(e) => { e.stopPropagation(); removeImage(img.id); }}
                      className="absolute top-1 right-1 bg-black/60 backdrop-blur-md p-1 rounded-md text-white/70 hover:text-red-400"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Step 2: Specialized Prompts */}
          <section className="bg-slate-900/30 border border-slate-800/60 rounded-3xl p-6 backdrop-blur-sm shadow-xl">
            <h2 className="text-sm font-bold uppercase tracking-widest text-slate-400 flex items-center gap-2 mb-4">
              <Settings2 className="w-4 h-4 text-amber-500" />
              AI 戰略指令集
            </h2>
            
            <div className="space-y-6">
              {PROMPT_CATEGORIES.map((cat, i) => (
                <div key={i} className="space-y-2">
                  <h3 className="text-xs font-medium text-slate-500 px-1">{cat.title}</h3>
                  <div className="flex flex-wrap gap-2">
                    {cat.items.map((item) => (
                      <button 
                        key={item.id}
                        onClick={() => useTemplate(item)}
                        className="text-[11px] px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700/50 hover:bg-amber-500 hover:text-slate-950 hover:border-amber-500 transition-all text-slate-300"
                      >
                        {item.label}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Variable Inputs */}
            <div className="mt-6 pt-6 border-t border-slate-800/50 space-y-4">
              <div className="grid grid-cols-1 gap-3">
                <div className="space-y-1">
                  <label className="text-[10px] text-slate-500 uppercase font-bold px-1">目前從事職業 (OO)</label>
                  <input 
                    type="text" value={vars.current_job} onChange={e => updateVar('current_job', e.target.value)}
                    placeholder="例如：行銷主管、自由接案者..."
                    className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-2 text-xs focus:ring-1 focus:ring-amber-500/50 outline-none"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase font-bold px-1">強項 A</label>
                    <input 
                      type="text" value={vars.strength_a} onChange={e => updateVar('strength_a', e.target.value)}
                      placeholder="例如：溝通"
                      className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-2 text-xs focus:ring-1 focus:ring-amber-500/50 outline-none"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] text-slate-500 uppercase font-bold px-1">強項 B</label>
                    <input 
                      type="text" value={vars.strength_b} onChange={e => updateVar('strength_b', e.target.value)}
                      placeholder="例如：美感"
                      className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-2 text-xs focus:ring-1 focus:ring-amber-500/50 outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6">
              <textarea 
                value={customPrompt}
                onChange={(e) => setCustomPrompt(e.target.value)}
                placeholder="在此編輯或預覽最終指令..."
                className="w-full h-32 bg-slate-950/50 border border-slate-800 rounded-xl p-3 text-xs focus:outline-none focus:ring-1 focus:ring-amber-500/50 resize-none font-mono text-slate-400"
              />
            </div>
          </section>

          <button 
            disabled={isAnalyzing || images.length === 0}
            onClick={startAnalysis}
            className={`w-full py-4 rounded-2xl font-bold flex items-center justify-center gap-2 transition-all shadow-xl ${
              isAnalyzing || images.length === 0 
              ? 'bg-slate-800 text-slate-600 cursor-not-allowed' 
              : 'bg-gradient-to-r from-amber-500 to-orange-600 text-slate-950 hover:scale-[1.01] active:scale-[0.98] shadow-orange-950/20'
            }`}
          >
            {isAnalyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                正在啟動 Pro 思考模式...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                開始 AI 深度解讀
              </>
            )}
          </button>
        </div>

        {/* Right Column: Deep Analysis Result */}
        <div className="lg:col-span-7 flex flex-col min-h-[700px]">
          <div className="flex-1 bg-slate-900/20 border border-slate-800/40 rounded-[2.5rem] p-8 relative flex flex-col shadow-2xl backdrop-blur-md">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h3 className="font-serif text-2xl italic text-amber-500">Strategic Insight</h3>
                <p className="text-[10px] text-slate-500 uppercase tracking-widest mt-1">Generated by Gemini 3 Pro</p>
              </div>
              <div className="flex gap-1.5">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="w-1.5 h-1.5 rounded-full bg-slate-800 shadow-inner"></div>
                ))}
              </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-6 pr-4 custom-scrollbar">
              {!result && !isAnalyzing ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-700 text-center space-y-4">
                  <div className="p-6 bg-slate-900/50 rounded-full ring-1 ring-slate-800">
                    <BrainCircuit className="w-12 h-12 opacity-10" />
                  </div>
                  <div className="max-w-xs">
                    <p className="text-sm font-medium">準備進行高階命理運算</p>
                    <p className="text-xs text-slate-600 mt-1">請上傳您的命盤資料，並從左側選擇解讀角度。Pro 模型將會進行深度鏈式思考。</p>
                  </div>
                </div>
              ) : (
                <div className="prose prose-invert prose-amber prose-sm max-w-none">
                  {/* Markdown content container */}
                  <div className="whitespace-pre-wrap leading-relaxed text-slate-300 font-light text-base">
                    {result}
                  </div>
                  <div ref={resultEndRef} />
                </div>
              )}
            </div>

            {isAnalyzing && (
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-4 pointer-events-none">
                <div className="relative">
                  <div className="absolute inset-0 bg-amber-500/20 blur-3xl rounded-full animate-pulse"></div>
                  <Loader2 className="w-12 h-12 text-amber-500 animate-spin relative z-10" />
                </div>
                <div className="bg-slate-950/80 backdrop-blur-xl px-5 py-2.5 rounded-2xl border border-slate-800 flex items-center gap-3">
                  <div className="flex gap-1">
                    <span className="w-1 h-1 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1 h-1 bg-amber-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1 h-1 bg-amber-500 rounded-full animate-bounce"></span>
                  </div>
                  <span className="text-[10px] uppercase tracking-[0.2em] font-black text-amber-500/80">Pro Thinking Active</span>
                </div>
              </div>
            )}
          </div>
          
          {/* Legend / Tips */}
          <div className="mt-6 flex flex-wrap gap-4 px-4 justify-center">
            <div className="flex items-center gap-2 text-[10px] text-slate-600">
              <span className="w-2 h-2 rounded-full bg-amber-500/50"></span>
              <span>思考模式已開啟 (32k)</span>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-slate-600">
              <span className="w-2 h-2 rounded-full bg-orange-500/50"></span>
              <span>Gemini 3 Pro Preview</span>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-slate-600">
              <span className="w-2 h-2 rounded-full bg-blue-500/50"></span>
              <span>跨維度天賦分析</span>
            </div>
          </div>
        </div>
      </main>

      <footer className="mt-12 py-10 border-t border-slate-900 text-center space-y-2">
        <p className="text-slate-600 text-xs font-medium uppercase tracking-widest">
          CelestialLens Destiny System
        </p>
        <p className="text-slate-800 text-[10px] max-w-lg mx-auto leading-relaxed px-6">
          本系統運用人工智慧進行模擬分析，所有命理數據僅供決策參考。請以積極心態規劃人生，把握每一次選擇的權利。
        </p>
      </footer>
    </div>
  );
};

export default App;
