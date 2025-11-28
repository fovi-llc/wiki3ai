export interface ChatHttpKernelOptions {
    /**
     * Optional model identifier for chromeAI.
     * Defaults to the default Chrome built-in AI model.
     */
    model?: string;
}
export declare class ChatHttpKernel {
    private model;
    constructor(opts?: ChatHttpKernelOptions);
    /**
     * Send a prompt and stream the response.
     * @param prompt The user prompt
     * @param onChunk Optional callback invoked for each chunk of text as it arrives
     * @returns The full response text
     */
    send(prompt: string, onChunk?: (chunk: string) => void): Promise<string>;
}
