// Team game controller

const teamName = document.getElementById('lbl-team-name').textContent.trim();
let ws = null;
let currentGameState = null;
let elapsedSeconds = 0;
let timerIntervalId = null;
let winModalShown = false;

// DOM Elements
const ticketsVal = document.getElementById('val-tickets');
const ticketsCard = document.getElementById('card-tickets');
const locationVal = document.getElementById('val-location');
const historyList = document.getElementById('list-history');
const cluesList = document.getElementById('list-clues');
const statusBadge = document.getElementById('game-status-badge');
const lobbyOverlay = document.getElementById('lobby-overlay');
const puzzleModal = document.getElementById('puzzle-modal');
const puzzleQuestion = document.getElementById('puzzle-question');
const puzzleAnswerInput = document.getElementById('puzzle-answer');
const puzzleError = document.getElementById('puzzle-error');
const puzzleForm = document.getElementById('puzzle-form');
const btnBypassPuzzle = document.getElementById('btn-bypass-puzzle');
const winnerOverlay = document.getElementById('winner-overlay');
const leaderboardBody = document.getElementById('leaderboard-body');

// SVG Elements
const mapSvg = document.getElementById('map-svg');
const mapLinksGroup = document.getElementById('map-links-group');
const mapNodesGroup = document.getElementById('map-nodes-group');
const playerMarkerGroup = document.getElementById('player-marker-group');

// Node rendering: custom_map coords (x: 0-64, y: 0-50) mapped to
// the background image canvas (1092 x 1092 SVG viewBox)
const MAP_X_MAX = 64;   // max x coord in custom_map.json
const MAP_Y_MAX = 50;   // max y coord in custom_map.json
const SVG_W = 1092;
const SVG_H = 1092;
const MAP_PAD = 12;     // pixel padding so edge nodes don't touch border

function getNodeCoords(node) {
    return {
        x: MAP_PAD + (node.x / MAP_X_MAX) * (SVG_W - MAP_PAD * 2),
        y: MAP_PAD + (node.y / MAP_Y_MAX) * (SVG_H - MAP_PAD * 2)
    };
}

let isPolling = false;
let pollingIntervalId = null;

async function fetchState() {
    try {
        const response = await fetch(`/api/team/state/${encodeURIComponent(teamName)}`);
        if (response.ok) {
            const data = await response.json();
            handleStateUpdate(data);
        }
    } catch (err) {
        console.error('Error fetching team state:', err);
    }
}

function startPolling() {
    if (isPolling) return;
    isPolling = true;
    console.log('WebSocket down. Starting HTTP polling fallback...');
    pollingIntervalId = setInterval(fetchState, 2000);
}

function stopPolling() {
    if (!isPolling) return;
    isPolling = false;
    console.log('WebSocket restored. Stopping HTTP polling fallback.');
    if (pollingIntervalId) {
        clearInterval(pollingIntervalId);
        pollingIntervalId = null;
    }
}

