export interface ChatHttpKernelOptions {
    /**
     * Optional model identifier for webLLM.
     * Defaults to a small, fast instruction-tuned model.
     */
    model?: string;
}
export declare class ChatHttpKernel {
    private modelName;
    private model;
    constructor(opts?: ChatHttpKernelOptions);
    send(prompt: string): Promise<string>;
}
