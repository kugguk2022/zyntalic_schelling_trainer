
export enum TranslationEngine {
  SEMANTIC = 'Transformer (Semantic)',
  NEURAL = 'Neural (Direct)',
  LITERAL = 'Deterministic (Literal)'
}

export interface TranslationConfig {
  engine: TranslationEngine;
  mirror: number;
  sourceLang: string;
  targetLang: string;
}

export interface TranslationResult {
  text: string;
  detectedSentiment?: string;
  latency: number;
  confidence: number;
}
