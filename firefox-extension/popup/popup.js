/**
 * Medicine Cabinet - Popup UI Controller
 */

let capsules = [];
let tablets = [];
let sessions = [];
let activeCapsuleId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  loadMemoryData();
});

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // File input
  document.getElementById('file-input').addEventListener('change', handleFileSelect);

  // Tab switching
  document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => switchTab(button.dataset.tab));
  });

  // Auto-inject toggle
  document.getElementById('auto-inject-toggle').addEventListener('change', handleAutoInjectToggle);

  // Action buttons
  document.getElementById('inject-context-btn').addEventListener('click', injectContext);
  document.getElementById('refresh-btn').addEventListener('click', loadMemoryData);
  document.getElementById('clear-old-btn').addEventListener('click', clearOldMeds);
  document.getElementById('clear-all-btn').addEventListener('click', clearAllMeds);

  // Modal
  document.getElementById('close-modal').addEventListener('click', closeModal);
  document.getElementById('detail-modal').addEventListener('click', (e) => {
    if (e.target.id === 'detail-modal') closeModal();
  });

  // Help link
  document.getElementById('help-link').addEventListener('click', (e) => {
    e.preventDefault();
    showHelp();
  });

  // Load auto-inject preference
  browser.storage.local.get(['autoInjectEnabled'], (result) => {
    const enabled = result.autoInjectEnabled !== false; // Default true
    document.getElementById('auto-inject-toggle').checked = enabled;
  });
}

/**
 * Load memory data from background
 */
async function loadMemoryData() {
  try {
    const capsulesResponse = await browser.runtime.sendMessage({ action: 'getCapsules' });
    const tabletsResponse = await browser.runtime.sendMessage({ action: 'getTablets' });
    const sessionsResponse = await browser.runtime.sendMessage({ action: 'getSessions' });
    const activeResponse = await browser.runtime.sendMessage({ action: 'getActiveCapsule' });

    capsules = capsulesResponse.capsules || [];
    tablets = tabletsResponse.tablets || [];
    sessions = sessionsResponse.sessions || [];
    activeCapsuleId = activeResponse.capsule;

    renderCapsules();
    renderTablets();
    renderSessions();
    updateInjectButton();
  } catch (error) {
    console.error('Error loading memory data:', error);
    showNotification('Error loading data', 'error');
  }
}

/**
 * Handle file selection
 */
async function handleFileSelect(event) {
  const files = Array.from(event.target.files);
  
  for (const file of files) {
    try {
      const arrayBuffer = await file.arrayBuffer();
      const response = await browser.runtime.sendMessage({
        action: 'loadFile',
        file: {
          name: file.name,
          data: arrayBuffer
        }
      });

      if (response.success) {
        showNotification(`✓ Loaded ${file.name}`, 'success');
      } else {
        showNotification(`✗ Error loading ${file.name}: ${response.error}`, 'error');
      }
    } catch (error) {
      console.error('Error processing file:', error);
      showNotification(`✗ Error: ${error.message}`, 'error');
    }
  }

  // Clear input and reload
  event.target.value = '';
  setTimeout(loadMemoryData, 500);
}

/**
 * Render capsules list
 */
