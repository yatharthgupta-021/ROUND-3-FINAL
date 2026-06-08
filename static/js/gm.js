// Game Master controller

let ws = null;
let currentGameState = null;
let elapsedSeconds = 0;
let timerIntervalId = null;
let pathRecording = [];

// DOM Elements
const statusBadge = document.getElementById('game-status-badge');
const samCoordsBox = document.getElementById('sam-coords-box');
const diagonalChk = document.getElementById('diagonal_allowed');
const samStaticChk = document.getElementById('sam_static');
const samIntervalInput = document.getElementById('sam_interval');
const samPathInput = document.getElementById('sam_path_input');
const recordPathChk = document.getElementById('chk-record-path');
const btnForceSamMove = document.getElementById('btn-force-sam-move');
const btnResetGame = document.getElementById('btn-reset-game');

const teamsTelemetryGrid = document.getElementById('teams-telemetry-grid');
const leaderboardBody = document.getElementById('leaderboard-body');

// SVG Elements
const mapSvg = document.getElementById('map-svg');
const mapLinksGroup = document.getElementById('map-links-group');
const mapNodesGroup = document.getElementById('map-nodes-group');
const samMarkerGroup = document.getElementById('sam-marker-group');
const teamsMarkersGroup = document.getElementById('teams-markers-group');

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
        const response = await fetch('/api/gm/state');
        if (response.ok) {
            const data = await response.json();
            handleStateUpdate(data);
        }
    } catch (err) {
        console.error('Error fetching GM state:', err);
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
    const wsUrl = `${protocol}//${host}/ws/gm`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket GM connection established.');
        stopPolling();
    };
    
    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === 'state_update') {
            handleStateUpdate(msg.data);
        } else if (msg.type === 'winner_announcement') {
            console.log('Winner announced:', msg.winners);
        }
    };
    
    ws.onerror = (err) => {
        console.error('WebSocket GM error:', err);
        startPolling();
    };
    
    ws.onclose = () => {
        console.log('WebSocket GM connection closed. Retrying in 3 seconds...');
        startPolling();
        setTimeout(connectWebSocket, 3000);
    };
}

function formatDuration(totalSeconds) {
    if (totalSeconds === undefined || isNaN(totalSeconds)) return '00:00';
    const mins = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
    const secs = (totalSeconds % 60).toString().padStart(2, '0');
    return `${mins}:${secs}`;
}

function updateTimerDisplay(totalSeconds) {
    const timerVal = document.getElementById('val-timer');
    if (timerVal) {
        timerVal.textContent = formatDuration(totalSeconds);
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
                    
                    // Increment each active team's duration locally every second and re-render grid
                    if (currentGameState && currentGameState.teams) {
                        let updated = false;
                        Object.keys(currentGameState.teams).forEach(teamName => {
                            const team = currentGameState.teams[teamName];
                            if (!team.found_sam && !team.is_eliminated) {
                                team.elapsed_seconds = (team.elapsed_seconds || 0) + 1;
                                updated = true;
                            }
                        });
                        if (updated) {
                            renderTelemetry(currentGameState);
                        }
                    }
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
        statusBadge.textContent = 'SETUP MODE';
        statusBadge.className = 'game-badge badge-setup';
        enableConfigControls(true);
    } else if (data.game_status === 'active') {
        statusBadge.textContent = 'MISSION ACTIVE';
        statusBadge.className = 'game-badge badge-active';
        enableConfigControls(false);
    } else if (data.game_status === 'ended') {
        statusBadge.textContent = 'MISSION ENDED';
        statusBadge.className = 'game-badge badge-ended';
        enableConfigControls(false);
    }
    
    // Sync configurations to form fields
    if (document.activeElement !== diagonalChk) {
        diagonalChk.checked = data.diagonal_allowed;
    }
    if (document.activeElement !== samStaticChk) {
        samStaticChk.checked = data.sam_static;
    }
    if (document.activeElement !== samIntervalInput) {
        samIntervalInput.value = data.sam_movement_interval;
    }
    if (data.game_status === 'setup' && !recordPathChk.checked && document.activeElement !== samPathInput) {
        samPathInput.value = data.sam_path.join(',');
    }
    
    // Display Sam coordinates and countdown
    if (data.sam_coords) {
        let text = `SAM TARGET: ${data.sam_coords.name} (X:${data.sam_coords.x}, Y:${data.sam_coords.y})`;
        if (data.game_status === 'active' && !data.sam_static) {
            const timeLeft = Math.max(0, data.sam_movement_interval - data.seconds_since_sam_move);
            text += ` [Move in: ${timeLeft}s]`;
        }
        samCoordsBox.textContent = text;
    } else {
        samCoordsBox.textContent = 'SAM TARGET: OFF-GRID';
    }
    
    // Render Operatives Telemetry list
    renderTelemetry(data);
    
    // Render Winners Leaderboard
    renderLeaderboard(data.winners);
    
    // Draw Map UI
    renderMap(data);
}