// Establish Web Socket Connection
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/team/${encodeURIComponent(teamName)}`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket connection established.');
        stopPolling();
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'state_update') {
            handleStateUpdate(msg.data);
        } else if (msg.type === 'winner_announcement') {
            showWinnerOverlay(msg.winners);
        }
    };
    
    ws.onerror = (err) => {
        console.error('WebSocket error:', err);
        startPolling();
    };
    
    ws.onclose = () => {
        console.log('WebSocket connection closed. Retrying in 3 seconds...');
        startPolling();
        setTimeout(connectWebSocket, 3000);
    };
}

function updateTimerDisplay(totalSeconds) {
    const mins = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const secs = (totalSeconds % 60).toString().padStart(2, '0');
    const timerVal = document.getElementById('val-timer');
    if (timerVal) {
        timerVal.textContent = `${mins}:${secs}`;
    }
}

function handleStateUpdate(data) {
    currentGameState = data;
    
    // Update elapsed timer HUD
    if (data.elapsed_seconds !== undefined) {
        elapsedSeconds = data.elapsed_seconds;
        updateTimerDisplay(elapsedSeconds);
        
        // Start or sync local ticking interval if active and team is still playing
        if (data.game_status === 'active' && data.started && !data.found_sam && !data.is_eliminated) {
            if (!timerIntervalId) {
                timerIntervalId = setInterval(() => {
                    elapsedSeconds += 1;
                    updateTimerDisplay(elapsedSeconds);
                }, 1000);
            }
        } else {
            if (timerIntervalId) {
                clearInterval(timerIntervalId);
                timerIntervalId = null;
            }
        }
    }
    
    // Update Badge Status
    if (data.game_status === 'ended') {
        statusBadge.textContent = 'MISSION COMPLETED';
        statusBadge.className = 'game-badge badge-ended';
        lobbyOverlay.style.display = 'none';
    } else if (!data.started) {
        statusBadge.textContent = 'SETUP LOBBY';
        statusBadge.className = 'game-badge badge-setup';
        lobbyOverlay.style.display = 'flex';
    } else {
        statusBadge.textContent = 'MISSION RUNNING';
        statusBadge.className = 'game-badge badge-active';
        lobbyOverlay.style.display = 'none';
    }
    
    // Trigger Win Modal
    if (data.found_sam && !winModalShown) {
        winModalShown = true;
        const winModal = document.getElementById('win-modal');
        const winFinalTime = document.getElementById('win-final-time');
        const winFinalTickets = document.getElementById('win-final-tickets');
        if (winFinalTime) {
            const mins = Math.floor(data.elapsed_seconds / 60).toString().padStart(2, '0');
            const secs = (data.elapsed_seconds % 60).toString().padStart(2, '0');
            winFinalTime.textContent = `${mins}:${secs}`;
        }
        if (winFinalTickets) {
            winFinalTickets.textContent = data.tickets;
        }
        if (winModal) {
            winModal.classList.add('active');
        }
    }
    
    // Update Operative stats
    ticketsVal.textContent = data.tickets;
    if (data.is_eliminated) {
        ticketsVal.textContent = 'OUT';
        ticketsCard.style.borderColor = 'var(--neon-pink)';
        ticketsVal.style.color = 'var(--neon-pink)';
        ticketsVal.style.textShadow = '0 0 10px rgba(255, 0, 127, 0.4)';
    } else if (data.found_sam) {
        ticketsCard.style.borderColor = 'var(--neon-green)';
        ticketsVal.style.color = 'var(--neon-green)';
        ticketsVal.style.textShadow = '0 0 10px rgba(57, 255, 20, 0.4)';
    } else {
        ticketsCard.style.borderColor = 'var(--border-color)';
        ticketsVal.style.color = 'var(--neon-blue)';
        ticketsVal.style.textShadow = 'var(--shadow-glow-blue)';
    }
    
    // Update Clearance Level HUD
    const clearanceVal = document.getElementById('val-clearance');
    if (clearanceVal && data.clearance_level !== undefined) {
        const isUnlocked = data.clearance_level >= data.required_clearance;
        clearanceVal.textContent = `Level: ${data.clearance_level} (${isUnlocked ? 'UNLOCKED' : 'LOCKED'})`;
        if (isUnlocked) {
            clearanceVal.style.color = 'var(--neon-green)';
            clearanceVal.style.borderColor = 'rgba(57, 255, 20, 0.3)';
            clearanceVal.style.background = 'rgba(57, 255, 20, 0.05)';
            clearanceVal.style.textShadow = 'var(--shadow-glow-green)';
        } else {
            clearanceVal.style.color = 'var(--neon-purple)';
            clearanceVal.style.borderColor = 'rgba(189, 0, 255, 0.3)';
            clearanceVal.style.background = 'rgba(189, 0, 255, 0.05)';
            clearanceVal.style.textShadow = 'var(--shadow-glow-purple)';
        }
    }
    
    // Set location labels
    if (data.current_node !== undefined && data.map_nodes) {
        const currentNodeObj = data.map_nodes.find(n => n.id === data.current_node);
        locationVal.textContent = currentNodeObj ? currentNodeObj.name : `Node ${data.current_node}`;
    }
    
    // Render History Logs
    historyList.innerHTML = '';
    if (data.history && data.history.length > 0) {
        // Reverse to show most recent first
        [...data.history].reverse().forEach(nodeName => {
            const li = document.createElement('li');
            li.className = 'log-item';
            li.textContent = nodeName;
            historyList.appendChild(li);
        });
    }
    
    // Render Clues Inventory
    cluesList.innerHTML = '';
    if (data.clues && data.clues.length > 0) {
        [...data.clues].reverse().forEach(clue => {
            const li = document.createElement('li');
            li.className = `clue-item ${clue.type || 'system'}`;
            li.textContent = clue.text;
            cluesList.appendChild(li);
        });
    } else {
        cluesList.innerHTML = '<li class="clue-item system">Dossier initialized. Gather coordinates to trace Sam.</li>';
    }
    
    // Trigger Decrypter Puzzle Modal
    if (data.active_puzzle) {
        puzzleQuestion.textContent = data.active_puzzle.question;
        puzzleError.style.display = 'none';
        puzzleAnswerInput.value = '';
        puzzleModal.classList.add('active');
    } else {
        puzzleModal.classList.remove('active');
    }
    
    // Draw Map UI
    renderMap(data);
    
    // Auto-trigger winner overlay if leaderboard is active
    if (data.winners && data.winners.length > 0) {
        showWinnerOverlay(data.winners);
    }
}

// Render dynamic map layout in SVG
function renderMap(data) {
    mapLinksGroup.innerHTML = '';
    mapNodesGroup.innerHTML = '';
    playerMarkerGroup.innerHTML = '';
    
    const nodes = data.map_nodes || [];
    const nodesById = {};
    nodes.forEach(node => {
        nodesById[node.id] = node;
    });
    
    // Render Connections (Links)
    const links = data.links || [];
    links.forEach(link => {
        const nodeA = nodesById[link.source];
        const nodeB = nodesById[link.target];
        if (nodeA && nodeB) {
            drawLink(getNodeCoords(nodeA), getNodeCoords(nodeB), link.is_diagonal, link.source, link.target, data);
        }
    });
    
    // Render Nodes (Circles)
    nodes.forEach(node => {
        const coords = getNodeCoords(node);
        const isCurrent = (node.id === data.current_node);
        const isAdjacent = data.adjacent_nodes && data.adjacent_nodes.includes(node.id);
        
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        let classes = 'map-node';
        if (isCurrent) classes += ' current-location';
        if (isAdjacent) classes += ' adjacent';
        g.setAttribute('class', classes);
        g.setAttribute('id', `node-${node.id}`);
        
        // Background Circle (smaller for dense map)
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'node-bg');
        circle.setAttribute('cx', coords.x);
        circle.setAttribute('cy', coords.y);
        circle.setAttribute('r', isCurrent ? '18' : '14');
        g.appendChild(circle);
        
        // Add text label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('class', 'node-label');
        text.setAttribute('x', coords.x);
        text.setAttribute('y', coords.y + 4);
        text.textContent = node.id;
        g.appendChild(text);
        
        // Tooltip text for location name (on hover)
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${node.name}`;
        g.appendChild(title);
        
        // Add click events to move if adjacent
        if (isAdjacent && !data.is_eliminated && !data.found_sam && data.game_status === 'active' && data.started) {
            g.addEventListener('click', () => handleMove(node.id));
        }
        
        mapNodesGroup.appendChild(g);
    });
    
    // Draw Current Position Pulsating Beacon
    if (data.current_node !== undefined) {
        const currNode = nodesById[data.current_node];
        if (currNode) {
            const coords = getNodeCoords(currNode);
            
            const beaconGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            beaconGroup.setAttribute('class', 'beacon beacon-team');
            
            const pulse = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            pulse.setAttribute('class', 'beacon-pulse');
            pulse.setAttribute('cx', coords.x);
            pulse.setAttribute('cy', coords.y);
            pulse.setAttribute('r', '22');
            
            const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            core.setAttribute('class', 'beacon-core');
            core.setAttribute('cx', coords.x);
            core.setAttribute('cy', coords.y);
            core.setAttribute('r', '5');
            
            beaconGroup.appendChild(pulse);
            beaconGroup.appendChild(core);
            playerMarkerGroup.appendChild(beaconGroup);
        }
    }
}

