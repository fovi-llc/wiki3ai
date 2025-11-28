// built-in-chat/src/ChatHttpKernel.ts
// Browser-side chat kernel that uses Chrome's built-in AI via @built-in-ai/core

import { streamText } from "ai";
import { builtInAI } from "@built-in-ai/core";

declare const window: any;

export interface ChatHttpKernelOptions {
  /**
   * Optional model identifier for chromeAI.
   * Defaults to the default Chrome built-in AI model.
   */
  model?: string;
}

export class ChatHttpKernel {
  private model: ReturnType<typeof builtInAI>;

  constructor(opts: ChatHttpKernelOptions = {}) {
    this.model = builtInAI();
    console.log("[ChatHttpKernel] Using Chrome built-in AI");
  }

  /**
   * Send a prompt and stream the response.
   * @param prompt The user prompt
   * @param onChunk Optional callback invoked for each chunk of text as it arrives
   * @returns The full response text
   */
  async send(prompt: string, onChunk?: (chunk: string) => void): Promise<string> {
    const availability = await this.model.availability();
    if (availability === "unavailable") {
      throw new Error("Browser does not support Chrome built-in AI.");
    }
    if (availability === "downloadable" || availability === "downloading") {
      await this.model.createSessionWithProgress((report: any) => {
        if (typeof window !== "undefined") {
          window.dispatchEvent(
            new CustomEvent("builtinai:model-progress", { detail: report })
          );
        }
      });
    }

    const result = await streamText({
      model: this.model,
      messages: [{ role: "user", content: prompt }],
    });

    let reply = "";
    for await (const chunk of result.textStream) {
      reply += chunk;
      if (onChunk) {
        onChunk(chunk);
      }
    }
    return reply;
  }
}