function enableConfigControls(enable) {
    diagonalChk.disabled = false;
    samStaticChk.disabled = false;
    samIntervalInput.disabled = false;
    samPathInput.disabled = !enable;
    recordPathChk.disabled = !enable;
}

function renderTelemetry(data) {
    teamsTelemetryGrid.innerHTML = '';
    const teams = Object.entries(data.teams || {});
    
    if (teams.length === 0) {
        teamsTelemetryGrid.innerHTML = '<p style="color: var(--text-secondary); font-size: 13px;">No operative teams registered.</p>';
        return;
    }
    
    teams.forEach(([name, details]) => {
        const card = document.createElement('div');
        let cardClass = 'team-status-card';
        if (details.found_sam) cardClass += ' found';
        else if (details.is_eliminated) cardClass += ' eliminated';
        card.className = cardClass;
        
        let statusText = 'IN PLAY';
        let statusColor = 'var(--neon-blue)';
        if (details.found_sam) {
            statusText = 'FOUND SAM';
            statusColor = 'var(--neon-green)';
        } else if (details.is_eliminated) {
            statusText = 'ELIMINATED';
            statusColor = 'var(--neon-pink)';
        }
        
        card.innerHTML = `
            <div class="team-card-header">
                <span class="team-card-title">${name} ${details.is_online ? '<span class="status-dot online" style="color: var(--neon-green); margin-left: 6px; font-size: 14px; text-shadow: var(--shadow-glow-green);" title="Online">●</span>' : '<span class="status-dot offline" style="color: #555; margin-left: 6px; font-size: 14px;" title="Offline">●</span>'}</span>
                <span style="font-size: 11px; font-weight: 700; color: ${statusColor}; text-transform: uppercase;">${statusText}</span>
            </div>
            <div class="team-card-meta">
                <span>Landmark: <strong>${getLandmarkName(details.current_node)} (Node ${details.current_node})</strong></span>
                <span>Tix: <strong>${details.tickets}</strong></span>
            </div>
            <div class="team-card-meta" style="margin-top: 4px;">
                <span>Time: <strong>${formatDuration(details.elapsed_seconds)}</strong></span>
                <span>Decrypted: <strong>${details.puzzles_solved_count}</strong></span>
            </div>
            <div class="team-card-meta" style="margin-top: 4px;">
                <span>Moves: <strong>${details.history.length - 1}</strong></span>
            </div>
        `;
        teamsTelemetryGrid.appendChild(card);
    });
}

function renderLeaderboard(winners) {
    leaderboardBody.innerHTML = '';
    if (!winners || winners.length === 0) {
        leaderboardBody.innerHTML = `
            <tr>
                <td colspan="4" style="color: var(--text-secondary); text-align: center;">No finishes logged yet.</td>
            </tr>
        `;
        return;
    }
    
    winners.forEach((winner, idx) => {
        const tr = document.createElement('tr');
        tr.className = `leaderboard-row ${idx === 0 ? 'winner' : ''}`;
        
        let rankText = `#${idx + 1}`;
        if (idx === 0) rankText = '🥇 WINNER';
        else if (idx === 1) rankText = '🥈 2nd';
        else if (idx === 2) rankText = '🥉 3rd';
        
        tr.innerHTML = `
            <td>${rankText}</td>
            <td><strong>${winner.team_name}</strong></td>
            <td>${winner.duration_seconds}s</td>
            <td>${winner.tickets_left}</td>
        `;
        leaderboardBody.appendChild(tr);
    });
}

