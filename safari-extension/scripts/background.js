/**
 * Medicine Cabinet - Background Service Worker
 * Handles extension lifecycle, native messaging, and data storage
 */

import { parse } from './parser.js';

// Store for loaded capsules and tablets
let memoryStore = {
  capsules: [],
  tablets: [],
  activeCapsule: null
};

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Medicine Cabinet extension installed');
  loadStoredMemory();
});

// Listen for messages from popup and content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);

  switch (message.action) {
    case 'getCapsules':
      sendResponse({ capsules: memoryStore.capsules });
      break;

    case 'getTablets':
      sendResponse({ tablets: memoryStore.tablets });
      break;

    case 'getActiveCapsule':
      sendResponse({ capsule: memoryStore.activeCapsule });
      break;

    case 'setActiveCapsule':
      setActiveCapsule(message.capsuleId);
      sendResponse({ success: true });
      break;

    case 'loadFile':
      handleLoadFile(message.file).then(result => {
        sendResponse(result);
      }).catch(error => {
        sendResponse({ error: error.message });
      });
      return true; // Keep channel open for async response

    case 'removeMemory':
      handleRemoveMemory(message.id, message.type);
      sendResponse({ success: true });
      break;

    case 'injectContext':
      handleInjectContext(message.tabId);
      sendResponse({ success: true });
      break;

    default:
      sendResponse({ error: 'Unknown action' });
  }

  return false;
});

/**
 * Load memory from chrome.storage
 */
async function loadStoredMemory() {
  try {
    const data = await chrome.storage.local.get(['capsules', 'tablets', 'activeCapsule']);
    memoryStore.capsules = data.capsules || [];
    memoryStore.tablets = data.tablets || [];
    memoryStore.activeCapsule = data.activeCapsule || null;
    console.log('Loaded stored memory:', memoryStore);
  } catch (error) {
    console.error('Error loading stored memory:', error);
  }
}

/**
 * Save memory to chrome.storage
 */
async function saveMemory() {
  try {
    await chrome.storage.local.set({
      capsules: memoryStore.capsules,
      tablets: memoryStore.tablets,
      activeCapsule: memoryStore.activeCapsule
    });
    console.log('Memory saved to storage');
  } catch (error) {
    console.error('Error saving memory:', error);
  }
}

/**
 * Handle loading a file (capsule or tablet)
 */
async function handleLoadFile(fileData) {
  try {
    // fileData should contain: { name, data: ArrayBuffer }
    const arrayBuffer = fileData.data;
    const parsed = parse(arrayBuffer);

    const memoryItem = {
      id: generateId(),
      filename: fileData.name,
      loadedAt: new Date().toISOString(),
      ...parsed
    };

    if (parsed.type === 'capsule') {
      memoryStore.capsules.push(memoryItem);
      // Auto-set as active if it's the first capsule
      if (!memoryStore.activeCapsule) {
        memoryStore.activeCapsule = memoryItem.id;
      }
    } else if (parsed.type === 'tablet') {
      memoryStore.tablets.push(memoryItem);
    }

    await saveMemory();
    return { success: true, item: memoryItem };
  } catch (error) {
    console.error('Error loading file:', error);
    return { success: false, error: error.message };
  }
}

/**
 * Remove a memory item
 */
async function handleRemoveMemory(id, type) {
  if (type === 'capsule') {
    memoryStore.capsules = memoryStore.capsules.filter(c => c.id !== id);
    if (memoryStore.activeCapsule === id) {
      memoryStore.activeCapsule = memoryStore.capsules.length > 0 
        ? memoryStore.capsules[0].id 
        : null;
    }
  } else if (type === 'tablet') {
    memoryStore.tablets = memoryStore.tablets.filter(t => t.id !== id);
  }
  await saveMemory();
}

/**
 * Set the active capsule
 */
async function setActiveCapsule(capsuleId) {
  memoryStore.activeCapsule = capsuleId;
  await saveMemory();
  
  // Notify all content scripts about the new active capsule
  const capsule = memoryStore.capsules.find(c => c.id === capsuleId);
  if (capsule) {
    broadcastToContentScripts({ 
      action: 'activeCapsuleChanged', 
      capsule 
    });
  }
}

/**
 * Inject context into the active tab
 */
async function handleInjectContext(tabId) {
  const capsule = memoryStore.capsules.find(c => c.id === memoryStore.activeCapsule);
  if (!capsule) {
    console.log('No active capsule to inject');
    return;
  }

  try {
    await chrome.tabs.sendMessage(tabId, {
      action: 'injectCapsuleContext',
      capsule
    });
  } catch (error) {
    console.error('Error injecting context:', error);
  }
}

/**
 * Broadcast message to all content scripts
 */
async function broadcastToContentScripts(message) {
  const tabs = await chrome.tabs.query({});
  for (const tab of tabs) {
    try {
      await chrome.tabs.sendMessage(tab.id, message);
    } catch (error) {
      // Tab may not have content script loaded, ignore
    }
  }
}

/**
 * Generate a unique ID
 */
function generateId() {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { memoryStore };
}
