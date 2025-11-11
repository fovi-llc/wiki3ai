function render({ model, el }) {
    // Get accessor functions for traitlets
    let getPrompt = () => model.get("prompt");
    let getResponse = () => model.get("response");
    let getStatus = () => model.get("status");
    
    // Create status message
    let statusTA = document.createElement("textarea");
    statusTA.className = "status-message";
    statusTA.value = getStatus();
    model.on("change:status", () => {
        const status = getStatus();
        statusTA.value = status;
        // Set color based on status
        if (status.includes("Error") || status.includes("not available")) {
            statusTA.style.color = "#dc2626";
        } else if (status.includes("Generating") || status.includes("Creating")) {
            statusTA.style.color = "#2563eb";
        } else if (status.includes("Ready") || status.includes("received")) {
            statusTA.style.color = "#16a34a";
        } else {
            statusTA.style.color = "inherit";
        }
    });
    el.appendChild(statusTA);
    
    // Create prompt textarea
    let promptTA = document.createElement("textarea");
    promptTA.className = "prompt-input";
    promptTA.placeholder = "Enter your prompt here...";
    promptTA.rows = 3;
    promptTA.value = getPrompt();
    promptTA.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            model.set("prompt", promptTA.value);
            model.save_changes();
        }
    });
    el.appendChild(promptTA);
    
    // Create submit button
    let button = document.createElement("button");
    button.className = "submit-button";
    button.textContent = "Submit";
    button.addEventListener("click", () => {
        model.set("prompt", promptTA.value);
        model.save_changes();
    });
    el.appendChild(button);
    
    // Create response textarea
    let responseTA = document.createElement("textarea");
        responseTA.className = "response-box";
        responseTA.value = getResponse();
        model.on("change:response", () => {
        responseTA.value = getResponse();
    });
    el.appendChild(responseTA);
    
    // Initialize Chrome AI session (async but doesn't block render)
    let session = null;
    // (async () => {
    // try {
    //     model.set("status", "Initializing...");
    //     model.save_changes();
        
    //     if (!window.ai || !window.ai.languageModel) {
    //     model.set("status", "Chrome AI not available. Please enable chrome://flags/#prompt-api-for-gemini-nano");
    //     model.save_changes();
    //     button.disabled = true;
    //     return;
    //     }
        
    //     model.set("status", "Creating AI session...");
    //     model.save_changes();
    //     session = await window.ai.languageModel.create();
    //     model.set("status", "Ready! Enter a prompt and press Submit or Enter.");
    //     model.save_changes();
        
    // } catch (error) {
    //     model.set("status", `Error: ${error.message}`);
    //     model.save_changes();
    //     button.disabled = true;
    // }
    // })();
    
    // Handle prompt changes - call Chrome AI
    model.on("change:prompt", async () => {
        const promptText = getPrompt().trim();
        if (!promptText || !session) return;

        try {
            button.disabled = true;
            promptTA.disabled = true;
            
            model.set("status", "Generating response...");
            model.set("response", "");
            model.save_changes();
            
            const result = await session.prompt(promptText);
            
            model.set("response", result);
            model.set("status", "Response received! Enter another prompt.");
            model.save_changes();
            
        } catch (error) {
            model.set("response", `Error: ${error.message}`);
            model.set("status", "Error occurred. Please try again.");
            model.save_changes();
        } finally {
            button.disabled = false;
            promptTA.disabled = false;
        }
    });
}

export default { render };
