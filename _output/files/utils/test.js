function render({ model, el }) {
    let getPrompt = () => model.get("prompt");
    let promptTextArea = document.createElement("textarea");
    promptTextArea.value = "Prompt";
    promptTextArea.addEventListener("keydown", (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent the default action (adding a new line)
        console.log('Enter pressed without Shift. Performing action...');
        model.set("prompt", promptTextArea.value);
        model.save_changes();        
    }
    });
    el.appendChild(promptTextArea);
    let getResult = () => model.get("result");
    let resultTextArea = document.createElement("textarea");
    resultTextArea.value = getResult();
    model.on("change:result", () => {
        resultTextArea.value = model.get("result");
    });
    model.on("change:prompt", () => {
        model.set("result", getPrompt());
    });
    el.appendChild(resultTextArea);
    let getCount = () => model.get("count");
        let button = document.createElement("button");
        button.classList.add("counter-button");
        button.innerHTML = `count is ${getCount()}`;
        button.addEventListener("click", () => {
        model.set("count", getCount() + 1);
        model.set("prompt", promptTextArea.value);        
        model.save_changes();
    });
    model.on("change:count", () => {
        button.innerHTML = `count is ${getCount()}`;
    });
    el.appendChild(button);
}

export default { render };
