// built-in-chat/src/ChatHttpKernel.ts
// Browser-side chat kernel that uses Chrome's built-in AI via @built-in-ai/core
import { streamText } from "ai";
import { builtInAI } from "@built-in-ai/core";
export class ChatHttpKernel {
    constructor(opts = {}) {
        this.model = builtInAI();
        console.log("[ChatHttpKernel] Using Chrome built-in AI");
    }
    async send(prompt) {
        const availability = await this.model.availability();
        if (availability === "unavailable") {
            throw new Error("Browser does not support Chrome built-in AI.");
        }
        if (availability === "downloadable" || availability === "downloading") {
            await this.model.createSessionWithProgress((report) => {
                if (typeof window !== "undefined") {
                    window.dispatchEvent(new CustomEvent("builtinai:model-progress", { detail: report }));
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
        }
        return reply;
    }
}
