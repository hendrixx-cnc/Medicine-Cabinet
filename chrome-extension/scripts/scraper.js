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
   * Scrape current conversation
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
      this.conversationHistory.push(...newMessages);
      this.lastMessageCount = messages.length;

      // Notify background script of new messages
      this.sendToNativeHost(newMessages);
    }
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
   * Send scraped messages to native host
   */
  async sendToNativeHost(messages) {
    if (messages.length === 0) return;

    try {
      // Send to background script which will relay to native host
      await chrome.runtime.sendMessage({
        action: 'captureConversation',
        messages: messages
      });

      console.log(`📝 Captured ${messages.length} new messages`);
    } catch (error) {
      console.error('Error sending to native host:', error);
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
