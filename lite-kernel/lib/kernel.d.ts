import { BaseKernel, IKernel } from "@jupyterlite/kernel";
type KernelOptions = IKernel.IOptions & {
    /**
     * Optional WebLLM model identifier to pass through to ChatHttpKernel.
     */
    model?: string;
};
export declare class HttpLiteKernel extends BaseKernel {
    private chat;
    constructor(options: KernelOptions);
    executeRequest(content: any): Promise<any>;
    kernelInfoRequest(): Promise<any>;
    completeRequest(content: any): Promise<any>;
    inspectRequest(_content: any): Promise<any>;
    isCompleteRequest(_content: any): Promise<any>;
    commInfoRequest(_content: any): Promise<any>;
    historyRequest(_content: any): Promise<any>;
    shutdownRequest(_content: any): Promise<any>;
    inputReply(_content: any): Promise<void>;
    commOpen(_content: any): Promise<void>;
    commMsg(_content: any): Promise<void>;
    commClose(_content: any): Promise<void>;
}
export declare function createHttpLiteKernel(options: KernelOptions): IKernel;
export {};
