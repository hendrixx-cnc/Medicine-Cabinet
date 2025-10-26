/**
 * Medicine Cabinet - Content Script
 * Pops AI memory context into supported web pages
 * AUTO-POP MODE: Automatically pops context when you visit AI sites
 * CONVERSATION CAPTURE: Scrapes and persists chat conversations
 */

console.log('Medicine Cabinet content script loaded');

let activeCapsule = null;
let autoInjectEnabled = true;
let hasAutoInjected = false;
let conversationScraper = null;

// Check if we should auto-pop on this site
const hostname = window.location.hostname;
const isAISite = hostname.includes('openai.com') || 
                 hostname.includes('claude.ai') || 
                 hostname.includes('gemini.google.com') ||
                 hostname.includes('chat.google.com') ||
                 hostname.includes('bing.com');

// Load auto-pop preference from storage
browser.storage.local.get(['autoInjectEnabled', 'captureConversations'], (result) => {
  autoInjectEnabled = result.autoInjectEnabled !== false; // Default true
  const captureEnabled = result.captureConversations !== false; // Default true
  
  console.log('Auto-pop preference loaded:', autoInjectEnabled);
  console.log('Conversation capture:', captureEnabled);
  
  // Start conversation scraper if enabled and on AI site
  if (captureEnabled && isAISite) {
    initializeConversationScraper();
  }
});

/**
 * Initialize conversation scraper
 */
function initializeConversationScraper() {
  // Load scraper script
  const script = document.createElement('script');
  script.src = browser.runtime.getURL('scripts/scraper.js');
  script.onload = () => {
    if (window.ConversationScraper) {
      conversationScraper = new window.ConversationScraper();
      conversationScraper.start();
      console.log('💬 Conversation capture started');
    }
  };
  (document.head || document.documentElement).appendChild(script);
}

// Listen for messages from background script
browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Content script received message:', message);

  switch (message.action) {
    case 'activeCapsuleChanged':
      activeCapsule = message.capsule;
      console.log('Active capsule updated:', activeCapsule);
      // Auto-pop when capsule changes
      if (autoInjectEnabled && isAISite && !hasAutoInjected) {
        setTimeout(() => autoPop(), 1000);
      }
      break;

    case 'injectCapsuleContext':
      injectContext(message.capsule);
      sendResponse({ success: true });
      break;

    case 'toggleAutoInject':
      autoInjectEnabled = message.enabled;
      console.log('Auto-pop:', autoInjectEnabled ? 'enabled' : 'disabled');
      sendResponse({ success: true });
      break;
  }

  return false;
});

// Request active capsule from background when page loads
browser.runtime.sendMessage({ action: 'getActiveCapsule' }, (response) => {
  if (response && response.capsule) {
    activeCapsule = response.capsule;
    console.log('Retrieved active capsule:', activeCapsule.metadata.project);
    
    // Auto-pop if on AI site and have capsule
    if (autoInjectEnabled && isAISite && activeCapsule) {
      setTimeout(() => autoPop(), 2000); // Wait for page to load
    }
  }
});

/**
 * Auto-pop context when page is ready
 */
function autoPop() {
  if (!activeCapsule || hasAutoInjected) {
    return;
  }

  console.log('Auto-popping context...');
  
  // Wait for input field to be available
  waitForElement(getInputSelector(), (element) => {
    if (element && !hasAutoInjected) {
      hasAutoInjected = true;
      injectContext(activeCapsule);
    }
  });
}

/**
 * Get the appropriate input selector for current site
 */
function getInputSelector() {
  if (hostname.includes('openai.com')) {
    return 'textarea[data-id], textarea#prompt-textarea, div[contenteditable="true"]';
  } else if (hostname.includes('claude.ai')) {
    return 'div[contenteditable="true"], textarea';
  } else if (hostname.includes('gemini.google.com') || hostname.includes('chat.google.com')) {
    return 'textarea, div[contenteditable="true"]';
  } else if (hostname.includes('bing.com')) {
    return 'textarea.searchbox, textarea[aria-label*="Ask"], div[contenteditable="true"]';
  }
  return 'textarea, div[contenteditable="true"]';
}

/**
 * Wait for element to appear in DOM
 */
