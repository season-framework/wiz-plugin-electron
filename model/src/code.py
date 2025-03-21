class Model:
    ESBUILD = """const fs = require('fs');
const pug = require('pug');

if (process.argv.length > 2) {
    for (let i = 2 ; i < process.argv.length ; i++) {
        const target = process.argv[i];
        const targetpath = target + '.pug';
        const savepath = target + '.html';
        const compiledFunction = pug.compileFile(targetpath);
        fs.writeFileSync(savepath, compiledFunction(), "utf8")
    }
} else {
    const NgcEsbuild = require('ngc-esbuild');
    new NgcEsbuild({
        minify: true,
        open: false,
        serve: false,
        watch: false
    }).resolve.then((result) => {
        process.exit(1);
    });
}
    """

    ENV = """export const environment = {
    production: true
    };"""

    TSCONFIG = """{
    "compileOnSave": false,
    "compilerOptions": {
        "baseUrl": "./",
        "outDir": "./dist/out-tsc",
        "forceConsistentCasingInFileNames": true,
        "strict": true,
        "noImplicitOverride": true,
        "noPropertyAccessFromIndexSignature": true,
        "noImplicitReturns": true,
        "noFallthroughCasesInSwitch": true,
        "sourceMap": true,
        "declaration": false,
        "downlevelIteration": true,
        "experimentalDecorators": true,
        "moduleResolution": "node",
        "importHelpers": true,
        "target": "ES2022",
        "module": "ES2022",
        "useDefineForClassFields": false,
        "lib": [
        "ES2022",
        "dom"
        ]
    },
    "angularCompilerOptions": {
        "enableI18nLegacyMessageIdFormat": false,
        "strictInjectionParameters": true,
        "strictInputAccessModifiers": true,
        "strictTemplates": true
    }
    }
    """

    STYLES = '@import "styles/styles"'

    DOTENV = """DATA_PATH='.wetest'
WIDTH=960
HEIGHT=640
APP_TITLE='WIZ ELECTRON APPLICATION'
API_BASE=''
    """

    ELECTRON = """import path from "path";
import fs from "fs";
import isDev from "electron-is-dev";
import { fileURLToPath } from "url";

const dirname = fileURLToPath(new URL(".", import.meta.url));
process.env.WIZ_ELECTRON_IS_DEV = isDev;
process.env['ELECTRON_DISABLE_SECURITY_WARNINGS'] = 'true';

import {
    dataPath,
    indexPath,
    appPath,
    assetsPath,
} from "./paths.js";

import {
    app, screen, BrowserWindow, ipcMain, shell,
    Tray, Menu, nativeImage,
    Notification, dialog,
    // globalShortcut,
} from "electron";
import electron from "electron";

let win = null;
let tray = null;
const size = {
    width: process.env.WIDTH,
    height: process.env.HEIGHT,
};
let pos = null;

const toggleWindow = () => {
    if (win.isVisible()) {
        app.hide();
    }
    else {
        win.setVisibleOnAllWorkspaces(true);
        win.show();
    }
}

const notice = (title, body, cb = null) => {
    const obj = new Notification({
        title,
        body,
    });
    if (cb) {
        obj.addListener("click", toggleWindow);
    }
    obj.show();
}

const confirmClose = async e => {
    try {
        e.preventDefault();
    } catch { }
    const { response } = await dialog.showMessageBox(win, {
        type: "question",
        title: "Confirm",
        message: "Are you sure that you want to close this window?",
        buttons: ["Yes", "No"],
    });

    if (response === 0) {
        app.quit();
    }
}

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        // Someone tried to run a second instance, we should focus our window.
        if (win) {
            if (win.isMinimized() || !win.isVisible()) {
                win.show();
            }
            win.focus();
        }
    });
}

async function createWindow() {
    if (!fs.existsSync(dataPath)) {
        fs.mkdirSync(dataPath);
    }
    if (!pos) {
        const { bounds } = screen.getPrimaryDisplay();
        pos = [bounds.width - size.width - 40, 60];
    }

    win = new BrowserWindow({
        ...size,
        x: pos[0],
        y: pos[1],
        title: process.env.APP_TITLE,
        resizable: false,
        useContentSize: true,
        frame: true,
        webPreferences: {
            // nativeWindowOpen: false,
            nodeIntegration: true,
            enableRemoteModule: true,
            preload: path.join(dirname, 'preload.mjs'),
            devTools: isDev,
        },
    });
    // win.on("close", (e) => {
    //     e.preventDefault();
    //     app.hide();
    // });

    // tray setting
    const icon = nativeImage.createFromPath(path.join(assetsPath, "icon", "24x24.png"));
    tray = new Tray(icon);
    tray.setToolTip(process.env.APP_TITLE);
    const contextMenu = Menu.buildFromTemplate([
        { label: "Exit", click: confirmClose },
    ]);
    tray.on("click", () => {
        tray.setContextMenu(null);
        toggleWindow();
    });
    tray.on("right-click", () => {
        tray.setContextMenu(contextMenu);
        tray.popUpContextMenu();
    });

    // if (isDev) {
    //     globalShortcut.register('CommandOrControl+R', () => {
    //         win.loadFile(indexPath);
    //     });
    // }

    win.setMenuBarVisibility(false);
    win.loadFile(indexPath);
    if (isDev) win.webContents.openDevTools({ mode: "undocked" });
}

// image src https config
app.commandLine.appendSwitch('ignore-certificate-errors');

if (!isDev) {
    app.setLoginItemSettings({
        openAtLogin: true,
        openAsHidden: true,
    });
}

app.on("ready", createWindow);
app.on("window-all-closed", () => {
    // if (process.platform !== "darwin") {
    //     app.quit();
    // }
    app.quit();
});

app.on("activate", () => {
    if (win === null) {
        createWindow();
    }
});

ipcMain.on("window-close", e => {
    // pos = win.getPosition();
    // app.hide();
    app.quit();
});

ipcMain.on("window-refresh", async e => {
    win.loadFile(indexPath);
});

ipcMain.on("notice", async (e, body, title = "") => {
    notice(title, body);
});

ipcMain.on("open", (e, url) => {
    shell.openExternal(url);
});

// Never remove this function(APIObject)
// this function's return response is API's first parameter.
/** example
 * const func = ({ electron, win, app, ipcMain }, a, b, c) => {
 *     const pos = win.getPosition();
 *     console.log(pos);
 *     console.log(a, b, c);
 *     return pos;
 * }
 */
const APIObject = () => {
    return { electron, app, win, ipcMain };
}"""

    PRELOAD = """import { ipcRenderer, contextBridge } from "electron";

const isDev = process.env.WIZ_ELECTRON_IS_DEV;
const API_BASE = process.env.API_BASE;
const APP_VERSION = process.env.npm_package_version;

process.once("loaded", () => {
    window.ipcRenderer = ipcRenderer;
});

contextBridge.exposeInMainWorld("env", {
    isDev,
    API_BASE,
    APP_VERSION,
});

contextBridge.exposeInMainWorld("api", {
    send: (channel, ...data) => {
        //whitelist channels
        const validChannels = [
            "window-close",
            "window-refresh",
            "notice",
            "open",
            "@wiz.electron.channels",
        ];
        if (!validChannels.includes(channel)) {
            return;
        }
        ipcRenderer.send(channel, ...data);
    },
    receive: (channel, func) => {
        const validChannels = [
            "window-close",
            "window-refresh",
            "notice",
            "open",
            "@wiz.electron.channels",
        ];
        if (!validChannels.includes(channel)) {
            return;
        }
        const f = (event, ...args) => {
            func(...args);
            ipcRenderer.removeListener(channel, f);
        }
        ipcRenderer.on(channel, f);
    },
});"""

    PATHS = """import path from "path";
import os from "os";
import { fileURLToPath } from "url";

const BASE = os.homedir();
const dirname = fileURLToPath(new URL(".", import.meta.url));
const dataPath = path.join(os.homedir(), process.env.DATA_PATH);
const buildPath = path.join(dirname, "..", "dist", "build");
const appPath = path.join(buildPath, "src", "app");
const indexPath = `${path.join(buildPath, "index.html")}`;
const assetsPath = path.join(buildPath, "assets");

export {
    BASE,
    dataPath,
    buildPath,
    appPath,
    indexPath,
    assetsPath,
};"""

    INDEX_PUG = """doctype html
html(lang="en")
    head
        meta(charset="utf-8")
        title WIZ ELECTRON SAMPLE PROJECT
        base(href="./")
        meta(name="viewport", content="width=device-width, initial-scale=1")
        script.
            window.addEventListener("keydown", (e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === 'r') {
                    e.preventDefault();
                    window.api.send('window-refresh');
                }
            });

    body
        app-root

"""

    WIZ_TS = """import $ from "jquery";
import { io } from "socket.io-client";

export default class Wiz {
    public namespace: any;
    public baseuri: any;

    constructor(baseuri: any) {
        this.baseuri = baseuri;
    }

    public app(namespace: any) {
        let instance = new Wiz(this.baseuri);
        instance.namespace = namespace;
        return instance;
    }

    public dev() {
        let findcookie = (name) => {
            let ca: Array<string> = document.cookie.split(';');
            let caLen: number = ca.length;
            let cookieName = `${name}=`;
            let c: string;

            for (let i: number = 0; i < caLen; i += 1) {
                c = ca[i].replace(/^\s+/g, '');
                if (c.indexOf(cookieName) == 0) {
                    return c.substring(cookieName.length, c.length);
                }
            }
            return '';
        }

        let isdev = findcookie("season-wiz-devmode");
        if (isdev == 'true') return true;
        return false;
    }

    public project() {
        let findcookie = (name) => {
            let ca: Array<string> = document.cookie.split(';');
            let caLen: number = ca.length;
            let cookieName = `${name}=`;
            let c: string;

            for (let i: number = 0; i < caLen; i += 1) {
                c = ca[i].replace(/^\s+/g, '');
                if (c.indexOf(cookieName) == 0) {
                    return c.substring(cookieName.length, c.length);
                }
            }
            return '';
        }

        let project = findcookie("season-wiz-project");
        if (project) return project;
        return "main";
    }

    public socket() {
        let socketns = this.baseuri + "/app/" + this.project();
        if (this.namespace)
            socketns = socketns + "/" + this.namespace;
        return io(socketns);
    };

    public server = {
        url: (function_name: string) => {
            let base = window.env.API_BASE;
            if (base.endsWith("/")) base = base.slice(0, -1);
            if (function_name[0] == "/") function_name = function_name.substring(1);
            return `${base}/api/${this.namespace}/${function_name}`;
        },
        call: (function_name: string, data = {}, options = {}) => {
            let ajax = {
                url: this.server.url(function_name),
                type: "POST",
                data: data,
                ...options,
            };

            return new Promise((resolve) => {
                $.ajax(ajax).always(function (res) {
                    resolve(res);
                });
            });
        },
    };

    public send(name, ...data) {
        window.api.send(name, ...data);
    }
    public receive(name, callback) {
        if (!callback) return;
        window.api.receive(name, callback);
    }

    public async electron(name, ...data) {
        return new Promise((resolve) => {
            this.receive(name, resolve);
            this.send(name, ...data);
        });
    }

    public url(function_name: string) {
        return `api.${this.namespace}.${function_name}`;
    }

    public call(function_name: string, ...params) {
        return this.electron(this.url(function_name), ...params);
    }
}
"""