function renderCapsules() {
  const container = document.getElementById('capsules-list');
  const countEl = document.getElementById('capsules-count');
  
  countEl.textContent = capsules.length;

  if (capsules.length === 0) {
    container.innerHTML = '<p class="empty-state">No capsules loaded. Load a .auractx file to get started.</p>';
    return;
  }

  container.innerHTML = capsules.map(capsule => {
    const isActive = capsule.id === activeCapsuleId;
    return `
      <div class="memory-item ${isActive ? 'active' : ''}" data-id="${capsule.id}" data-type="capsule">
        <div class="memory-header">
          <div class="memory-title">${capsule.metadata.project || 'Untitled Capsule'}</div>
          <span class="memory-badge capsule">Capsule</span>
        </div>
        <div class="memory-info">${capsule.metadata.summary || 'No summary'}</div>
        <div class="memory-meta">
          <span>📦 ${capsule.sections.length} sections</span>
          <div class="memory-actions">
            ${!isActive ? `<button class="icon-btn" onclick="setActive('${capsule.id}')" title="Set as active">⭐</button>` : '<span title="Active">✓</span>'}
            <button class="icon-btn" onclick="viewDetails('${capsule.id}', 'capsule')" title="View details">👁️</button>
            <button class="icon-btn" onclick="removeMemory('${capsule.id}', 'capsule')" title="Remove">🗑️</button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Render tablets list
 */
function renderTablets() {
  const container = document.getElementById('tablets-list');
  const countEl = document.getElementById('tablets-count');
  
  countEl.textContent = tablets.length;

  if (tablets.length === 0) {
    container.innerHTML = '<p class="empty-state">No tablets loaded. Load a .auratab file to get started.</p>';
    return;
  }

  container.innerHTML = tablets.map(tablet => `
    <div class="memory-item" data-id="${tablet.id}" data-type="tablet">
      <div class="memory-header">
        <div class="memory-title">${tablet.metadata.title || 'Untitled Tablet'}</div>
        <span class="memory-badge tablet">Tablet</span>
      </div>
      <div class="memory-info">${tablet.metadata.description || 'No description'}</div>
      <div class="memory-meta">
        <span>📝 ${tablet.entries.length} entries</span>
        <div class="memory-actions">
          <button class="icon-btn" onclick="viewDetails('${tablet.id}', 'tablet')" title="View details">👁️</button>
          <button class="icon-btn" onclick="removeMemory('${tablet.id}', 'tablet')" title="Remove">🗑️</button>
        </div>
      </div>
    </div>
  `).join('');
}

/**
 * Render sessions list
 */
function renderSessions() {
  const container = document.getElementById('sessions-list');
  const countEl = document.getElementById('sessions-count');
  
  countEl.textContent = sessions.length;

  if (sessions.length === 0) {
    container.innerHTML = '<p class="empty-state">No sessions loaded yet.</p>';
    return;
  }

  container.innerHTML = sessions.map(session => {
    const typeIcon = session.type === 'capsule' ? '📦' : '📄';
    const typeBadge = session.type === 'capsule' ? 'capsule' : 'tablet';
    const loadedDate = new Date(session.loadedAt).toLocaleString();
    
    return `
      <div class="memory-item" data-id="${session.id}" data-type="session">
        <div class="memory-header">
          <div class="memory-title">${typeIcon} ${session.filename}</div>
          <span class="memory-badge ${typeBadge}">${session.type}</span>
        </div>
        <div class="memory-info">
          ${session.metadata.project || session.metadata.title || 'No title'}
        </div>
        <div class="memory-meta">
          <span>🕒 ${loadedDate}</span>
          <div class="memory-actions">
            <button class="icon-btn" onclick="viewSessionDetails('${session.id}')" title="View details">👁️</button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * Switch between tabs
 */
function switchTab(tabName) {
  // Update tab buttons
  document.querySelectorAll('.tab-button').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.tab === tabName);
  });

  // Update tab content
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.toggle('active', content.id === `${tabName}-tab`);
  });
}

/**
 * Set active capsule
 */
async function setActive(capsuleId) {
  try {
    await browser.runtime.sendMessage({
      action: 'setActiveCapsule',
      capsuleId
    });
    activeCapsuleId = capsuleId;
    renderCapsules();
    updateInjectButton();
    showNotification('✓ Active capsule updated', 'success');
  } catch (error) {
    console.error('Error setting active capsule:', error);
    showNotification('✗ Error updating active capsule', 'error');
  }
}

/**
 * Remove memory item
 */
async function removeMemory(id, type) {
  if (!confirm(`Remove this ${type}?`)) return;

  try {
    await browser.runtime.sendMessage({
      action: 'removeMemory',
      id,
      type
    });
    showNotification(`✓ ${type} removed`, 'success');
    loadMemoryData();
  } catch (error) {
    console.error('Error removing memory:', error);
    showNotification('✗ Error removing memory', 'error');
  }
}

/**
 * View details of a memory item
 */
