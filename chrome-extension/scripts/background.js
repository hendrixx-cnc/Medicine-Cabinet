/**
 * Medicine Cabinet - Background Service Worker
 * Handles extension lifecycle, native messaging, and data storage
 * 
 * NATIVE MESSAGING: Connects to Python backend for bidirectional sync
 * Browser can read files, Python backend handles writes
 */

import { parse } from './parser.js';

// Store for loaded capsules and tablets
let memoryStore = {
  capsules: [],
  tablets: [],
  activeCapsule: null,
  sessions: [] // Track all loaded sessions with metadata
};

// Native messaging port
let nativePort = null;

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  console.log('Medicine Cabinet extension installed');
  loadStoredMemory();
  connectNativeHost();
});

/**
 * Connect to native messaging host
 */
function connectNativeHost() {
  try {
    nativePort = chrome.runtime.connectNative('com.medicinecabinet.host');
    
    nativePort.onMessage.addListener((message) => {
      console.log('Received from native host:', message);
      handleNativeMessage(message);
    });
    
    nativePort.onDisconnect.addListener(() => {
      console.log('Native host disconnected:', chrome.runtime.lastError);
      nativePort = null;
      
      // Try to reconnect after 5 seconds
      setTimeout(connectNativeHost, 5000);
    });
    
    console.log('✅ Connected to native messaging host');
  } catch (error) {
    console.warn('Native messaging host not available:', error);
    // Extension will work in read-only mode without native host
  }
}

/**
 * Send message to native host
 */
function sendToNativeHost(message) {
  if (nativePort) {
    nativePort.postMessage(message);
    return true;
  } else {
    console.warn('Native host not connected');
    return false;
  }
}

/**
 * Handle messages from native host
 */
function handleNativeMessage(message) {
  // Handle responses from Python backend
  if (message.action === 'capsuleUpdated') {
    // Reload the updated capsule
    // TODO: Implement hot-reload
    console.log('Capsule updated by native host');
  } else if (message.action === 'tabletUpdated') {
    console.log('Tablet updated by native host');
  }
}

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

    case 'getSessions':
      sendResponse({ sessions: memoryStore.sessions });
      break;

    case 'getActiveCapsule':
      const activeCapsule = memoryStore.capsules.find(c => c.id === memoryStore.activeCapsule);
      sendResponse({ capsule: activeCapsule || null });
      break;

    case 'setActiveCapsule':
      setActiveCapsule(message.capsuleId);
      sendResponse({ success: true });
      break;

    case 'viewSession':
      handleViewSession(message.sessionId).then(result => {
        sendResponse(result);
      }).catch(error => {
        sendResponse({ error: error.message });
      });
      return true;

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

    case 'clearOldMeds':
      handleClearOldMeds(message.daysOld || 7).then(result => {
        sendResponse(result);
      }).catch(error => {
        sendResponse({ error: error.message });
      });
      return true;

    case 'clearAllMeds':
      handleClearAllMeds().then(result => {
        sendResponse(result);
      }).catch(error => {
        sendResponse({ error: error.message });
      });
      return true;

    case 'captureConversation':
      handleCaptureConversation(message.memories || message.messages); // Support both memories and messages
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
    const data = await chrome.storage.local.get(['capsules', 'tablets', 'activeCapsule', 'sessions']);
    memoryStore.capsules = data.capsules || [];
    memoryStore.tablets = data.tablets || [];
    memoryStore.activeCapsule = data.activeCapsule || null;
    memoryStore.sessions = data.sessions || [];
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
      activeCapsule: memoryStore.activeCapsule,
      sessions: memoryStore.sessions
    });
    
    // Check storage usage and warn if getting full
    await checkStorageUsage();
    
    console.log('Memory saved to storage');
  } catch (error) {
    console.error('Error saving memory:', error);
    
    // Check if quota exceeded
    if (error.message && error.message.includes('QUOTA_BYTES')) {
      console.error('⚠️  Storage quota exceeded! Please clear old meds.');
      // Could notify user here
    }
  }
}

/**
 * Check chrome.storage usage and warn if getting full
 */
