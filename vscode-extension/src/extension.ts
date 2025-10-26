import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface ContextState {
    loadedCapsule: string | null;
    loadedTablets: string[];
    contextSize: number;
    lastUpdate: Date;
}

let contextState: ContextState = {
    loadedCapsule: null,
    loadedTablets: [],
    contextSize: 0,
    lastUpdate: new Date()
};

let contextTreeProvider: ContextTreeProvider;
let healthTreeProvider: HealthTreeProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('Medicine Cabinet extension activated');

    // Initialize tree providers
    contextTreeProvider = new ContextTreeProvider();
    healthTreeProvider = new HealthTreeProvider();

    vscode.window.registerTreeDataProvider('medicine-cabinet.contextView', contextTreeProvider);
    vscode.window.registerTreeDataProvider('medicine-cabinet.healthView', healthTreeProvider);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('medicine-cabinet.loadCapsule', loadCapsule),
        vscode.commands.registerCommand('medicine-cabinet.loadTablet', loadTablet),
        vscode.commands.registerCommand('medicine-cabinet.refresh', refresh),
        vscode.commands.registerCommand('medicine-cabinet.clearContext', clearContext),
        vscode.commands.registerCommand('medicine-cabinet.exportSession', exportSession),
        vscode.commands.registerCommand('medicine-cabinet.showHealth', showHealth)
    );

    // Auto-load on startup if enabled
    const config = vscode.workspace.getConfiguration('medicine-cabinet');
    if (config.get<boolean>('autoLoad')) {
        loadContextOnStartup();
    }

    // Show welcome message
    vscode.window.showInformationMessage('💊 Medicine Cabinet ready!');
}

