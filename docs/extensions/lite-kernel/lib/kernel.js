// lite-kernel/src/kernel.ts
import { BaseKernel } from "@jupyterlite/kernel";
import { ChatHttpKernel } from "./ChatHttpKernel.js";
export class HttpLiteKernel extends BaseKernel {
    constructor(options) {
        super(options);
        const model = options.model;
        this.chat = new ChatHttpKernel({ model });
    }
    async executeRequest(content) {
        const code = String(content.code ?? "");
        try {
            const reply = await this.chat.send(code);
            this.publishExecuteResult({
                data: { "text/plain": reply },
                metadata: {},
                execution_count: this.executionCount,
            }, this.parentHeader);
            return {
                status: "ok",
                execution_count: this.executionCount,
                payload: [],
                user_expressions: {},
            };
        }
        catch (err) {
            const message = err?.message ?? String(err);
            this.publishExecuteError({
                ename: "Error",
                evalue: message,
                traceback: [],
            }, this.parentHeader);
            return {
                status: "error",
                execution_count: this.executionCount,
                ename: "Error",
                evalue: message,
                traceback: [],
            };
        }
    }
    async kernelInfoRequest() {
        return {
            status: "ok",
            protocol_version: "5.3",
            implementation: "http-lite-kernel",
            implementation_version: "0.1.0",
            language_info: {
                name: "markdown",
                version: "0.0.0",
                mimetype: "text/markdown",
                file_extension: ".md",
            },
            banner: "HTTP-backed LLM chat kernel",
            help_links: [],
        };
    }
    async completeRequest(content) {
        return {
            status: "ok",
            matches: [],
            cursor_start: content.cursor_pos ?? 0,
            cursor_end: content.cursor_pos ?? 0,
            metadata: {},
        };
    }
    async inspectRequest(_content) {
        return {
            status: "ok",
            found: false,
            data: {},
            metadata: {},
        };
    }
    async isCompleteRequest(_content) {
        return {
            status: "complete",
            indent: "",
        };
    }
    async commInfoRequest(_content) {
        return {
            status: "ok",
            comms: {},
        };
    }
    async historyRequest(_content) {
        return {
            status: "ok",
            history: [],
        };
    }
    async shutdownRequest(_content) {
        return {
            status: "ok",
            restart: false,
        };
    }
    async inputReply(_content) { }
    async commOpen(_content) { }
    async commMsg(_content) { }
    async commClose(_content) { }
}
export function createHttpLiteKernel(options) {
    return new HttpLiteKernel(options);
}
