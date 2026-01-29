
import { GoogleGenAI, GenerateContentResponse } from "@google/genai";
import { ChartImage } from "../types";

export const analyzeCharts = async (
  images: ChartImage[],
  prompt: string,
  onStream?: (chunk: string) => void
): Promise<string> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  
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
      model: 'gemini-3-flash-preview', 
      contents: { 
        parts: [...imageParts, textPart] 
      },
      config: {
        systemInstruction: "你是一位精通八字與紫微的命理專家。請使用 Markdown 格式提供清晰的分析。回答應包含結構化表格與條列式建議，語氣專業且富有啟發性。",
        temperature: 0.7,
        topP: 0.9,
      },
    });

    let fullText = "";
    for await (const chunk of responseStream) {
      const chunkText = (chunk as GenerateContentResponse).text || "";
      fullText += chunkText;
      if (onStream) onStream(chunkText);
    }

    return fullText;
  } catch (error: any) {
    console.error("Gemini Flash Analysis Error:", error);
    if (error.message?.includes("429")) {
      throw new Error("配額已達上限，請稍候一分鐘再試，或檢查您的 API 計費設定。");
    }
    throw new Error("解讀過程中發生錯誤，請稍後再試。");
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