// Render dynamic map layout in SVG
// Render dynamic map layout in SVG
function renderMap(data) {
    mapLinksGroup.innerHTML = '';
    mapNodesGroup.innerHTML = '';
    samMarkerGroup.innerHTML = '';
    teamsMarkersGroup.innerHTML = '';
    
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
        
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        let classes = 'map-node';
        
        // Is this node in Sam's path?
        const isSamPath = data.sam_path && data.sam_path.includes(node.id);
        if (isSamPath) classes += ' visited';
        
        g.setAttribute('class', classes);
        g.setAttribute('id', `node-${node.id}`);
        
        // Background Circle
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('class', 'node-bg');
        circle.setAttribute('cx', coords.x);
        circle.setAttribute('cy', coords.y);
        circle.setAttribute('r', '24');
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
        
        // Click event for recording Sam's path (Only in setup mode)
        g.addEventListener('click', () => {
            if (data.game_status === 'setup' && recordPathChk.checked) {
                handleNodePathClick(node.id);
            }
        });
        
        mapNodesGroup.appendChild(g);
    });
    
    // Draw Sam's position (pulsating red beacon)
    if (data.sam_current_node !== undefined) {
        const samNode = nodesById[data.sam_current_node];
        if (samNode) {
            const coords = getNodeCoords(samNode);
            
            const beaconGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            beaconGroup.setAttribute('class', 'beacon beacon-sam');
            
            const pulse = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            pulse.setAttribute('class', 'beacon-pulse');
            pulse.setAttribute('cx', coords.x);
            pulse.setAttribute('cy', coords.y);
            pulse.setAttribute('r', '38');
            
            const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            core.setAttribute('class', 'beacon-core');
            core.setAttribute('cx', coords.x);
            core.setAttribute('cy', coords.y);
            core.setAttribute('r', '9');
            
            // Sam text overlay
            const samText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            samText.setAttribute('class', 'sam-label');
            samText.setAttribute('x', coords.x);
            samText.setAttribute('y', coords.y - 34);
            samText.textContent = 'SAM';
            
            beaconGroup.appendChild(pulse);
            beaconGroup.appendChild(core);
            beaconGroup.appendChild(samText);
            samMarkerGroup.appendChild(beaconGroup);
        }
    }
    
    // Draw all teams (small offset dots)
    const teams = Object.entries(data.teams || {});
    // Group teams by node ID to calculate offset spacing
    const nodeTeams = {};
    teams.forEach(([name, details]) => {
        const nid = details.current_node;
        if (!nodeTeams[nid]) nodeTeams[nid] = [];
        nodeTeams[nid].push({ name, details });
    });
    
    Object.entries(nodeTeams).forEach(([nid_str, teamItems]) => {
        const nid = parseInt(nid_str);
        const node = nodesById[nid];
        if (node) {
            const baseCoords = getNodeCoords(node);
            
            teamItems.forEach(({ name, details }, idx) => {
                // Calculate spiral offset if multiple teams occupy same node
                let offset_x = 0;
                let offset_y = 0;
                if (teamItems.length > 1) {
                    const angle = (idx * (2 * Math.PI)) / teamItems.length;
                    offset_x = Math.cos(angle) * 18;
                    offset_y = Math.sin(angle) * 18;
                }
                
                let dotColor = 'var(--neon-blue)';
                let dotFilter = 'drop-shadow(var(--shadow-glow-blue))';
                
                if (details.found_sam) {
                    dotColor = 'var(--neon-green)';
                    dotFilter = 'drop-shadow(var(--shadow-glow-green))';
                } else if (details.is_eliminated) {
                    dotColor = 'var(--neon-pink)';
                    dotFilter = 'drop-shadow(var(--shadow-glow-red))';
                } else if (!details.is_online) {
                    dotColor = '#7a828a';
                    dotFilter = 'none';
                }
                
                const teamDot = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                teamDot.setAttribute('cx', baseCoords.x + offset_x);
                teamDot.setAttribute('cy', baseCoords.y + offset_y);
                teamDot.setAttribute('r', '7');
                teamDot.setAttribute('fill', dotColor);
                teamDot.setAttribute('stroke', '#fff');
                teamDot.setAttribute('stroke-width', '1.5');
                if (dotFilter !== 'none') {
                    teamDot.setAttribute('filter', dotFilter);
                }
                
                // Text tooltip
                const tooltip = document.createElementNS('http://www.w3.org/2000/svg', 'title');
                tooltip.textContent = `${name} (${details.is_online ? 'Online' : 'Offline'})`;
                teamDot.appendChild(tooltip);
                
                // Add label abbreviation text
                const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                label.setAttribute('class', 'teams-marker-label');
                label.setAttribute('x', baseCoords.x + offset_x);
                label.setAttribute('y', baseCoords.y + offset_y - 10);
                label.textContent = name.substring(0, 3).toUpperCase();
                
                teamsMarkersGroup.appendChild(teamDot);
                teamsMarkersGroup.appendChild(label);
            });
        }
    });
}

