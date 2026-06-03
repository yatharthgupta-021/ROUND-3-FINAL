// Team game controller

const teamName = document.getElementById('lbl-team-name').textContent.trim();
let ws = null;
let currentGameState = null;
let elapsedSeconds = 0;
let timerIntervalId = null;

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

// Node rendering layout settings (10x8 grid)
const gridPaddingX = 96;
const gridPaddingY = 108;
const gridSpacingX = 112;
const gridSpacingY = 112;

function getNodeCoords(node) {
    return {
        x: gridPaddingX + node.x * gridSpacingX,
        y: gridPaddingY + node.y * gridSpacingY
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
        
        // Start or sync local ticking interval if active
        if (data.game_status === 'active') {
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
    if (data.game_status === 'setup') {
        statusBadge.textContent = 'SETUP LOBBY';
        statusBadge.className = 'game-badge badge-setup';
        lobbyOverlay.style.display = 'flex';
    } else if (data.game_status === 'active') {
        statusBadge.textContent = 'MISSION RUNNING';
        statusBadge.className = 'game-badge badge-active';
        lobbyOverlay.style.display = 'none';
    } else if (data.game_status === 'ended') {
        statusBadge.textContent = 'MISSION COMPLETED';
        statusBadge.className = 'game-badge badge-ended';
        lobbyOverlay.style.display = 'none';
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
        clearanceVal.textContent = `Level: ${data.clearance_level}/${data.required_clearance} (${isUnlocked ? 'UNLOCKED' : 'LOCKED'})`;
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
        
        // Background Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'node-bg');
        circle.setAttribute('cx', coords.x);
        circle.setAttribute('cy', coords.y);
        circle.setAttribute('r', isCurrent ? '32' : '24');
        g.appendChild(circle);
        
        // Add text label
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('class', 'node-label');
        text.setAttribute('x', coords.x);
        text.setAttribute('y', coords.y + 7);
        text.textContent = node.id;
        g.appendChild(text);
        
        // Add landmark name label below circle
        const labelText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        labelText.setAttribute('class', 'node-name-label');
        labelText.setAttribute('x', coords.x);
        labelText.setAttribute('y', coords.y + 38);
        labelText.textContent = node.name;
        g.appendChild(labelText);
        
        // Tooltip text for location name
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = node.name;
        g.appendChild(title);
        
        // Add click events to move if adjacent
        if (isAdjacent && !data.is_eliminated && !data.found_sam && data.game_status === 'active') {
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
            pulse.setAttribute('r', '38');
            
            const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            core.setAttribute('class', 'beacon-core');
            core.setAttribute('cx', coords.x);
            core.setAttribute('cy', coords.y);
            core.setAttribute('r', '8');
            
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
    if (!currentGameState || currentGameState.game_status !== 'active') return;
    
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
            alert(`Decryption successful! Clue Unlocked: \n\n"${result.intel}"`);
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

// Rule Book Modal Toggle
const btnRules = document.getElementById('btn-rules');
const rulesModal = document.getElementById('rules-modal');
const btnCloseRules = document.getElementById('btn-close-rules');

console.log("Rule Book elements check:", { btnRules, rulesModal, btnCloseRules });

if (btnRules && rulesModal && btnCloseRules) {
    btnRules.addEventListener('click', () => {
        console.log("Rule Book opened");
        rulesModal.classList.add('active');
    });
    btnCloseRules.addEventListener('click', () => {
        console.log("Rule Book closed");
        rulesModal.classList.remove('active');
    });
    rulesModal.addEventListener('click', (e) => {
        if (e.target === rulesModal) {
            console.log("Rule Book closed by background click");
            rulesModal.classList.remove('active');
        }
    });
} else {
    console.error("Rule Book elements missing from DOM!");
}

// Initialise Connect
fetchState();
connectWebSocket();
