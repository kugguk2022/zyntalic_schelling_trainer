
import { TranslationConfig, TranslationResult } from "../types";

const API_BASE_URL = ""; // Relative to same-origin backend

export const performGeminiTranslation = async (
  text: string,
  config: TranslationConfig
): Promise<TranslationResult> => {
  const startTime = Date.now();

  try {
    const response = await fetch(`${API_BASE_URL}/translate/gemini`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text,
        mirror_rate: config.mirror,
        target_lang: config.targetLang,
        source_lang: config.sourceLang,
        engine: config.engine,
      }),
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      const detail = (payload as any).detail || response.statusText;
      throw new Error(`Gemini proxy error: ${detail}`);
    }

    const data = await response.json();
    const endTime = Date.now();

    return {
      text: data.translated_text || "No translation generated.",
      latency: endTime - startTime,
      confidence: data.confidence ?? 1.0,
      detectedSentiment: data.detected_source_language,
    };
  } catch (error) {
    console.error("Gemini Translation Error:", error);
    throw new Error("Failed to connect to Gemini proxy.");
  }
};
