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
   * Only captures what's needed for context, not every literal message
   */
  extractContext(messages) {
    const contextualMemories = [];
    
    for (const msg of messages) {
      const content = msg.content;
      
      // Skip short, non-contextual messages
      if (content.length < 50) continue;
      
      // Check if message contains contextual information
      const hasContext = (
        // Code blocks
        content.includes('```') ||
        // Decisions/plans
        /\b(decide|plan|implement|design|architecture|approach|solution)\b/i.test(content) ||
        // Task/objective
        /\b(task|objective|goal|requirement|need to|should)\b/i.test(content) ||
        // Technical discussions
        /\b(function|class|method|API|database|algorithm|pattern)\b/i.test(content) ||
        // File references
        /\.(js|py|ts|jsx|tsx|json|md|html|css)\b/i.test(content) ||
        // Errors/issues
        /\b(error|issue|bug|problem|fix|debug)\b/i.test(content)
      );
      
      if (hasContext) {
        contextualMemories.push({
          ...msg,
          type: 'contextual_memory',  // Mark as memory, not raw message
          extracted: new Date().toISOString()
        });
      }
    }
    
    return contextualMemories;
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
