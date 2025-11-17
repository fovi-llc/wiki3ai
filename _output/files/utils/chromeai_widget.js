function render({ model, el }) {
    const getPrompt = () => model.get("prompt") ?? "";
    const getResponse = () => model.get("response") ?? "";
    const getStatus = () => model.get("status") ?? "";

    const setStatus = (value) => {
        model.set("status", value);
        model.save_changes();
    };

    const setResponse = (value) => {
        model.set("response", value);
        model.save_changes();
    };

    const container = document.createElement("div");
    container.className = "chrome-ai-container";
    el.appendChild(container);

    const statusTA = document.createElement("textarea");
    statusTA.className = "status-message";
    statusTA.readOnly = true;
    statusTA.value = getStatus();
    model.on("change:status", () => {
        const status = getStatus();
        statusTA.value = status;
        if (status.includes("Error") || status.includes("not available")) {
            statusTA.style.color = "#dc2626";
        } else if (status.includes("Generating") || status.includes("Preparing")) {
            statusTA.style.color = "#2563eb";
        } else if (status.includes("Ready") || status.includes("received")) {
            statusTA.style.color = "#16a34a";
        } else {
            statusTA.style.color = "inherit";
        }
    });
    container.appendChild(statusTA);

    const promptTA = document.createElement("textarea");
    promptTA.className = "prompt-input";
    promptTA.placeholder = "Enter your prompt here...";
    promptTA.rows = 3;
    promptTA.value = getPrompt();
    container.appendChild(promptTA);

    const button = document.createElement("button");
    button.className = "submit-button";
    button.textContent = "Submit";
    container.appendChild(button);

    const responseTA = document.createElement("textarea");
    responseTA.className = "response-box";
    responseTA.readOnly = true;
    responseTA.value = getResponse();
    model.on("change:response", () => {
        responseTA.value = getResponse();
    });
    container.appendChild(responseTA);

    const languageModelAPI = globalThis.LanguageModel ?? globalThis.ai?.languageModel ?? null;
    let session = null;
    let sessionPromise = null;
    let currentPromptController = null;
    let suppressNextPrompt = false;
    let pendingPromptFromModel = null;
    let lastPromptText = "";

    const ensureSession = async () => {
        if (session) {
            return session;
        }
        if (!languageModelAPI) {
            setStatus("Chrome AI not available. Please enable chrome://flags/#prompt-api-for-gemini-nano");
            button.disabled = true;
            promptTA.disabled = true;
            return null;
        }
        if (sessionPromise) {
            return sessionPromise;
        }

        sessionPromise = (async () => {
            try {
                setStatus("Preparing on-device model...");
                const availability = await languageModelAPI.availability();
                if (availability === "unavailable") {
                    throw new Error("Model unavailable on this device");
                }
                if (availability === "downloadable" || availability === "downloading") {
                    setStatus("Downloading model (this can take a few minutes)...");
                }

                const monitor = (monitoring) => {
                    monitoring.addEventListener("downloadprogress", (event) => {
                        if (typeof event.loaded === "number") {
                            const progress = Math.round(event.loaded * 100);
                            setStatus(`Downloading model... ${progress}%`);
                        }
                    });
                };

                const createdSession = await languageModelAPI.create({ monitor });
                session = createdSession;
                setStatus("Ready! Enter a prompt and press Submit or Enter.");
                button.disabled = false;
                promptTA.disabled = false;
                return createdSession;
            } catch (error) {
                sessionPromise = null;
                setStatus(`Error initializing model: ${error.message}`);
                button.disabled = true;
                promptTA.disabled = true;
                return null;
            }
        })();

        sessionPromise.then((created) => {
            if (!created) {
                session = null;
            }
        });

        return sessionPromise;
    };

    const extractChunkText = (chunk) => {
        if (typeof chunk === "string") {
            return chunk;
        }
        if (chunk && typeof chunk === "object") {
            if (typeof chunk.text === "string") {
                return chunk.text;
            }
            if (typeof chunk.delta === "string") {
                return chunk.delta;
            }
            if (typeof chunk.value === "string") {
                return chunk.value;
            }
            if (Array.isArray(chunk.content)) {
                return chunk.content.map((part) => extractChunkText(part)).join("");
            }
        }
        return "";
    };

    const runPrompt = async (promptText) => {
        const activeSession = await ensureSession();
        if (!promptText || !activeSession) {
            return;
        }
        lastPromptText = promptText;

        if (currentPromptController) {
            currentPromptController.abort();
        }

        const controller = new AbortController();
        currentPromptController = controller;

        button.disabled = true;
        promptTA.disabled = true;
        setStatus("Generating response...");
        setResponse("");
        responseTA.value = "";

        try {
            const stream = activeSession.promptStreaming(promptText, {
                signal: controller.signal,
            });

            let combined = "";
            for await (const chunk of stream) {
                if (controller.signal.aborted) {
                    break;
                }
                const chunkText = extractChunkText(chunk);
                if (!chunkText) {
                    continue;
                }
                combined += chunkText;
                responseTA.value = combined;
            }

            if (!controller.signal.aborted) {
                setResponse(responseTA.value);
                setStatus("Response received! Enter another prompt.");
            } else {
                setStatus("Generation cancelled.");
            }
        } catch (error) {
            if (error.name === "AbortError") {
                setStatus("Generation cancelled.");
            } else {
                setResponse(`Error: ${error.message}`);
                setStatus("Error occurred. Please try again.");
            }
        } finally {
            if (currentPromptController === controller) {
                currentPromptController = null;
            }
            button.disabled = false;
            promptTA.disabled = false;
        }
    };

    button.addEventListener("click", async () => {
        const promptText = promptTA.value.trim();
        if (!promptText) {
            return;
        }
        suppressNextPrompt = true;
        model.set("prompt", promptTA.value);
        model.save_changes();
        let queuedPrompt = null;
        try {
            await runPrompt(promptText);
        } finally {
            suppressNextPrompt = false;
            queuedPrompt = pendingPromptFromModel;
            pendingPromptFromModel = null;
        }
        if (queuedPrompt) {
            const queuedText = queuedPrompt.trim();
            if (queuedText && queuedText !== lastPromptText) {
                await runPrompt(queuedText);
            }
        }
    });

    promptTA.addEventListener("keydown", async (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            button.click();
        }
    });

    model.on("change:prompt", async () => {
        if (suppressNextPrompt) {
            pendingPromptFromModel = getPrompt();
            return;
        }
        const promptValue = getPrompt();
        promptTA.value = promptValue;
        const promptText = promptValue.trim();
        if (!promptText) {
            return;
        }
        await runPrompt(promptText);
    });

    if (!getStatus()) {
        setStatus("Initializing Chrome AI widget...");
    } else {
        statusTA.value = getStatus();
    }

    if (getResponse()) {
        responseTA.value = getResponse();
    }
}

export default { render };
