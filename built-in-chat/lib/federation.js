// built-in-chat/src/federation.ts
// Module Federation container for JupyterLite
import { streamText } from "ai";
import { builtInAI } from "@built-in-ai/core";
console.log("[built-in-chat/federation] Setting up Module Federation container");
const scope = "@wiki3-ai/built-in-chat";
let sharedScope = null;
// Helper to get a module from the shared scope
async function importShared(pkg) {
    if (!sharedScope) {
        // Fallback to global webpack share scope if available
        // @ts-ignore
        if (window.__webpack_share_scopes__ && window.__webpack_share_scopes__.default) {
            console.warn(`[built-in-chat] Using global __webpack_share_scopes__.default for ${pkg}`);
            // @ts-ignore
            sharedScope = window.__webpack_share_scopes__.default;
        }
        else {
            throw new Error(`[built-in-chat] Shared scope not initialized when requesting ${pkg}`);
        }
    }
    const versions = sharedScope[pkg];
    if (!versions) {
        throw new Error(`[built-in-chat] Shared module ${pkg} not found in shared scope. Available: ${Object.keys(sharedScope)}`);
    }
    const versionKeys = Object.keys(versions);
    if (versionKeys.length === 0) {
        throw new Error(`[built-in-chat] No versions available for ${pkg}`);
    }
    // Pick the first available version
    const version = versions[versionKeys[0]];
    const factory = version?.get;
    if (typeof factory !== "function") {
        throw new Error(`[built-in-chat] Module ${pkg} has no factory function`);
    }
    // Factory might return a Promise or the module directly
    let result = factory();
    // If it's a promise, await it
    if (result && typeof result.then === 'function') {
        result = await result;
    }
    // If result is a function (Webpack module wrapper), call it to get the actual exports
    if (typeof result === 'function') {
        result = result();
    }
    console.log(`[built-in-chat] Loaded ${pkg}:`, result);
    return result;
}
// Module Federation container API
const container = {
    init: (scope) => {
        console.log("[built-in-chat/federation] init() called, storing shared scope");
        sharedScope = scope;
        return Promise.resolve();
    },
    get: async (module) => {
        console.log("[built-in-chat/federation] get() called for module:", module);
        console.log("[built-in-chat/federation] This means JupyterLite is requesting our plugin!");
        // JupyterLite may request either "./index" or "./extension"
        if (module === "./index" || module === "./extension") {
            // Lazy-load our plugin module, which will pull from shared scope
            return async () => {
                console.log("[built-in-chat/federation] ===== LOADING PLUGIN MODULE =====");
                console.log("[built-in-chat/federation] Loading plugins from shared scope...");
                // Import JupyterLab/JupyterLite modules from shared scope
                const { BaseKernel, IKernelSpecs } = await importShared('@jupyterlite/kernel');
                const { Widget } = await importShared('@lumino/widgets');
                const { ReactWidget } = await importShared('@jupyterlab/apputils');
                const React = await importShared('react');
                const { HTMLSelect } = await importShared('@jupyterlab/ui-components');
                console.log("[built-in-chat/federation] Got BaseKernel from shared scope:", BaseKernel);
                // Define Chrome built-in AI Chat kernel inline (browser-only)
                class ChatHttpKernel {
                    constructor(opts = {}) {
                        this.model = builtInAI();
                        console.log("[ChatHttpKernel] Using Chrome built-in AI");
                    }
                    async send(prompt, onChunk) {
                        console.log("[ChatHttpKernel] Sending prompt to Chrome built-in AI:", prompt);
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
                            if (onChunk) {
                                onChunk(chunk);
                            }
                        }
                        console.log("[ChatHttpKernel] Got reply from Chrome built-in AI:", reply);
                        return reply;
                    }
                }
                // Define BuiltInChatKernel extending BaseKernel
                class BuiltInChatKernel extends BaseKernel {
                    constructor(options) {
                        super(options);
                        const model = options.model;
                        this.chat = new ChatHttpKernel({ model });
                    }
                    async executeRequest(content) {
                        const code = String(content.code ?? "");
                        try {
                            // Stream each chunk as it arrives using the stream() method for stdout
                            await this.chat.send(code, (chunk) => {
                                // @ts-ignore
                                this.stream({ name: "stdout", text: chunk }, 
                                // @ts-ignore
                                this.parentHeader);
                            });
                            return {
                                status: "ok",
                                // @ts-ignore
                                execution_count: this.executionCount,
                                payload: [],
                                user_expressions: {},
                            };
                        }
                        catch (err) {
                            const message = err?.message ?? String(err);
                            // @ts-ignore
                            this.publishExecuteError({
                                ename: "Error",
                                evalue: message,
                                traceback: [],
                            }, 
                            // @ts-ignore
                            this.parentHeader);
                            return {
                                status: "error",
                                // @ts-ignore
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
                            implementation: "built-in-chat-kernel",
                            implementation_version: "0.1.0",
                            language_info: {
                                name: "markdown",
                                version: "0.0.0",
                                mimetype: "text/markdown",
                                file_extension: ".md",
                            },
                            banner: "Chrome built-in AI chat kernel",
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
                        return { status: "ok", found: false, data: {}, metadata: {} };
                    }
                    async isCompleteRequest(_content) {
                        return { status: "complete", indent: "" };
                    }
                    async commInfoRequest(_content) {
                        return { status: "ok", comms: {} };
                    }
                    async historyRequest(_content) {
                        return { status: "ok", history: [] };
                    }
                    async shutdownRequest(_content) {
                        return { status: "ok", restart: false };
                    }
                    async inputReply(_content) { }
                    async commOpen(_content) { }
                    async commMsg(_content) { }
                    async commClose(_content) { }
                }
                // Define and return the plugin
                const builtInChatKernelPlugin = {
                    id: "@wiki3-ai/built-in-chat:plugin",
                    autoStart: true,
                    // Match the official JupyterLite custom kernel pattern:
                    // https://jupyterlite.readthedocs.io/en/latest/howto/extensions/kernel.html
                    requires: [IKernelSpecs],
                    activate: (app, kernelspecs) => {
                        console.log("[built-in-chat] ===== ACTIVATE FUNCTION CALLED =====");
                        console.log("[built-in-chat] JupyterLab app:", app);
                        console.log("[built-in-chat] kernelspecs service:", kernelspecs);
                        if (!kernelspecs || typeof kernelspecs.register !== "function") {
                            console.error("[built-in-chat] ERROR: kernelspecs.register not available!");
                            return;
                        }
                        try {
                            kernelspecs.register({
                                spec: {
                                    name: "built-in-chat",
                                    display_name: "Built-in AI Chat",
                                    language: "python",
                                    argv: [],
                                    resources: {},
                                },
                                create: async (options) => {
                                    console.log("[built-in-chat] Creating BuiltInChatKernel instance", options);
                                    return new BuiltInChatKernel(options);
                                },
                            });
                            console.log("[built-in-chat] ===== KERNEL REGISTERED SUCCESSFULLY =====");
                            console.log("[built-in-chat] Kernel name: built-in-chat");
                            console.log("[built-in-chat] Display name: Built-in AI Chat");
                        }
                        catch (error) {
                            console.error("[built-in-chat] ===== REGISTRATION ERROR =====", error);
                        }
                        if (typeof document !== "undefined") {
                            // Progress indicator for Chrome built-in AI
                            window.addEventListener("builtinai:model-progress", (ev) => {
                                const { progress: p, text } = ev.detail;
                                console.log(`[built-in-chat] Model progress: ${text} (${Math.round((p ?? 0) * 100)}%)`);
                            });
                        }
                    },
                };
                const plugins = [builtInChatKernelPlugin];
                console.log("[built-in-chat/federation] ===== PLUGIN CREATED SUCCESSFULLY =====");
                console.log("[built-in-chat/federation] Plugin ID:", builtInChatKernelPlugin.id);
                console.log("[built-in-chat/federation] Plugin autoStart:", builtInChatKernelPlugin.autoStart);
                console.log("[built-in-chat/federation] Returning plugins array:", plugins);
                // IMPORTANT: Shape the exports like a real federated ES module
                // so JupyterLite's loader sees our plugins. It checks for
                // `__esModule` and then reads `.default`.
                const moduleExports = {
                    __esModule: true,
                    default: plugins
                };
                return moduleExports;
            };
        }
        throw new Error(`[built-in-chat/federation] Unknown module: ${module}`);
    }
};
// Register the container
window._JUPYTERLAB = window._JUPYTERLAB || {};
window._JUPYTERLAB[scope] = container;
console.log("[built-in-chat/federation] Registered Module Federation container for scope:", scope);