async function loadCapsule() {
    const config = vscode.workspace.getConfiguration('medicine-cabinet');
    const capsulePath = config.get<string>('capsulePath') || '';
    
    const fileUri = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: false,
        filters: { 'Context Capsules': ['auractx', 'json'] },
        defaultUri: capsulePath ? vscode.Uri.file(capsulePath) : undefined,
        title: 'Select Context Capsule'
    });

    if (fileUri && fileUri[0]) {
        const filePath = fileUri[0].fsPath;
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const data = JSON.parse(content);
            
            contextState.loadedCapsule = filePath;
            contextState.contextSize += Buffer.byteLength(content, 'utf-8') / 1024;
            contextState.lastUpdate = new Date();

            contextTreeProvider.refresh();
            healthTreeProvider.refresh();

            vscode.window.showInformationMessage(
                `💊 Loaded capsule: ${path.basename(filePath)}\n` +
                `Project: ${data.metadata?.project || 'Unknown'}\n` +
                `Files: ${data.relevant_files?.length || 0}`
            );
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to load capsule: ${error}`);
        }
    }
}

async function loadTablet() {
    const config = vscode.workspace.getConfiguration('medicine-cabinet');
    const tabletPath = expandPath(config.get<string>('tabletPath') || '~/.medicine_cabinet/tablets');
    
    const fileUri = await vscode.window.showOpenDialog({
        canSelectFiles: true,
        canSelectFolders: false,
        canSelectMany: true,
        filters: { 'Tablets': ['auratab', 'json'] },
        defaultUri: fs.existsSync(tabletPath) ? vscode.Uri.file(tabletPath) : undefined,
        title: 'Select Tablets (Memory)'
    });

    if (fileUri && fileUri.length > 0) {
        for (const uri of fileUri) {
            const filePath = uri.fsPath;
            try {
                const content = fs.readFileSync(filePath, 'utf-8');
                const data = JSON.parse(content);
                
                if (!contextState.loadedTablets.includes(filePath)) {
                    contextState.loadedTablets.push(filePath);
                    contextState.contextSize += Buffer.byteLength(content, 'utf-8') / 1024;
                }
            } catch (error) {
                vscode.window.showErrorMessage(`Failed to load tablet ${path.basename(filePath)}: ${error}`);
            }
        }

        contextState.lastUpdate = new Date();
        contextTreeProvider.refresh();
        healthTreeProvider.refresh();

        vscode.window.showInformationMessage(
            `💊 Loaded ${fileUri.length} tablet(s)\n` +
            `Total context: ${contextState.contextSize.toFixed(1)}KB`
        );
    }
}

async function refresh() {
    try {
        // Re-read all loaded files to update context
        let newSize = 0;
        
        if (contextState.loadedCapsule && fs.existsSync(contextState.loadedCapsule)) {
            const content = fs.readFileSync(contextState.loadedCapsule, 'utf-8');
            newSize += Buffer.byteLength(content, 'utf-8') / 1024;
        }

        for (const tabletPath of contextState.loadedTablets) {
            if (fs.existsSync(tabletPath)) {
                const content = fs.readFileSync(tabletPath, 'utf-8');
                newSize += Buffer.byteLength(content, 'utf-8') / 1024;
            }
        }

        contextState.contextSize = newSize;
        contextState.lastUpdate = new Date();

        contextTreeProvider.refresh();
        healthTreeProvider.refresh();

        vscode.window.showInformationMessage('💊 Context refreshed!');
    } catch (error) {
        vscode.window.showErrorMessage(`Failed to refresh: ${error}`);
    }
}

async function clearContext() {
    const answer = await vscode.window.showWarningMessage(
        'Clear all loaded context?',
        { modal: true },
        'Yes', 'No'
    );

    if (answer === 'Yes') {
        contextState = {
            loadedCapsule: null,
            loadedTablets: [],
            contextSize: 0,
            lastUpdate: new Date()
        };

        contextTreeProvider.refresh();
        healthTreeProvider.refresh();

        vscode.window.showInformationMessage('💊 Context cleared!');
    }
}

async function exportSession() {
    try {
        const { stdout } = await execAsync('python3 -m medicine_cabinet.cli export');
        vscode.window.showInformationMessage(`💊 Session exported!\n${stdout.trim()}`);
    } catch (error: any) {
        vscode.window.showErrorMessage(`Failed to export: ${error.message}`);
    }
}

async function showHealth() {
    const config = vscode.workspace.getConfiguration('medicine-cabinet');
    const maxSize = config.get<number>('maxContextSize') || 75;
    
    const percentage = (contextState.contextSize / maxSize) * 100;
    let status = '🟢 HEALTHY';
    let message = 'Context size is within limits';

    if (percentage > 90) {
        status = '🔴 CRITICAL';
        message = 'I need to visit the doctor! (export or refresh needed)';
    } else if (percentage > 75) {
        status = '🟡 WARNING';
        message = 'Getting full - consider a checkup soon';
    }

    vscode.window.showInformationMessage(
        `💊 Health Status: ${status}\n\n` +
        `Context: ${contextState.contextSize.toFixed(1)}KB / ${maxSize}KB (${percentage.toFixed(0)}%)\n` +
        `Capsule: ${contextState.loadedCapsule ? '✓' : '✗'}\n` +
        `Tablets: ${contextState.loadedTablets.length}\n\n` +
        message
    );
}

async function loadContextOnStartup() {
    const config = vscode.workspace.getConfiguration('medicine-cabinet');
    const tabletPath = expandPath(config.get<string>('tabletPath') || '~/.medicine_cabinet/tablets');
    
    if (fs.existsSync(tabletPath)) {
        try {
            const files = fs.readdirSync(tabletPath)
                .filter(f => f.endsWith('.auratab'))
                .slice(0, 10); // Load last 10 tablets
            
            for (const file of files) {
                const filePath = path.join(tabletPath, file);
                const content = fs.readFileSync(filePath, 'utf-8');
                
                contextState.loadedTablets.push(filePath);
                contextState.contextSize += Buffer.byteLength(content, 'utf-8') / 1024;
            }

            contextState.lastUpdate = new Date();
            contextTreeProvider.refresh();
            healthTreeProvider.refresh();
        } catch (error) {
            console.error('Failed to auto-load context:', error);
        }
    }
}

function expandPath(p: string): string {
    if (p.startsWith('~')) {
        return path.join(process.env.HOME || process.env.USERPROFILE || '', p.slice(1));
    }
    return p;
}

class ContextTreeProvider implements vscode.TreeDataProvider<ContextItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ContextItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: ContextItem): vscode.TreeItem {
        return element;
    }

    getChildren(element?: ContextItem): Thenable<ContextItem[]> {
        if (!element) {
            const items: ContextItem[] = [];
            
            if (contextState.loadedCapsule) {
                items.push(new ContextItem(
                    `📋 ${path.basename(contextState.loadedCapsule)}`,
                    vscode.TreeItemCollapsibleState.None
                ));
            }

            if (contextState.loadedTablets.length > 0) {
                items.push(new ContextItem(
                    `📚 Tablets (${contextState.loadedTablets.length})`,
                    vscode.TreeItemCollapsibleState.Collapsed,
                    contextState.loadedTablets.map(t => 
                        new ContextItem(`💊 ${path.basename(t)}`, vscode.TreeItemCollapsibleState.None)
                    )
                ));
            }

            if (items.length === 0) {
                items.push(new ContextItem('No context loaded', vscode.TreeItemCollapsibleState.None));
            }

            return Promise.resolve(items);
        } else {
            return Promise.resolve(element.children || []);
        }
    }
}

class ContextItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly children?: ContextItem[]
    ) {
        super(label, collapsibleState);
    }
}

class HealthTreeProvider implements vscode.TreeDataProvider<HealthItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<HealthItem | undefined | null | void>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: HealthItem): vscode.TreeItem {
        return element;
    }

    getChildren(): Thenable<HealthItem[]> {
        const config = vscode.workspace.getConfiguration('medicine-cabinet');
        const maxSize = config.get<number>('maxContextSize') || 75;
        const percentage = (contextState.contextSize / maxSize) * 100;
        
        let status = '🟢 Healthy';
        if (percentage > 90) {
            status = '🔴 Critical';
        } else if (percentage > 75) {
            status = '🟡 Warning';
        }

        const items = [
            new HealthItem(`Status: ${status}`),
            new HealthItem(`Size: ${contextState.contextSize.toFixed(1)}KB / ${maxSize}KB`),
            new HealthItem(`Usage: ${percentage.toFixed(0)}%`),
            new HealthItem(`Updated: ${contextState.lastUpdate.toLocaleTimeString()}`)
        ];

        return Promise.resolve(items);
    }
}

class HealthItem extends vscode.TreeItem {
    constructor(public readonly label: string) {
        super(label, vscode.TreeItemCollapsibleState.None);
    }
}

export function deactivate() {}
