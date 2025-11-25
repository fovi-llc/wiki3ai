import { JupyterFrontEndPlugin } from "@jupyterlab/application";
declare global {
    interface Window {
        webllmModelId?: string;
        __JUPYTERLITE_SHARED_SCOPE__?: Record<string, unknown>;
        _JUPYTERLAB?: Record<string, any>;
    }
}
declare const plugins: JupyterFrontEndPlugin<any>[];
export default plugins;
