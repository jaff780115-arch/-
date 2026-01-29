
import React, { useState, useRef, useEffect } from 'react';
import { ChartImage, PROMPT_CATEGORIES, STYLE_OPTIONS, PromptItem } from './types';
import { analyzeCharts } from './services/geminiService';
import { 
  Sparkles, 
  Upload, 
  Trash2, 
  Loader2, 
  Image as ImageIcon,
  History,
  BrainCircuit,
  LayoutGrid,
  Zap,
  MessageSquareQuote
} from 'lucide-react';

const App: React.FC = () => {
  const [images, setImages] = useState<ChartImage[]>([]);
  const [selectedCatIndex, setSelectedCatIndex] = useState(0);
  const [selectedItemIndex, setSelectedItemIndex] = useState(0);
  const [selectedStyleId, setSelectedStyleId] = useState('default');
  const [customPrompt, setCustomPrompt] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<string>('');
  
  const [vars, setVars] = useState({
    current_job: '',
    strength_a: '',
    strength_b: ''
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const resultEndRef = useRef<HTMLDivElement>(null);

  // 當選擇變更時，自動更新預覽指令
  useEffect(() => {
    const item = PROMPT_CATEGORIES[selectedCatIndex].items[selectedItemIndex];
    const style = STYLE_OPTIONS.find(s => s.id === selectedStyleId);
    setCustomPrompt(item.template + (style?.suffix || ''));
  }, [selectedCatIndex, selectedItemIndex, selectedStyleId]);

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
      const removed = prev.find(img => img.id === id);
      if (removed) URL.revokeObjectURL(removed.preview);
      return prev.filter(img => img.id !== id);
    });
  };

  const startAnalysis = async () => {
    if (images.length === 0) {
      alert('請先上傳命盤截圖');
      return;
    }

    let finalPrompt = customPrompt.trim();
    finalPrompt = finalPrompt
      .replace(/{current_job}/g, vars.current_job || "[自由業]")
      .replace(/{strength_a}/g, vars.strength_a || "[未指定]")
      .replace(/{strength_b}/g, vars.strength_b || "[未指定]");

    setIsAnalyzing(true);
    setResult('');
    
    try {
      await analyzeCharts(images, finalPrompt, (chunk) => {
        setResult(prev => prev + chunk);
        resultEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      });
    } catch (error: any) {
      setResult(`解讀失敗：${error.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#020617] text-slate-200">
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Zap className="w-6 h-6 text-amber-500 fill-amber-500" />
            <h1 className="text-xl font-bold font-serif bg-gradient-to-r from-white to-slate-500 bg-clip-text text-transparent">
              CelestialLens <span className="text-xs font-normal text-slate-500 ml-1">Flash Edition</span>
            </h1>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* 控制面板 */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* 上傳區 */}
          <section className="bg-slate-900/40 border border-slate-800 rounded-2xl p-5">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 flex items-center gap-2">
              <ImageIcon className="w-3.5 h-3.5" /> 命盤資料
            </h2>
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-slate-800 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer hover:bg-slate-800/30 transition-all group"
            >
              <Upload className="w-6 h-6 text-slate-600 mb-2 group-hover:text-amber-500" />
              <p className="text-[10px] text-slate-500">點擊上傳多張截圖</p>
              <input type="file" multiple accept="image/*" className="hidden" ref={fileInputRef} onChange={handleFileChange} />
            </div>

            {images.length > 0 && (
              <div className="mt-4 flex gap-2 overflow-x-auto pb-2">
                {images.map((img) => (
                  <div key={img.id} className="relative w-14 h-14 rounded-lg overflow-hidden border border-slate-800 shrink-0">
                    <img src={img.preview} className="w-full h-full object-cover" />
                    <button onClick={() => removeImage(img.id)} className="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 flex items-center justify-center transition-opacity">
                      <Trash2 className="w-3 h-3 text-red-400" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* 指令設定區 */}
          <section className="bg-slate-900/40 border border-slate-800 rounded-2xl p-5 space-y-4">
            <h2 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 flex items-center gap-2">
              <LayoutGrid className="w-3.5 h-3.5" /> 指令配置
            </h2>
            
            <div className="space-y-3">
              <div>
                <label className="text-[10px] text-slate-500 block mb-1">1. 功能分類</label>
                <select 
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm outline-none focus:border-amber-500/50"
                  value={selectedCatIndex}
                  onChange={(e) => { setSelectedCatIndex(Number(e.target.value)); setSelectedItemIndex(0); }}
                >
                  {PROMPT_CATEGORIES.map((cat, i) => <option key={i} value={i}>{cat.title}</option>)}
                </select>
              </div>

              <div>
                <label className="text-[10px] text-slate-500 block mb-1">2. 具體指令</label>
                <select 
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm outline-none focus:border-amber-500/50"
                  value={selectedItemIndex}
                  onChange={(e) => setSelectedItemIndex(Number(e.target.value))}
                >
                  {PROMPT_CATEGORIES[selectedCatIndex].items.map((item, i) => <option key={i} value={i}>{item.label}</option>)}
                </select>
              </div>

              <div>
                <label className="text-[10px] text-slate-500 block mb-1">3. 語氣風格</label>
                <select 
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-sm outline-none focus:border-amber-500/50"
                  value={selectedStyleId}
                  onChange={(e) => setSelectedStyleId(e.target.value)}
                >
                  {STYLE_OPTIONS.map((style) => <option key={style.id} value={style.id}>{style.label}</option>)}
                </select>
              </div>
            </div>

            {/* 參數輸入 */}
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <input 
                type="text" placeholder="目前職業 (選填)" value={vars.current_job}
                onChange={e => setVars({...vars, current_job: e.target.value})}
                className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-2 text-xs outline-none"
              />
              <div className="grid grid-cols-2 gap-2">
                <input 
                  type="text" placeholder="強項 A" value={vars.strength_a}
                  onChange={e => setVars({...vars, strength_a: e.target.value})}
                  className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-2 text-xs outline-none"
                />
                <input 
                  type="text" placeholder="強項 B" value={vars.strength_b}
                  onChange={e => setVars({...vars, strength_b: e.target.value})}
                  className="w-full bg-slate-950/50 border border-slate-800 rounded-lg p-2 text-xs outline-none"
                />
              </div>
            </div>

            <textarea 
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
              className="w-full h-24 bg-slate-950/30 border border-slate-800 rounded-lg p-2 text-[10px] font-mono text-slate-500 resize-none outline-none"
            />
          </section>

          <button 
            disabled={isAnalyzing || images.length === 0}
            onClick={startAnalysis}
            className={`w-full py-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all ${
              isAnalyzing || images.length === 0 
              ? 'bg-slate-800 text-slate-600' 
              : 'bg-amber-500 text-slate-950 hover:bg-amber-400 shadow-lg shadow-amber-900/20'
            }`}
          >
            {isAnalyzing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
            {isAnalyzing ? '正在解讀命盤...' : '開始 AI 命理分析'}
          </button>
        </div>

        {/* 結果顯示區 */}
        <div className="lg:col-span-8">
          <div className="bg-slate-900/20 border border-slate-800 rounded-3xl p-6 min-h-[600px] flex flex-col backdrop-blur-sm">
            <div className="flex items-center gap-3 mb-6 border-b border-slate-800/50 pb-4">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
              <h3 className="font-serif text-lg text-slate-300">Analysis Report</h3>
              <span className="text-[10px] text-slate-600 ml-auto uppercase tracking-tighter">Gemini 3 Flash</span>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
              {!result && !isAnalyzing ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-700 opacity-40">
                  <BrainCircuit className="w-16 h-16 mb-4" />
                  <p className="text-sm">等待輸入資料與指令</p>
                </div>
              ) : (
                <div className="prose prose-invert prose-amber max-w-none">
                  <div className="text-slate-300 leading-relaxed whitespace-pre-wrap">
                    {result}
                  </div>
                  <div ref={resultEndRef} />
                </div>
              )}
            </div>
            
            {isAnalyzing && (
              <div className="flex items-center gap-2 mt-4 text-xs text-amber-500/60 font-medium">
                <Loader2 className="w-3 h-3 animate-spin" />
                正在接收 AI 智慧串流...
              </div>
            )}
          </div>
        </div>
      </main>
      
      <footer className="py-8 text-center border-t border-slate-900/50 mt-12">
        <p className="text-[10px] text-slate-700 uppercase tracking-[0.3em]">CelestialLens System v3.0</p>
      </footer>
    </div>
  );
};

export default App;
