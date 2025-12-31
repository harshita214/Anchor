/**
 * Anchor Frontend Application
 * Real-time context continuity for dementia care
 */

const API_BASE = 'http://localhost:5000/api';
const POLL_INTERVAL = 2000;

// DOM Elements
const confusedBtn = document.getElementById('confusedBtn');
const explanationSection = document.getElementById('explanationSection');
const explanationText = document.getElementById('explanationText');
const statusMessage = document.getElementById('statusMessage');
const backendStatus = document.getElementById('backendStatus');
const eventLog = document.getElementById('eventLog');

// State
let isLoading = false;
let pollInterval = null;
let eventHistory = [];

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('[Anchor] Initializing...');
    
    confusedBtn.addEventListener('click', handleConfusedClick);
    
    checkBackendConnection();
    startPollingState();
    startPollingEvents();
});

// ============================================================================
// Event Simulation (for demo)
// ============================================================================

async function simulateEvent(type, action, value) {
    try {
        let topic, payload;
        
        if (type === 'presence') {
            topic = 'anchor-presence-events';
            payload = { action, person: value };
        } else if (type === 'call') {
            topic = 'anchor-call-events';
            payload = { action, caller: value };
        } else if (type === 'location') {
            topic = 'anchor-location-events';
            payload = { location: value };
        } else if (type === 'time') {
            topic = 'anchor-time-events';
            payload = { time_of_day: value };
        }
        
        const response = await fetch(`${API_BASE}/events/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, payload })
        });
        
        const data = await response.json();
        if (data.success) {
            console.log('[Anchor] Event simulated:', topic);
            addEventToLog(topic, payload);
        }
    } catch (error) {
        console.error('[Anchor] Error simulating event:', error);
    }
}

async function addPerson() {
    const name = document.getElementById('personName').value;
    const role = document.getElementById('personRole').value;
    
    if (!name) {
        showStatus('Please enter a name', 'error');
        return;
    }
    
    const person = role ? `${name} (${role})` : name;
    await simulateEvent('presence', 'enter', person);
    
    document.getElementById('personName').value = '';
    document.getElementById('personRole').value = '';
}

async function removePerson() {
    const name = document.getElementById('personName').value;
    const role = document.getElementById('personRole').value;
    
    if (!name) {
        showStatus('Please enter a name', 'error');
        return;
    }
    
    const person = role ? `${name} (${role})` : name;
    await simulateEvent('presence', 'leave', person);
    
    document.getElementById('personName').value = '';
    document.getElementById('personRole').value = '';
}

// ============================================================================
// Event Log Display
// ============================================================================

function addEventToLog(topic, payload) {
    const time = new Date().toLocaleTimeString();
    const eventType = payload.action || payload.time_of_day || payload.location || 'event';
    
    eventHistory.unshift({
        time,
        topic,
        type: eventType,
        payload
    });
    
    // Keep only last 10 events
    if (eventHistory.length > 10) {
        eventHistory.pop();
    }
    
    updateEventLog();
}

function updateEventLog() {
    if (eventHistory.length === 0) {
        eventLog.innerHTML = '<div class="event-log-item" style="color: var(--text-light);">Waiting for events...</div>';
        return;
    }
    
    eventLog.innerHTML = eventHistory.map(event => `
        <div class="event-log-item">
            <span class="event-time">[${event.time}]</span>
            <span class="event-type">${event.topic.replace('anchor-', '').replace('-events', '')}</span>:
            ${event.type}
        </div>
    `).join('');
}

async function startPollingEvents() {
    // Poll for new events every 2 seconds
    setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/history?limit=1`);
            const data = await response.json();
            
            if (data.success && data.events.length > 0) {
                const latestEvent = data.events[0];
                // Only add if not already in log
                if (!eventHistory.some(e => e.time === latestEvent.timestamp)) {
                    addEventToLog(latestEvent.topic, latestEvent.payload);
                }
            }
        } catch (error) {
            console.error('[Anchor] Error polling events:', error);
        }
    }, 1000);
}

// ============================================================================
// Backend Communication
// ============================================================================

async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            setBackendStatus('connected', 'Connected');
            console.log('[Anchor] Backend connected');
        } else {
            setBackendStatus('error', 'Backend error');
        }
    } catch (error) {
        setBackendStatus('error', 'Disconnected');
        console.error('[Anchor] Backend connection failed:', error);
    }
}

async function getState() {
    try {
        const response = await fetch(`${API_BASE}/state`);
        if (!response.ok) throw new Error('Failed to fetch state');
        return await response.json();
    } catch (error) {
        console.error('[Anchor] Error fetching state:', error);
        return null;
    }
}

async function requestExplanation() {
    try {
        isLoading = true;
        confusedBtn.classList.add('loading');
        confusedBtn.disabled = true;
        
        showStatus('Grounding you...', 'info');
        
        const response = await fetch(`${API_BASE}/explain`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to get explanation');
        
        const data = await response.json();
        
        if (data.success) {
            displayExplanation(data.explanation);
            showStatus('Here\'s what\'s happening right now.', 'success');
        } else {
            showStatus('Could not generate explanation. Please try again.', 'error');
        }
    } catch (error) {
        console.error('[Anchor] Error requesting explanation:', error);
        showStatus('Something went wrong. Please try again.', 'error');
    } finally {
        isLoading = false;
        confusedBtn.classList.remove('loading');
        confusedBtn.disabled = false;
    }
}

// ============================================================================
// UI Updates
// ============================================================================

function updateStateDisplay(state) {
    if (!state) return;
    
    document.getElementById('location').textContent = state.location || 'home';
    document.getElementById('time').textContent = state.time_of_day || 'now';
    
    const peopleList = state.people_present || [];
    const peopleText = peopleList.length > 0 
        ? peopleList.join(', ')
        : 'no one';
    document.getElementById('people').textContent = peopleText;
    
    const callItem = document.getElementById('call-item');
    if (state.call_active_with) {
        callItem.style.display = 'flex';
        document.getElementById('call').textContent = state.call_active_with;
    } else {
        callItem.style.display = 'none';
    }
}

function displayExplanation(text) {
    explanationText.textContent = text;
    explanationSection.style.display = 'block';
    explanationSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showStatus(message, type = 'info') {
    statusMessage.textContent = message;
    statusMessage.className = `status-message ${type}`;
    statusMessage.style.display = 'block';
    
    setTimeout(() => {
        statusMessage.style.display = 'none';
    }, 5000);
}

function setBackendStatus(status, text) {
    backendStatus.textContent = text;
    backendStatus.className = status;
}

// ============================================================================
// Event Handlers
// ============================================================================

function handleConfusedClick() {
    if (isLoading) return;
    requestExplanation();
}

// ============================================================================
// Polling
// ============================================================================

function startPollingState() {
    getState().then(updateStateDisplay);
    
    pollInterval = setInterval(() => {
        getState().then(updateStateDisplay);
    }, POLL_INTERVAL);
}

function stopPollingState() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

window.addEventListener('beforeunload', stopPollingState);
