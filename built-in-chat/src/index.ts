import { JupyterFrontEnd, JupyterFrontEndPlugin } from "@jupyterlab/application";
import { BUILTIN_AI_MODELS, DEFAULT_BUILTIN_AI_MODEL } from "./models.js";

import { BuiltInChatKernel } from "./kernel.js";

console.log("[built-in-chat] entrypoint loaded");

declare global {
  interface Window {
    builtinAIModelId?: string;
    __JUPYTERLITE_SHARED_SCOPE__?: Record<string, unknown>;
    _JUPYTERLAB?: Record<string, any>;
  }
}

/**
 * JupyterLite / JupyterLab plugin that registers our Chrome built-in AI chat kernel.
 */
const builtInChatKernelPlugin: JupyterFrontEndPlugin<void> = {
  id: "@wiki3-ai/built-in-chat:plugin",
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log("[built-in-chat] Activating plugin");

    // Grab kernelspecs from the app's serviceManager
    const anyApp = app as any;
    const kernelspecs = anyApp.serviceManager?.kernelspecs;

    if (!kernelspecs || typeof kernelspecs.register !== "function") {
      console.warn(
        "[built-in-chat] kernelspecs.register is not available; kernel will not be registered.",
        kernelspecs
      );
      return;
    }

    kernelspecs.register({
      id: "built-in-chat",
      spec: {
        name: "built-in-chat",
        display_name: "Built-in AI Chat",
        language: "python", // purely cosmetic; syntax highlighting
        argv: [],
        resources: {}
      },
      create: (options: any) => {
        console.log("[built-in-chat] Creating BuiltInChatKernel instance", options);
        return new BuiltInChatKernel(options);
      }
    });

    console.log("[built-in-chat] Kernel spec 'built-in-chat' registered");

    // --- Progress bar for model loading ---
    if (typeof document !== "undefined") {
      const bar = document.createElement("div");
      bar.style.position = "fixed";
      bar.style.top = "8px";
      bar.style.right = "8px";
      bar.style.zIndex = "9999";
      bar.style.padding = "4px 8px";
      bar.style.background = "rgba(0,0,0,0.7)";
      bar.style.color = "#fff";
      bar.style.fontSize = "12px";
      bar.style.borderRadius = "4px";
      bar.style.display = "flex";
      bar.style.gap = "4px";
      bar.style.alignItems = "center";

      const label = document.createElement("span");
      label.textContent = "Built-in AI:";
      bar.appendChild(label);

      const progress = document.createElement("progress");
      progress.max = 1;
      progress.value = 0;
      progress.style.width = "120px";
      progress.style.display = "none";
      bar.appendChild(progress);

      const status = document.createElement("span");
      status.textContent = "";
      bar.appendChild(status);

      window.addEventListener("builtinai:model-progress", (ev: any) => {
        const { progress: p, text } = ev.detail;
        progress.style.display = p > 0 && p < 1 ? "inline-block" : "none";
        progress.value = p ?? 0;
        status.textContent = text ?? "";
      });

      document.body.appendChild(bar);
    }
  }
};

const plugins: JupyterFrontEndPlugin<any>[] = [builtInChatKernelPlugin];

export default plugins;

// --- manual MF shim for static usage ---
if (typeof window !== "undefined") {
  const scope = "@wiki3-ai/built-in-chat";
  const moduleFactories: Record<string, () => any> = {
    "./index": () => ({ default: plugins }),
    "./extension": () => ({ default: plugins })
  };

  window._JUPYTERLAB = window._JUPYTERLAB || {};

  if (!window._JUPYTERLAB[scope]) {
    window._JUPYTERLAB[scope] = {
      get: (module: string) => {
        const factory = moduleFactories[module];
        if (!factory) {
          return Promise.reject(new Error(`[built-in-chat] Unknown module: ${module}`));
        }
        return Promise.resolve(factory);
      },
      init: (shareScope: Record<string, unknown> | undefined) => {
        const scopeData = shareScope ?? {};
        const globalShare = window.__JUPYTERLITE_SHARED_SCOPE__ ||= {};
        Object.assign(globalShare, scopeData);
        console.log("[built-in-chat] Module federation shim init() with shared scope keys", Object.keys(scopeData));
        return Promise.resolve();
      }
    };

    console.log(`[built-in-chat] Registered manual Module Federation shim on window._JUPYTERLAB scope='${scope}'`);
  }
}
