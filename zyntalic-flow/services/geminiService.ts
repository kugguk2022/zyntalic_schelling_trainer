
import { GoogleGenAI } from "@google/genai";
import { TranslationConfig, TranslationResult } from "../types";

export const performTranslation = async (
  text: string,
  config: TranslationConfig
): Promise<TranslationResult> => {
  const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
  const startTime = Date.now();

  const isAutoDetect = config.sourceLang === 'Auto-detect';

  const systemPrompt = `You are the Zyntalic Engine v0.3, a deterministic semantic translation system. 
  Your goal is to translate the input text to ${config.targetLang} using a ${config.engine} approach. 
  
  ${isAutoDetect 
    ? "The source language is unknown. You must first detect the source language of the input." 
    : `The source language is ${config.sourceLang}.`}
  
  The "Mirror" parameter is set to ${config.mirror}, which dictates the balance between literal accuracy (low) and semantic flow (high).
  
  Format your response exactly as a JSON object with these fields:
  {
    "translatedText": "the translation",
    "confidence": 0.95,
    "detectedSourceLanguage": "name of the language detected (only if Auto-detect was used)",
    "semanticNote": "brief explanation of semantic choices"
  }`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: text,
      config: {
        systemInstruction: systemPrompt,
        responseMimeType: "application/json",
        temperature: config.mirror,
      },
    });

    const data = JSON.parse(response.text || '{}');
    const endTime = Date.now();

    return {
      text: data.translatedText || "Translation failed to parse.",
      latency: endTime - startTime,
      confidence: data.confidence || 1.0,
      detectedSentiment: data.detectedSourceLanguage // Reusing field for display purposes in diagnostics if needed
    };
  } catch (error) {
    console.error("Translation Error:", error);
    throw new Error("The Zyntalic Engine encountered a processing error.");
  }
};