function drawLink(coordsA, coordsB, isDiagonal, idA, idB, data) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    let classes = 'map-link';
    if (isDiagonal) classes += ' diagonal';
    
    line.setAttribute('class', classes);
    line.setAttribute('x1', coordsA.x);
    line.setAttribute('y1', coordsA.y);
    line.setAttribute('x2', coordsB.x);
    line.setAttribute('y2', coordsB.y);
    mapLinksGroup.appendChild(line);
}

// Config field handlers
async function postConfigure() {
    if (!currentGameState) return;
    
    // Parse Sam's path array
    const pathString = samPathInput.value.trim();
    const pathArray = pathString ? pathString.split(',').map(x => parseInt(x.trim())).filter(x => !isNaN(x) && x >= 0 && x < 80) : [];
    
    const configData = {
        diagonal_allowed: diagonalChk.checked,
        sam_static: samStaticChk.checked,
        sam_start_node: pathArray[0] !== undefined ? pathArray[0] : 35,
        sam_movement_interval: parseInt(samIntervalInput.value) || 90,
        sam_path: pathArray,
        puzzles: currentGameState.puzzles || [],
        node_names: {} // Keep current names
    };
    
    try {
        const response = await fetch('/api/gm/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(configData)
        });
        const result = await response.json();
        if (response.ok) {
            console.log('Configurations applied successfully.');
        } else {
            console.error('Configure error:', result.message);
        }
    } catch (err) {
        console.error('Network configure error:', err);
    }
}

// Attach configuration listeners
[diagonalChk, samStaticChk].forEach(el => {
    el.addEventListener('change', postConfigure);
});
[samIntervalInput, samPathInput].forEach(el => {
    el.addEventListener('blur', postConfigure);
});

function getAdjacentNodes(nodeId) {
    if (!currentGameState || !currentGameState.links) return [];
    const adjacent = [];
    currentGameState.links.forEach(link => {
        if (link.source === nodeId) adjacent.push(link.target);
        if (link.target === nodeId) adjacent.push(link.source);
    });
    return adjacent;
}

// Click map nodes to draw Sam's path
function handleNodePathClick(nodeId) {
    if (!recordPathChk.checked) return;
    
    if (pathRecording.length === 0) {
        pathRecording.push(nodeId);
    } else {
        // Only allow adjacent track/spur connections next to the previous node
        const prevNodeId = pathRecording[pathRecording.length - 1];
        const adjacent = getAdjacentNodes(prevNodeId);
        
        if (adjacent.includes(nodeId) || nodeId === prevNodeId) {
            pathRecording.push(nodeId);
        } else {
            alert("Error: Sam can only move to adjacent nodes. Custom step ignored.");
            return;
        }
    }
    
    samPathInput.value = pathRecording.join(',');
    postConfigure();
}

// Toggle record path checkbox
recordPathChk.addEventListener('change', (e) => {
    if (e.target.checked) {
        pathRecording = [];
        samPathInput.value = '';
        console.log('Path recording mode active. Click adjacent map nodes in order.');
    } else {
        postConfigure();
    }
});

// Game actions events

btnForceSamMove.addEventListener('click', () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: 'move_sam_now' }));
    }
});

btnResetGame.addEventListener('click', async () => {
    if (!confirm('Are you sure you want to abort the current operation and clear the network?')) return;
    
    try {
        const response = await fetch('/api/gm/reset', { method: 'POST' });
        if (response.ok) {
            pathRecording = [];
            recordPathChk.checked = false;
            console.log('Network reset completed.');
        }
    } catch (err) {
        console.error(err);
    }
});

function getLandmarkName(id) {
    if (currentGameState && currentGameState.map_nodes) {
        const node = currentGameState.map_nodes.find(n => n.id === id);
        if (node) return node.name;
    }
    return `Location ${id}`;
}

// Start
fetchState();
connectWebSocket();
// Periodic timer tick update for countdown display in title box
setInterval(() => {
    if (currentGameState && currentGameState.game_status === 'active' && !currentGameState.sam_static) {
        currentGameState.seconds_since_sam_move = (currentGameState.seconds_since_sam_move || 0) + 1;
        
        let text = `SAM TARGET: ${currentGameState.sam_coords.name} (X:${currentGameState.sam_coords.x}, Y:${currentGameState.sam_coords.y})`;
        const timeLeft = Math.max(0, currentGameState.sam_movement_interval - currentGameState.seconds_since_sam_move);
        text += ` [Move in: ${timeLeft}s]`;
        samCoordsBox.textContent = text;
    }
}, 1000);