function drawLink(coordsA, coordsB, isDiagonal, idA, idB, data) {
    // Only draw diagonal links if diagonal is allowed in game state
    if (isDiagonal && !data.diagonal_nodes_allowed) return;
    
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    let classes = 'map-link';
    if (isDiagonal) classes += ' diagonal';
    
    // Check if line was walked by team
    const teamHistory = data.history_nodes || []; // We can check if path traveled
    
    line.setAttribute('class', classes);
    line.setAttribute('x1', coordsA.x);
    line.setAttribute('y1', coordsA.y);
    line.setAttribute('x2', coordsB.x);
    line.setAttribute('y2', coordsB.y);
    mapLinksGroup.appendChild(line);
}

// Move Team via API call
async function handleMove(nodeId) {
    if (!currentGameState || currentGameState.game_status !== 'active' || !currentGameState.started) return;
    
    try {
        const response = await fetch('/api/team/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                team_name: teamName,
                target_node: nodeId
            })
        });
        const result = await response.json();
        if (response.ok) {
            console.log('Move successful:', result);
        } else {
            alert(result.detail || 'Movement denied.');
        }
    } catch (err) {
        console.error('Error posting move:', err);
    }
}

// Solve Puzzle Form submission
puzzleForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const answer = puzzleAnswerInput.value.trim();
    if (!answer) return;
    
    try {
        const response = await fetch('/api/team/solve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                team_name: teamName,
                answer: answer
            })
        });
        const result = await response.json();
        if (response.ok && result.success) {
            puzzleModal.classList.remove('active');
            showIntelModal(result.intel);
        } else {
            puzzleError.textContent = result.message || 'Incorrect decryption key.';
            puzzleError.style.display = 'block';
        }
    } catch (err) {
        console.error('Error solving puzzle:', err);
        puzzleError.textContent = 'Communication failure. Try again.';
        puzzleError.style.display = 'block';
    }
});

