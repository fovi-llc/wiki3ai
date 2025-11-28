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
    send(prompt: string): Promise<string>;
}
