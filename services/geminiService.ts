
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { ChartImage } from "../types";

export const analyzeCharts = async (
  images: ChartImage[],
  prompt: string,
  onStream?: (chunk: string) => void
): Promise<string> => {
  // 使用最新 API Key
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
  // 圖片處理
  const imageParts = await Promise.all(
    images.map(async (img) => {
      const base64Data = await fileToBase64(img.file);
      return {
        inlineData: {
          mimeType: img.file.type,
          data: base64Data,
        },
      };
    })
  );

  const textPart = { text: prompt };

  try {
    const responseStream = await ai.models.generateContentStream({
      model: 'gemini-3-pro-preview', // 升級為 Pro 預覽版
      contents: { 
        parts: [...imageParts, textPart] 
      },
      config: {
        systemInstruction: "你是一位精通八字、紫微斗數、三元九運與現代職業戰略的頂尖玄學專家。你擅長將古老的東方智慧轉化為具備未來感、跨領域且符合現代趨勢的實戰建議。你的目標是幫助命主找到其在地球上的『原廠設定』並發揮最大天賦。解讀時請使用 Markdown 格式，表格必須清晰，語氣根據用戶要求調整。",
        temperature: 0.8,
        topP: 0.95,
        // 啟用思考模式 (Thinking Mode)
        thinkingConfig: {
          thinkingBudget: 32768
        }
      },
    });

    let fullText = "";
    for await (const chunk of responseStream) {
      const chunkText = (chunk as GenerateContentResponse).text || "";
      fullText += chunkText;
      if (onStream) onStream(chunkText);
    }

    return fullText;
  } catch (error) {
    console.error("Gemini Pro Analysis Error:", error);
    throw new Error("解讀過程中發生錯誤，可能與模型限制或網路有關，請稍後再試。");
  }
};

const fileToBase64 = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64String = (reader.result as string).split(',')[1];
      resolve(base64String);
    };
    reader.onerror = (error) => reject(error);
  });
};
