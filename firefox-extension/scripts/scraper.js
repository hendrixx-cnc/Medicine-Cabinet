/**
 * Medicine Cabinet - Conversation Scraper
 * Captures ChatGPT conversations for persistent context
 */

class ConversationScraper {
  constructor() {
    this.conversationHistory = [];
    this.isObserving = false;
    this.observer = null;
    this.lastMessageCount = 0;
  }

  /**
   * Start observing conversation for new messages
   */
  start() {
    if (this.isObserving) return;

    console.log('Starting conversation scraper...');
    this.isObserving = true;

    // Initial scrape
    this.scrapeConversation();

    // Watch for new messages
    this.observer = new MutationObserver((mutations) => {
      this.scrapeConversation();
    });

    // Observe the chat container
    const chatContainer = this.getChatContainer();
    if (chatContainer) {
      this.observer.observe(chatContainer, {
        childList: true,
        subtree: true
      });
    }
  }

  /**
   * Stop observing
   */
  stop() {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    this.isObserving = false;
    console.log('Stopped conversation scraper');
  }

  /**
   * Get the chat container element based on site
   */
  getChatContainer() {
    const hostname = window.location.hostname;

    if (hostname.includes('openai.com')) {
      return document.querySelector('main') || document.body;
    } else if (hostname.includes('claude.ai')) {
      return document.querySelector('[data-testid="conversation"]') || document.body;
    } else if (hostname.includes('gemini.google.com')) {
      return document.querySelector('chat-window') || document.body;
    }

    return document.body;
  }

  /**
   * Scrape current conversation and extract contextual memories
   */
  scrapeConversation() {
    const hostname = window.location.hostname;
    let messages = [];

    if (hostname.includes('openai.com')) {
      messages = this.scrapeChatGPT();
    } else if (hostname.includes('claude.ai')) {
      messages = this.scrapeClaude();
    } else if (hostname.includes('gemini.google.com')) {
      messages = this.scrapeGemini();
    }

    // Check if we have new messages
    if (messages.length > this.lastMessageCount) {
      const newMessages = messages.slice(this.lastMessageCount);
      
      // Filter for contextual memories (not every literal message)
      const contextualMemories = this.extractContext(newMessages);
      
      if (contextualMemories.length > 0) {
        this.conversationHistory.push(...contextualMemories);
        this.lastMessageCount = messages.length;

        // Notify background script of new contextual memories
        this.sendToNativeHost(contextualMemories);
      }
    }
  }

  /**
   * Extract contextual memories from raw messages
   * 
   * STRATEGY: Store generous amounts locally (IDE has space),
   * but filter aggressively for what gets loaded server-side
   * 
   * HARD LIMITS: 8MB persistent storage, 1MB active capsule
   * (works on any modern browser)
   * 
   * Stored locally: Full context for detailed queries
   * Sent to server: Tiny summaries for context window
   */
  extractContext(messages) {
    const contextualMemories = [];
    const MAX_PER_CYCLE = 10;  // Max 10 memories per cycle
    const MAX_ENTRY_SIZE = 1000;  // 1KB per entry max
    
    for (const msg of messages) {
      const content = msg.content;
      
      // Store if it has ANY technical value (IDE can handle it)
      if (content.length < 80) continue;  // Skip only trivial stuff
      
      const hasTechnicalValue = (
        // Code (any amount)
        content.includes('```') ||
        
        // Decisions or implementations
        /\b(decided|implemented|created|modified|fixed|refactored)\b/i.test(content) ||
        
        // Technical terms
        /\b(function|class|method|error|bug|API|database)\b/i.test(content) ||
        
        // File references
        /\.(js|py|ts|jsx|tsx|json|md|html|css)\b/i.test(content)
      );
      
      if (hasTechnicalValue) {
        // Truncate to 1KB max per entry to prevent bloat
        const truncatedContent = content.length > MAX_ENTRY_SIZE 
          ? content.substring(0, MAX_ENTRY_SIZE) + '...[truncated]'
          : content;
        
        contextualMemories.push({
          role: msg.role,
          content: truncatedContent,  // Max 1KB per entry
          summary: content.substring(0, 150) + '...',  // Tiny preview for server
          type: 'contextual_memory',
          extracted: new Date().toISOString(),
          size: truncatedContent.length
        });
      }
    }
    
    // Max 10 memories per cycle
    return contextualMemories.slice(0, MAX_PER_CYCLE);
  }

  /**
   * Scrape ChatGPT conversation
   */
  scrapeChatGPT() {
    const messages = [];
    const messageElements = document.querySelectorAll('[data-message-author-role]');

    messageElements.forEach((element) => {
      const role = element.getAttribute('data-message-author-role');
      const content = element.querySelector('.markdown') || element;
      
      if (content) {
        messages.push({
          role: role === 'user' ? 'user' : 'assistant',
          content: content.textContent.trim(),
          timestamp: new Date().toISOString()
        });
      }
    });

    return messages;
  }