function viewDetails(id, type) {
  const item = type === 'capsule' 
    ? capsules.find(c => c.id === id)
    : tablets.find(t => t.id === id);

  if (!item) return;

  const modal = document.getElementById('detail-modal');
  const title = document.getElementById('modal-title');
  const body = document.getElementById('modal-body');

  title.textContent = item.filename;

  if (type === 'capsule') {
    body.innerHTML = renderCapsuleDetails(item);
  } else {
    body.innerHTML = renderTabletDetails(item);
  }

  modal.classList.remove('hidden');
}

/**
 * View session details
 */
async function viewSessionDetails(sessionId) {
  try {
    const response = await browser.runtime.sendMessage({
      action: 'viewSession',
      sessionId
    });

    if (response.error) {
      showNotification('✗ Error loading session', 'error');
      return;
    }

    const session = response.session;
    const modal = document.getElementById('detail-modal');
    const title = document.getElementById('modal-title');
    const body = document.getElementById('modal-body');

    title.textContent = `Session: ${session.filename}`;

    if (session.type === 'capsule') {
      body.innerHTML = renderCapsuleDetails(session.data);
    } else {
      body.innerHTML = renderTabletDetails(session.data);
    }

    modal.classList.remove('hidden');
  } catch (error) {
    console.error('Error viewing session:', error);
    showNotification('✗ Error loading session', 'error');
  }
}

// Make function global for inline onclick
window.viewSessionDetails = viewSessionDetails;

/**
 * Render capsule details
 */
function renderCapsuleDetails(capsule) {
  let html = `
    <div class="detail-section">
      <h4>Metadata</h4>
      <pre>${JSON.stringify(capsule.metadata, null, 2)}</pre>
    </div>
  `;

  if (capsule.sections && capsule.sections.length > 0) {
    html += `
      <div class="detail-section">
        <h4>Sections (${capsule.sections.length})</h4>
        <ul class="detail-list">
          ${capsule.sections.map(section => `
            <li>
              <strong>${section.name}</strong> (${section.kindName})
              ${section.kind === 1 || section.kind === 2 ? `<pre>${typeof section.payload === 'string' ? section.payload : JSON.stringify(section.payload, null, 2)}</pre>` : `<span>${section.rawPayload.length} bytes</span>`}
            </li>
          `).join('')}
        </ul>
      </div>
    `;
  }

  return html;
}

/**
 * Render tablet details
 */
function renderTabletDetails(tablet) {
  let html = `
    <div class="detail-section">
      <h4>Metadata</h4>
      <pre>${JSON.stringify(tablet.metadata, null, 2)}</pre>
    </div>
  `;

  if (tablet.entries && tablet.entries.length > 0) {
    html += `
      <div class="detail-section">
        <h4>Entries (${tablet.entries.length})</h4>
        <ul class="detail-list">
          ${tablet.entries.map(entry => `
            <li>
              <strong>${entry.path}</strong>
              ${entry.notes ? `<div><em>Notes:</em> ${entry.notes}</div>` : ''}
              ${entry.diff ? `<pre>${entry.diff.substring(0, 500)}${entry.diff.length > 500 ? '...' : ''}</pre>` : ''}
            </li>
          `).join('')}
        </ul>
      </div>
    `;
  }

  return html;
}

/**
 * Close modal
 */
function closeModal() {
  document.getElementById('detail-modal').classList.add('hidden');
}

/**
 * Inject context into current tab
 */
async function injectContext() {
  try {
    const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
    await browser.runtime.sendMessage({
      action: 'injectContext',
      tabId: tab.id
    });
    showNotification('✓ Context injected', 'success');
  } catch (error) {
    console.error('Error injecting context:', error);
    showNotification('✗ Error injecting context', 'error');
  }
}

/**
 * Handle auto-inject toggle
 */
async function handleAutoInjectToggle(event) {
  const enabled = event.target.checked;
  
  // Save preference
  await browser.storage.local.set({ autoInjectEnabled: enabled });
  
  // Notify all tabs
  const tabs = await browser.tabs.query({});
  for (const tab of tabs) {
    try {
      await browser.tabs.sendMessage(tab.id, {
        action: 'toggleAutoInject',
        enabled
      });
    } catch (error) {
      // Tab may not have content script loaded, ignore
    }
  }
  
  showNotification(
    enabled ? '✓ Auto-inject enabled' : '✓ Auto-inject disabled',
    'success'
  );
}

