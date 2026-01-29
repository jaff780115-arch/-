
export interface ChartImage {
  id: string;
  file: File;
  preview: string;
}

export interface AnalysisResult {
  text: string;
  timestamp: number;
}

export interface PromptItem {
  id: string;
  label: string;
  template: string;
  hasVariables?: boolean;
}

export interface PromptCategory {
  title: string;
  items: PromptItem[];
}

export const PROMPT_CATEGORIES: PromptCategory[] = [
  {
    title: "一. 基本解讀",
    items: [
      {
        id: "basic_consultant",
        label: "八字顧問綜合分析",
        template: "請你當我的八字顧問，詳細分析這張截圖的命主性格，日主五行、身強或身弱。\n\n並請依序解讀：\na. 根據格局，提議多元且符合現代趨勢的工作事業方式。\nb. 分析我的財務能量與五行喜忌用神。\nc. 分析命盤所有不同階段的十年大運，與十神的特性(請附整理表格)。\n備註： 我是 [男] 性。"
      }
    ]
  },
  {
    title: "二. 探索天賦地圖",
    items: [
      { id: "talent_1", label: "我的天賦是什麼？", template: "根據我的命盤，你認為我有什麼天賦呢？" },
      { id: "talent_2", label: "地球體驗天賦", template: "根據我的八字，你認為我有什麼天賦，能讓我在地球上好好體驗呢？" },
      { 
        id: "talent_3", 
        label: "事業現狀避坑", 
        template: "我目前正在做 {current_job}，根據我的八字能量，我該注意什麼才能事半功倍？",
        hasVariables: true 
      },
      { id: "talent_4", label: "AI 與我的天賦發揮", template: "AI對我發揮天賦的意義是什麼？我可以如何運用Gemini以及其他AI工具來發揮能力？請為我分析，謝謝。" },
      { id: "talent_5", label: "生命設計顧問 (機器比喻)", template: "你現在是我的生命設計顧問：如果我是一台精密機器，我的原廠設定『預設強項』與『容易耗能的地方』分別是什麼？" }
    ]
  },
  {
    title: "三. 進階運勢能量",
    items: [
      { id: "adv_1", label: "未來趨勢工作方式", template: "關於八字的能量，我適合什麼什麼類型的工作方式？（符合未來趨勢、多元彈性的）" },
      { id: "adv_2", label: "三元九運：離火運策略", template: "在三元九運的「離火運」下，如何發揮我的事業天賦與商業模式？" },
      { id: "adv_3", label: "當前大運天賦發揮", template: "在我目前的大運狀態下，如何發揮我的天賦？" },
      { 
        id: "adv_4", 
        label: "職業戰略家模式", 
        template: "請你進入『職業戰略家』模式。根據剛才解析的八字十神格局，我注意到我有 [強項 A：{strength_a}] 與 [強項 B：{strength_b}] 這兩種能量。\n\n請幫我依序進行以下探索：\na. 化學反應分析：這兩種能量結合時，會產生什麼樣的『獨特工作風格』？\nb. 跨領域提案：請提出 3 個非傳統、具備未來感的『職業組合』，這些組合必須能同時發揮我的技術才華與內在價值感。\nc. 避坑指南：在整合這些能力時，我最容易遇到的『自我內耗』點是什麼？",
        hasVariables: true
      }
    ]
  },
  {
    title: "四. 語氣風格轉換",
    items: [
      { id: "style_1", label: "白話解讀", template: "請幫我將以上分析，用白話的方式解讀。" },
      { id: "style_2", label: "身心靈解讀", template: "請幫我將以上分析，用身心靈的方式解讀。" },
      { id: "style_3", label: "能量角度解讀", template: "請幫我將以上分析，用能量的方式解讀。" }
    ]
  }
];
