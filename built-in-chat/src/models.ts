// built-in-chat/src/models.ts
// Chrome's built-in AI model configuration
// Unlike WebLLM, Chrome's built-in AI uses a single model provided by the browser

// Chrome's built-in AI currently supports one model
export const BUILTIN_AI_MODELS: string[] = ["chrome-built-in-ai"];

// Default model for Chrome's built-in AI
export const DEFAULT_BUILTIN_AI_MODEL: string = "chrome-built-in-ai";

// Validation helper: check if a string is one of the known model IDs
export function isValidBuiltinAIModel(id: string): boolean {
  return BUILTIN_AI_MODELS.includes(id);
}