/**
 * Update inject button state
 */
function updateInjectButton() {
  const btn = document.getElementById('inject-context-btn');
  btn.disabled = !activeCapsuleId;
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
  // Simple alert for now - could be enhanced with toast notifications
  console.log(`[${type}] ${message}`);
  
  // You could add a toast notification system here
  const existingToast = document.querySelector('.toast');
  if (existingToast) existingToast.remove();
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#6366f1'};
    color: white;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    z-index: 10000;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

/**
 * Show help
 */
function showHelp() {
  const modal = document.getElementById('detail-modal');
  const title = document.getElementById('modal-title');
  const body = document.getElementById('modal-body');

  title.textContent = 'Help & Usage';
  body.innerHTML = `
    <div class="detail-section">
      <h4>Getting Started</h4>
      <p>Medicine Cabinet helps you manage AI memory using Capsules and Tablets.</p>
      <ul>
        <li><strong>Capsules (.auractx)</strong>: Current project context and working memory</li>
        <li><strong>Tablets (.auratab)</strong>: Long-term memory of completed work</li>
      </ul>
    </div>
    
    <div class="detail-section">
      <h4>How to Use</h4>
      <ol>
        <li>Load capsule or tablet files using the file picker</li>
        <li>Set an active capsule (⭐ button)</li>
        <li>Navigate to supported sites (GitHub, Stack Overflow, AI chat)</li>
        <li>Click "Inject Active Context" to provide memory to the page</li>
      </ol>
    </div>

    <div class="detail-section">
      <h4>Supported Sites</h4>
      <ul>
        <li>GitHub</li>
        <li>Stack Overflow</li>
        <li>ChatGPT</li>
        <li>Claude AI</li>
        <li>Google Gemini</li>
      </ul>
    </div>

    <div class="detail-section">
      <h4>Learn More</h4>
      <p>Visit the <a href="https://github.com/hendrixx-cnc/Medicine-Cabinet" target="_blank">Medicine Cabinet repository</a> for documentation and tools.</p>
    </div>
  `;

  modal.classList.remove('hidden');
}

/**
 * Clear old medications
 */
async function clearOldMeds() {
  const daysOld = prompt('Clear medications older than how many days?', '7');
  
  if (daysOld === null) return; // User cancelled
  
  const days = parseInt(daysOld);
  if (isNaN(days) || days < 0) {
    showNotification('⚠️ Please enter a valid number of days', 'error');
    return;
  }

  try {
    const response = await browser.runtime.sendMessage({
      action: 'clearOldMeds',
      daysOld: days
    });

    if (response.success) {
      showNotification(
        `✓ Cleared ${response.removed.total} old medications (${response.removed.capsules} capsules, ${response.removed.tablets} tablets)`,
        'success'
      );
      loadMemoryData();
    } else {
      showNotification('✗ Error clearing old medications', 'error');
    }
  } catch (error) {
    console.error('Error clearing old meds:', error);
    showNotification('✗ Error clearing old medications', 'error');
  }
}

/**
 * Clear all medications
 */
async function clearAllMeds() {
  const confirmed = confirm(
    '⚠️ WARNING: This will delete ALL capsules, tablets, and sessions.\n\nThis action cannot be undone. Are you sure?'
  );

  if (!confirmed) return;

  try {
    const response = await browser.runtime.sendMessage({
      action: 'clearAllMeds'
    });

    if (response.success) {
      showNotification(
        `✓ Cleared all medications (${response.removed.capsules} capsules, ${response.removed.tablets} tablets)`,
        'success'
      );
      loadMemoryData();
    } else {
      showNotification('✗ Error clearing all medications', 'error');
    }
  } catch (error) {
    console.error('Error clearing all meds:', error);
    showNotification('✗ Error clearing all medications', 'error');
  }
}

// Make functions available globally for inline event handlers
window.setActive = setActive;
window.removeMemory = removeMemory;
window.viewDetails = viewDetails;