  /**
   * Scrape Claude conversation
   */
  scrapeClaude() {
    const messages = [];
    const messageElements = document.querySelectorAll('[data-testid^="message"]');

    messageElements.forEach((element) => {
      const isUser = element.querySelector('[data-testid="user-message"]');
      const content = element.textContent.trim();

      if (content) {
        messages.push({
          role: isUser ? 'user' : 'assistant',
          content: content,
          timestamp: new Date().toISOString()
        });
      }
    });

    return messages;
  }

  /**
   * Scrape Gemini conversation
   */
  scrapeGemini() {
    const messages = [];
    const messageElements = document.querySelectorAll('message-content');

    messageElements.forEach((element) => {
      const isUser = element.closest('[data-test-id="user-message"]');
      const content = element.textContent.trim();

      if (content) {
        messages.push({
          role: isUser ? 'user' : 'assistant',
          content: content,
          timestamp: new Date().toISOString()
        });
      }
    });

    return messages;
  }

  /**
   * Send contextual memories to native host
   */
  async sendToNativeHost(memories) {
    if (memories.length === 0) return;

    // Check storage size first
    const storageCheck = await this.checkStorageSize();
    
    if (!storageCheck.ok) {
      console.error('💊 Medicine Cabinet: Storage full', storageCheck);
      this.showStorageWarning(storageCheck.message);
      return;
    }
    
    if (storageCheck.warning) {
      console.warn('💊 Medicine Cabinet:', storageCheck.message);
    }

    try {
      // Send to background script which will relay to native host
      await chrome.runtime.sendMessage({
        action: 'captureConversation',
        memories: memories  // Renamed from 'messages' to 'memories'
      });

      console.log(`💊 Captured ${memories.length} contextual memories (${storageCheck.size_mb.toFixed(2)}MB / 8MB)`);
    } catch (error) {
      console.error('Error sending memories to native host:', error);
    }
  }

  /**
   * Check storage size against 8MB limit
   */
  async checkStorageSize() {
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      return new Promise((resolve) => {
        chrome.storage.local.getBytesInUse(null, (bytes) => {
          const mb = bytes / (1024 * 1024);
          const MAX_MB = 8; // 8MB hard limit for persistent storage
          
          if (mb > MAX_MB) {
            resolve({
              ok: false,
              error: 'STORAGE_FULL',
              size_mb: mb,
              limit_mb: MAX_MB,
              message: `Storage full: ${mb.toFixed(2)}MB / ${MAX_MB}MB. Time to take your meds!`
            });
          } else if (mb > 6) {  // 75% threshold
            resolve({
              ok: true,
              warning: 'CLEANUP_RECOMMENDED',
              size_mb: mb,
              percent: (mb / MAX_MB * 100).toFixed(0),
              message: `Storage at ${mb.toFixed(2)}MB (${(mb / MAX_MB * 100).toFixed(0)}%) - cleanup recommended`
            });
          } else {
            resolve({
              ok: true,
              size_mb: mb,
              percent: (mb / MAX_MB * 100).toFixed(0),
              message: `Storage healthy: ${mb.toFixed(2)}MB (${(mb / MAX_MB * 100).toFixed(0)}%)`
            });
          }
        });
      });
    }
    return { ok: true, size_mb: 0 };
  }

  /**
   * Show storage warning to user
   */
  showStorageWarning(message) {
    // Create a notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: #ff4444;
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      z-index: 10000;
      font-family: system-ui;
      max-width: 400px;
    `;
    notification.innerHTML = `
      <div style="font-weight: bold; margin-bottom: 5px;">💊 Medicine Cabinet</div>
      <div>${message}</div>
      <div style="margin-top: 10px; font-size: 0.9em;">Run: <code>python3 cli.py cleanup</code></div>
    `;
    document.body.appendChild(notification);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      notification.remove();
    }, 10000);
  }

  /**
   * Send contextual memories to native host
   */
  async sendToNativeHost_old(memories) {
    if (memories.length === 0) return;

    try {
      // Send to background script which will relay to native host
      await chrome.runtime.sendMessage({
        action: 'captureConversation',
        memories: memories  // Renamed from 'messages' to 'memories'
      });

      console.log(`� Captured ${memories.length} contextual memories (not literal messages)`);
    } catch (error) {
      console.error('Error sending memories to native host:', error);
    }
  }

  /**
   * Get all captured conversation history
   */
  getHistory() {
    return this.conversationHistory;
  }

  /**
   * Clear conversation history
   */
  clear() {
    this.conversationHistory = [];
    this.lastMessageCount = 0;
  }
}

// Export for use in content script
window.ConversationScraper = ConversationScraper;