// ── Intel Success Modal ──────────────────────────────────────────────────────
const intelModal        = document.getElementById('intel-modal');
const intelClueList     = document.getElementById('intel-clue-list');
const intelClearanceBdg = document.getElementById('intel-clearance-badge');
const btnCloseIntel     = document.getElementById('btn-close-intel');

function showIntelModal(intelText) {
    // Parse the intel text
    // Expected format: "🔒 Decrypted Intel (Clearance Level: X):\n- clue1\n- clue2\n- clue3"
    intelClueList.innerHTML = '';

    const lines = intelText.split('\n');
    let clearanceText = 'Clearance Level Updated';
    const clueLines = [];

    lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith('🔒')) {
            // Extract clearance level e.g. "Clearance Level: 2"
            const match = trimmed.match(/Clearance Level:?\s*(\d+)/i);
            if (match) clearanceText = `Clearance Level ${match[1]} Unlocked`;
        } else if (trimmed.startsWith('-')) {
            clueLines.push(trimmed.replace(/^-\s*/, ''));
        }
    });

    if (intelClearanceBdg) intelClearanceBdg.textContent = clearanceText;

    clueLines.forEach(clue => {
        const li = document.createElement('li');
        li.className = 'intel-clue-item';
        li.textContent = clue;
        intelClueList.appendChild(li);
    });

    if (intelModal) intelModal.classList.add('active');
}