async function checkStorageUsage() {
  try {
    const usage = await chrome.storage.local.getBytesInUse();
    const QUOTA = chrome.storage.local.QUOTA_BYTES || 10485760; // 10MB default
    const percent = Math.round((usage / QUOTA) * 100);
    
    console.log(`Storage: ${formatBytes(usage)} / ${formatBytes(QUOTA)} (${percent}%)`);
    
    // Warn at 70% full
    if (percent >= 70 && percent < 90) {
      console.warn(`💊 Storage is ${percent}% full - Consider clearing old meds`);
      console.warn(`   Run: medicine-cabinet cleanup`);
    }
    // Critical warning at 90%
    else if (percent >= 90) {
      console.error(`⚠️  STORAGE CRITICAL: ${percent}% full`);
      console.error(`   Old meds need to be tossed! Browser memory getting full.`);
      console.error(`   Clear old sessions to prevent Alzheimer's (memory loss)`);
    }
  } catch (error) {
    // Some browsers don't support getBytesInUse
    console.log('Storage usage tracking not available');
  }
}

/**
 * Format bytes to human readable
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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

    // Create session entry
    const sessionEntry = {
      id: generateId(),
      type: parsed.type,
      itemId: memoryItem.id,
      filename: fileData.name,
      loadedAt: memoryItem.loadedAt,
      metadata: parsed.type === 'capsule' 
        ? { project: parsed.metadata.project, summary: parsed.metadata.summary }
        : { title: parsed.metadata.title, entries: parsed.entries?.length || 0 }
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

    // Add to sessions list
    memoryStore.sessions.push(sessionEntry);

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
 * View detailed session information
 */
async function handleViewSession(sessionId) {
  const session = memoryStore.sessions.find(s => s.id === sessionId);
  if (!session) {
    throw new Error('Session not found');
  }

  // Find the actual capsule or tablet
  const item = session.type === 'capsule' 
    ? memoryStore.capsules.find(c => c.id === session.itemId)
    : memoryStore.tablets.find(t => t.id === session.itemId);

  if (!item) {
    throw new Error('Session data not found');
  }

  return {
    success: true,
    session: {
      ...session,
      data: item
    }
  };
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
 * Clear old medications (capsules and tablets older than specified days)
 */
async function handleClearOldMeds(daysOld = 7) {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - daysOld);
  const cutoffTime = cutoffDate.toISOString();

  const removedCapsules = [];
  const removedTablets = [];
  const removedSessions = [];

  // Filter capsules
  memoryStore.capsules = memoryStore.capsules.filter(capsule => {
    if (capsule.loadedAt < cutoffTime) {
      removedCapsules.push(capsule.filename);
      return false;
    }
    return true;
  });

  // Filter tablets
  memoryStore.tablets = memoryStore.tablets.filter(tablet => {
    if (tablet.loadedAt < cutoffTime) {
      removedTablets.push(tablet.filename);
      return false;
    }
    return true;
  });

  // Filter sessions
  memoryStore.sessions = memoryStore.sessions.filter(session => {
    if (session.loadedAt < cutoffTime) {
      removedSessions.push(session.filename);
      return false;
    }
    return true;
  });

  // Reset active capsule if it was removed
  if (memoryStore.activeCapsule) {
    const activeCapsuleExists = memoryStore.capsules.some(c => c.id === memoryStore.activeCapsule);
    if (!activeCapsuleExists) {
      memoryStore.activeCapsule = memoryStore.capsules.length > 0 ? memoryStore.capsules[0].id : null;
    }
  }

  await saveMemory();

  return {
    success: true,
    removed: {
      capsules: removedCapsules.length,
      tablets: removedTablets.length,
      sessions: removedSessions.length,
      total: removedCapsules.length + removedTablets.length
    },
    cutoffDate: cutoffTime
  };
}

/**
 * Clear all medications (capsules, tablets, and sessions)
 */
async function handleClearAllMeds() {
  const capsulesCount = memoryStore.capsules.length;
  const tabletsCount = memoryStore.tablets.length;
  const sessionsCount = memoryStore.sessions.length;

  memoryStore.capsules = [];
  memoryStore.tablets = [];
  memoryStore.sessions = [];
  memoryStore.activeCapsule = null;

  await saveMemory();

  return {
    success: true,
    removed: {
      capsules: capsulesCount,
      tablets: tabletsCount,
      sessions: sessionsCount,
      total: capsulesCount + tabletsCount
    }
  };
}

/**
 * Handle conversation capture - receives contextual memories (not raw messages)
 */
function handleCaptureConversation(memories) {
  if (!memories || memories.length === 0) {
    return;
  }

  console.log(`� Capturing ${memories.length} contextual memories (filtered from conversation)`);

  // Send to native host for persistence as tablet
  if (nativePort) {
    sendToNativeHost({
      action: 'captureConversation',
      memories: memories,  // Filtered contextual memories
      timestamp: new Date().toISOString()
    });
  } else {
    console.warn('Native host not available, memories not persisted to tablet');
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