function waitForElement(selector, callback, timeout = 10000) {
  const element = document.querySelector(selector);
  if (element) {
    callback(element);
    return;
  }

  const observer = new MutationObserver((mutations, obs) => {
    const element = document.querySelector(selector);
    if (element) {
      obs.disconnect();
      callback(element);
    }
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Timeout after specified time
  setTimeout(() => {
    observer.disconnect();
    console.log('Timeout waiting for input element');
  }, timeout);
}

/**
 * Inject capsule context into the page
 */
function injectContext(capsule) {
  if (!capsule) {
    console.warn('No capsule provided for injection');
    return;
  }

  console.log('Injecting context for capsule:', capsule.metadata.project);

  // Detect the site and use appropriate injection method
  const hostname = window.location.hostname;

  if (hostname.includes('github.com')) {
    injectGitHub(capsule);
  } else if (hostname.includes('stackoverflow.com')) {
    injectStackOverflow(capsule);
  } else if (hostname.includes('openai.com')) {
    injectChatGPT(capsule);
  } else if (hostname.includes('claude.ai')) {
    injectClaude(capsule);
  } else if (hostname.includes('gemini.google.com')) {
    injectGemini(capsule);
  } else {
    // Generic injection
    injectGeneric(capsule);
  }

  showInjectionNotification(capsule.metadata.project);
}

/**
 * Inject context into GitHub
 */
function injectGitHub(capsule) {
  const context = formatCapsuleContext(capsule);
  
  // Try to find comment boxes, issue descriptions, PR descriptions, etc.
  const commentBoxes = document.querySelectorAll('textarea[name="comment[body]"], textarea.comment-form-textarea');
  
  if (commentBoxes.length > 0) {
    const textbox = commentBoxes[0];
    appendToTextarea(textbox, `\n\n<!-- Medicine Cabinet Context -->\n${context}\n`);
  } else {
    // Copy to clipboard as fallback
    copyToClipboard(context);
    console.log('GitHub: Copied context to clipboard (no active text field found)');
  }
}

/**
 * Inject context into Stack Overflow
 */
function injectStackOverflow(capsule) {
  const context = formatCapsuleContext(capsule);
  
  // Find question or answer editor
  const editors = document.querySelectorAll('textarea.wmd-input, div[contenteditable="true"]');
  
  if (editors.length > 0) {
    const editor = editors[0];
    if (editor.tagName === 'TEXTAREA') {
      appendToTextarea(editor, `\n\n<!-- Context -->\n${context}\n`);
    } else {
      editor.textContent += `\n\n${context}\n`;
    }
  } else {
    copyToClipboard(context);
    console.log('StackOverflow: Copied context to clipboard');
  }
}

/**
 * Inject context into ChatGPT
 */
function injectChatGPT(capsule) {
  const context = formatCapsuleContext(capsule);
  
  // Find the prompt textarea
  const promptBox = document.querySelector('textarea[data-id], textarea#prompt-textarea, div[contenteditable="true"]');
  
  if (promptBox) {
    if (promptBox.tagName === 'TEXTAREA') {
      appendToTextarea(promptBox, context);
      // Trigger input event to enable send button
      promptBox.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      promptBox.textContent = (promptBox.textContent || '') + '\n\n' + context;
    }
  } else {
    copyToClipboard(context);
    console.log('ChatGPT: Copied context to clipboard');
  }
}

/**
 * Inject context into Claude
 */
function injectClaude(capsule) {
  const context = formatCapsuleContext(capsule);
  
  // Find Claude's input field
  const inputFields = document.querySelectorAll('div[contenteditable="true"], textarea');
  
  if (inputFields.length > 0) {
    const field = inputFields[inputFields.length - 1]; // Usually the last one
    if (field.tagName === 'TEXTAREA') {
      appendToTextarea(field, context);
    } else {
      field.textContent = (field.textContent || '') + '\n\n' + context;
    }
  } else {
    copyToClipboard(context);
    console.log('Claude: Copied context to clipboard');
  }
}

/**
 * Inject context into Google Gemini
 */
function injectGemini(capsule) {
  const context = formatCapsuleContext(capsule);
  
  // Find Gemini's input field
  const inputFields = document.querySelectorAll('div[contenteditable="true"], textarea');
  
  if (inputFields.length > 0) {
    const field = inputFields[inputFields.length - 1];
    if (field.tagName === 'TEXTAREA') {
      appendToTextarea(field, context);
    } else {
      field.textContent = (field.textContent || '') + '\n\n' + context;
    }
  } else {
    copyToClipboard(context);
    console.log('Gemini: Copied context to clipboard');
  }
}

/**
 * Generic injection (copies to clipboard)
 */
function injectGeneric(capsule) {
  const context = formatCapsuleContext(capsule);
  copyToClipboard(context);
  console.log('Generic: Copied context to clipboard');
}

/**
 * Format capsule context for injection
 * Truncates if exceeds AI site input limits
 */
function formatCapsuleContext(capsule) {
  // AI site input limits (characters)
  const LIMITS = {
    'openai.com': 32000,      // ChatGPT (with GPT-4)
    'claude.ai': 200000,       // Claude (very large)
    'gemini.google.com': 30720, // Gemini Pro
    'bing.com': 4000           // Bing Chat (conservative)
  };
  
  // Get appropriate limit for current site
  const hostname = window.location.hostname;
  let maxLength = 8000; // Conservative default
  for (const [site, limit] of Object.entries(LIMITS)) {
    if (hostname.includes(site)) {
      maxLength = limit;
      break;
    }
  }
  
  let context = `## 💊 Medicine Cabinet Context\n\n`;
  context += `**Project:** ${capsule.metadata.project}\n`;
  context += `**Summary:** ${capsule.metadata.summary || 'N/A'}\n`;
  
  if (capsule.metadata.branch) {
    context += `**Branch:** ${capsule.metadata.branch}\n`;
  }
  
  context += `**Created:** ${new Date(capsule.createdAt).toLocaleString()}\n\n`;

  // Extract useful sections with size tracking
  let sectionsContext = '';
  if (capsule.sections) {
    for (const section of capsule.sections) {
      if (section.name === 'task_objective' && section.payload) {
        sectionsContext += `**Task Objective:**\n${section.payload}\n\n`;
      } else if (section.name === 'relevant_files' && section.payload) {
        const files = Array.isArray(section.payload) ? section.payload : JSON.parse(section.payload);
        if (files.length > 0) {
          sectionsContext += `**Relevant Files:**\n`;
          // Limit to first 50 files
          const filesToShow = files.slice(0, 50);
          filesToShow.forEach(file => {
            sectionsContext += `- ${file}\n`;
          });
          if (files.length > 50) {
            sectionsContext += `... and ${files.length - 50} more files\n`;
          }
          sectionsContext += '\n';
        }
      } else if (section.name === 'working_plan' && section.payload) {
        sectionsContext += `**Working Plan:**\n${typeof section.payload === 'string' ? section.payload : JSON.stringify(section.payload, null, 2)}\n\n`;
      }
    }
  }
  
  context += sectionsContext;
  
  // Check if we need to truncate
  if (context.length > maxLength) {
    const overhead = 150; // Space for truncation message
    const truncateAt = maxLength - overhead;
    context = context.substring(0, truncateAt);
    context += `\n\n⚠️ *Context truncated (${context.length}/${maxLength} chars). Load smaller capsule or remove sections for full context.*`;
    console.warn(`Context truncated: ${context.length} chars exceeded ${maxLength} limit`);
  } else {
    console.log(`Context size: ${context.length}/${maxLength} chars`);
  }

  return context;
}

/**
 * Append text to a textarea
 */
function appendToTextarea(textarea, text) {
  const currentValue = textarea.value || '';
  textarea.value = currentValue + (currentValue ? '\n\n' : '') + text;
  
  // Trigger events to notify the page
  textarea.dispatchEvent(new Event('input', { bubbles: true }));
  textarea.dispatchEvent(new Event('change', { bubbles: true }));
  
  // Focus the textarea
  textarea.focus();
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    console.log('Context copied to clipboard');
  }).catch(err => {
    console.error('Failed to copy to clipboard:', err);
  });
}

/**
 * Show injection notification
 */
function showInjectionNotification(projectName) {
  const notification = document.createElement('div');
  notification.id = 'medicine-cabinet-notification';
  notification.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color: white;
      padding: 16px 24px;
      border-radius: 12px;
      box-shadow: 0 10px 25px rgba(99, 102, 241, 0.3);
      z-index: 999999;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 600;
      animation: slideIn 0.3s ease-out;
    ">
      💊 <strong>Context Injected:</strong> ${projectName}
    </div>
    <style>
      @keyframes slideIn {
        from {
          transform: translateX(400px);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
    </style>
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.transition = 'opacity 0.3s ease-out';
    notification.style.opacity = '0';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Request active capsule on load
browser.runtime.sendMessage({ action: 'getActiveCapsule' }, (response) => {
  if (response && response.capsule) {
    activeCapsule = response.capsule;
    console.log('Active capsule loaded:', activeCapsule);
  }
});