if (btnCloseIntel) {
    btnCloseIntel.addEventListener('click', () => {
        intelModal.classList.remove('active');
    });
}
if (intelModal) {
    intelModal.addEventListener('click', e => {
        if (e.target === intelModal) intelModal.classList.remove('active');
    });
}

// Bypass/Close Puzzle Modal
btnBypassPuzzle.addEventListener('click', async () => {
    try {
        await fetch('/api/team/bypass', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ team_name: teamName })
        });
        puzzleModal.classList.remove('active');
    } catch (err) {
        console.error('Error bypassing puzzle:', err);
    }
});

// Show final leaderboard overlays
function showWinnerOverlay(winners) {
    leaderboardBody.innerHTML = '';
    winners.forEach((winner, idx) => {
        const tr = document.createElement('tr');
        tr.className = `leaderboard-row ${idx === 0 ? 'winner' : ''}`;
        
        let rankText = `#${idx + 1}`;
        if (idx === 0) rankText = '🥇 WINNER';
        else if (idx === 1) rankText = '🥈 2nd';
        else if (idx === 2) rankText = '🥉 3rd';
        
        const isCurrentTeam = winner.team_name === teamName;
        const teamDisplayName = isCurrentTeam ? `${winner.team_name} (You)` : winner.team_name;
        
        tr.innerHTML = `
            <td>${rankText}</td>
            <td style="${isCurrentTeam ? 'font-weight: bold; color: var(--neon-blue);' : ''}">${teamDisplayName}</td>
            <td>${winner.duration_seconds}s</td>
            <td>${winner.tickets_left} tickets</td>
        `;
        leaderboardBody.appendChild(tr);
    });
    
    winnerOverlay.style.display = 'flex';
}

function getLandmarkName(id) {
    if (currentGameState && currentGameState.map_nodes) {
        const node = currentGameState.map_nodes.find(n => n.id === id);
        if (node) return node.name;
    }
    return `Location ${id}`;
}

// ── Rule Book Modal ──────────────────────────────────────────────────────────
const btnRules     = document.getElementById('btn-rules');
const rulesModal   = document.getElementById('rules-modal');
const btnCloseRules = document.getElementById('btn-close-rules');

if (btnRules && rulesModal && btnCloseRules) {
    btnRules.addEventListener('click', () => rulesModal.classList.add('active'));
    btnCloseRules.addEventListener('click', () => rulesModal.classList.remove('active'));
    rulesModal.addEventListener('click', e => {
        if (e.target === rulesModal) rulesModal.classList.remove('active');
    });
}

// ── Circuit Map Popup ─────────────────────────────────────────────────────────
const btnCircuitMap     = document.getElementById('btn-circuit-map');
const mapPopup          = document.getElementById('map-popup');
const btnCloseMapPopup  = document.getElementById('btn-close-map-popup');

if (btnCircuitMap && mapPopup) {
    btnCircuitMap.addEventListener('click', () => mapPopup.classList.add('active'));
    btnCloseMapPopup.addEventListener('click', () => mapPopup.classList.remove('active'));
    mapPopup.addEventListener('click', e => {
        if (e.target === mapPopup) mapPopup.classList.remove('active');
    });
}

// ── Start Mission Button ──────────────────────────────────────────────────────
const btnStartMission = document.getElementById('btn-start-mission');

if (btnStartMission) {
    btnStartMission.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/team/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ team_name: teamName })
            });
            if (response.ok) {
                console.log('Mission started successfully');
            } else {
                const errorData = await response.json();
                alert(errorData.detail || 'Failed to start mission.');
            }
        } catch (err) {
            console.error('Error starting mission:', err);
            alert('Connection error. Please try again.');
        }
    });
}

// ── Win Success Modal ─────────────────────────────────────────────────────────
const btnCloseWin = document.getElementById('btn-close-win');
const winModalEl = document.getElementById('win-modal');

if (btnCloseWin && winModalEl) {
    btnCloseWin.addEventListener('click', () => {
        winModalEl.classList.remove('active');
    });
}

// Initialise Connect
fetchState();
connectWebSocket();
