import { JupyterFrontEndPlugin } from "@jupyterlab/application";
declare global {
    interface Window {
        webllmModelId?: string;
    }
}
declare const plugins: JupyterFrontEndPlugin<any>[];
export default plugins;
