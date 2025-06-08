/**
 * WebLLM Extension for JupyterLite
 * Provides WebLLM functionality in Pyodide environment
 */

// Load WebLLM CDN
const script = document.createElement('script');
script.src = 'https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm@0.2.46/lib/index.min.js';
script.onload = function() {
    console.log('WebLLM loaded successfully');
    // Make WebLLM available globally
    window.WebLLM = window.tvmjs.webllm;
};
script.onerror = function() {
    console.error('Failed to load WebLLM');
};
document.head.appendChild(script);

// JupyterLab extension definition
const extension = {
    id: 'webllm-extension',
    autoStart: true,
    activate: function(app) {
        console.log('WebLLM extension activated');
        
        // Add WebLLM to Pyodide when kernel starts
        app.serviceManager.kernels.kernelStarted.connect((sender, args) => {
            const kernel = args.kernel;
            if (kernel.name === 'python') {
                // Execute initialization code in Pyodide
                kernel.requestExecute({
                    code: `
# WebLLM initialization for Pyodide
import js
import asyncio
from pyodide.ffi import create_proxy

class WebLLMHelper:
    def __init__(self):
        self.engine = None
        self.model_loaded = False
    
    async def initialize(self, model_id="Llama-3.2-1B-Instruct-q4f16_1-MLC"):
        """Initialize WebLLM engine with specified model"""
        try:
            # Wait for WebLLM to be available
            while not hasattr(js, 'WebLLM'):
                await asyncio.sleep(0.1)
            
            # Create engine
            self.engine = await js.WebLLM.CreateMLCEngine(model_id)
            self.model_loaded = True
            print(f"WebLLM initialized with model: {model_id}")
            return True
        except Exception as e:
            print(f"Failed to initialize WebLLM: {e}")
            return False
    
    async def chat(self, message, max_tokens=512):
        """Send a chat message to WebLLM"""
        if not self.model_loaded:
            return "WebLLM not initialized. Call await webllm.initialize() first."
        
        try:
            messages = [{"role": "user", "content": message}]
            response = await self.engine.chat.completions.create(
                messages=messages,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"
    
    async def generate(self, prompt, max_tokens=512):
        """Generate text from a prompt"""
        if not self.model_loaded:
            return "WebLLM not initialized. Call await webllm.initialize() first."
        
        try:
            response = await self.engine.completions.create(
                prompt=prompt,
                max_tokens=max_tokens
            )
            return response.choices[0].text
        except Exception as e:
            return f"Error: {e}"

# Create global WebLLM helper instance
webllm = WebLLMHelper()
print("WebLLM helper available as 'webllm'")
print("Usage:")
print("  await webllm.initialize()  # Initialize with default model")
print("  await webllm.chat('Hello!')  # Chat with the model")
print("  await webllm.generate('Complete this: ')  # Generate text")
`
                });
            }
        });
    }
};

// Export for JupyterLab
if (typeof module !== 'undefined' && module.exports) {
    module.exports = extension;
} else if (typeof window !== 'undefined') {
    window.webllmExtension = extension;
}
