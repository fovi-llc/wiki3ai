"use strict";
// lite-kernel/src/ChatHttpKernel.ts
// Browser-side chat kernel that talks directly to a local WebLLM model
// via the Vercel AI SDK + @built-in-ai/web-llm.
Object.defineProperty(exports, "__esModule", { value: true });
exports.ChatHttpKernel = void 0;
const ai_1 = require("ai");
const web_llm_1 = require("@built-in-ai/web-llm");
class ChatHttpKernel {
    constructor(opts = {}) {
        const globalModel = typeof window !== "undefined" ? window.webllmModelId : undefined;
        this.modelName = opts.model ?? globalModel ?? "Llama-3.2-3B-Instruct-q4f16_1-MLC";
        this.model = (0, web_llm_1.webLLM)(this.modelName, {
            initProgressCallback: (report) => {
                if (typeof window !== "undefined") {
                    window.dispatchEvent(new CustomEvent("webllm:model-progress", { detail: report }));
                }
            },
        });
        console.log("[ChatHttpKernel] Using WebLLM model:", this.modelName);
    }
    async send(prompt) {
        const availability = await this.model.availability();
        if (availability === "unavailable") {
            throw new Error("Browser does not support WebLLM / WebGPU.");
        }
        if (availability === "downloadable" || availability === "downloading") {
            await this.model.createSessionWithProgress((report) => {
                if (typeof window !== "undefined") {
                    window.dispatchEvent(new CustomEvent("webllm:model-progress", { detail: report }));
                }
            });
        }
        const result = await (0, ai_1.streamText)({
            model: this.model,
            messages: [{ role: "user", content: prompt }],
        });
        let reply = "";
        for await (const chunk of result.textStream) {
            reply += chunk;
        }
        return reply;
    }
}
exports.ChatHttpKernel = ChatHttpKernel;
