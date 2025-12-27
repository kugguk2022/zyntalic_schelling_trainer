
import { TranslationConfig, TranslationResult } from "../types";

const API_BASE_URL = ""; // Relative path since we serve from same origin

export const performTranslation = async (
  text: string,
  config: TranslationConfig
): Promise<TranslationResult> => {
  const startTime = Date.now();

  try {
    // Map frontend engines to backend values
    let engine = "core";
    if (config.engine.includes("Transformer")) {
        engine = "transformer";
    } else if (config.engine.includes("Neural")) {
        engine = "chiasmus";
    } else if (config.engine.includes("Test Suite")) {
        engine = "test_suite";
    }

    const response = await fetch(`${API_BASE_URL}/translate`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            text: text,
            mirror_rate: config.mirror,
            engine: engine,
        }),
    });

    if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
    }

    const data = await response.json();
    const endTime = Date.now();
    
    // Backend returns { rows: [{ source, target, lemma, anchors, engine }] }
    // We need to map this to TranslationResult
    // For now, let's join all targets if multiple sentences
    
    // If rows is missing or empty, handle gracefully
    const rows = data.rows || [];
    const translatedText = rows.map((r: any) => r.target).join(" ");

    return {
      text: translatedText || "No translation generated.",
      latency: endTime - startTime,
      confidence: 1.0, // Backend doesn't give confidence yet
      detectedSentiment: "English" // Placeholder
    };
  } catch (error) {
    console.error("Translation Error:", error);
    throw new Error("Failed to connect to Zyntalic Local Engine.");
  }
};
