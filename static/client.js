let previous = new Map();
const removalTimers = new Map();

function esc(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }[character]));
}

function readableText(hex) {
    const value = String(hex || '').replace('#', '');

    if (!/^[0-9a-fA-F]{6}$/.test(value)) {
        return '#fff';
    }

    const red = parseInt(value.slice(0, 2), 16);
    const green = parseInt(value.slice(2, 4), 16);
    const blue = parseInt(value.slice(4, 6), 16);

    const luminance = (
        .2126 * red +
        .7152 * green +
        .0722 * blue
    ) / 255;

    return luminance > .55 ? '#111827' : '#fff';
}

function textPanelStyle(hex) {
    const value = String(hex || '').replace('#', '');

    if (!/^[0-9a-fA-F]{6}$/.test(value)) {
        return {
            background: '#111827',
            color: '#ffffff',
        };
    }

    const red = parseInt(value.slice(0, 2), 16);
    const green = parseInt(value.slice(2, 4), 16);
    const blue = parseInt(value.slice(4, 6), 16);

    const brightness = (
        0.2126 * red +
        0.7152 * green +
        0.0722 * blue
    );

    return brightness > 150
        ? { background: '#111827', color: '#ffffff' }
        : { background: '#f8fafc', color: '#111827' };
}

function entryClass(display) {
    return display.entry_direction === 'from_top'
        ? 'enter-top'
        : 'enter-bottom';
}

function exitClass(display) {
    return display.exit_direction === 'to_top'
        ? 'exit-top'
        : 'exit-bottom';
}

function gridSize(count) {
    if (count <= 1) {
        return [1, 1];
    }

    let rows = 1;
    let columns = 1;

    while (rows * columns < count) {
        if (columns === rows) {
            columns++;
        } else {
            rows++;
        }
    }

    return [rows, columns];
}

function renderBattleRound(state) {
    const initiative = document.querySelector('#initiative');

    if (!initiative) {
        return;
    }

    initiative.querySelector('.round-indicator')?.remove();

    const round = state?.battle_round;
    const active = Number.isInteger(round) && round >= 1;

    if (!active) {
        return;
    }

    const indicator = document.createElement('span');
    indicator.className = 'round-indicator';
    indicator.textContent = `Round ${round}`;
    indicator.setAttribute('aria-label', `Battle round ${round}`);

    initiative.prepend(indicator);
    initiative.hidden = false;
}

function effectBadges(combatant) {
    return (combatant.effects||[]).map(e=>`<span class="effect-badge">${esc(e.name)}</span>`).join(' ');
}
function renderClientCampaign(state) {
    const element=document.querySelector('#clientCampaign');if(!element)return;
    const name=state?.campaign?.name;element.textContent=name?'Campaign: '+name:'No active campaign';element.title=name||'';
}
function render(state) {
    renderClientCampaign(state);
    applyBattleOrderFontSize(state.display);

    const background = String(
        state.display?.background || '#080b14'
    ).trim() || '#080b14';

    // Reset the previous background, then apply the current one.
    document.body.style.background = '#080b14';

    if (background.startsWith('url(')) {
        document.body.style.backgroundImage = background;
        document.body.style.backgroundPosition = 'center center';
        document.body.style.backgroundSize = 'cover';
        document.body.style.backgroundRepeat = 'no-repeat';
        document.body.style.backgroundAttachment = 'fixed';
    } else {
        // Supports solid colors and CSS gradients.
        document.body.style.background = background;
    }

    const combatantsById = new Map(
        [...state.characters, ...state.monsters]
            .map(combatant => [combatant.id, combatant]),
    );

    const displayOrder = state.display_order ?? state.battle_order;

    const initiativeCombatants = displayOrder
        .map(id => combatantsById.get(id))
        .filter(combatant =>
            combatant && combatant.active && combatant.visible,
        );

    const initiative = document.querySelector('#initiative');

    initiative.hidden = initiativeCombatants.length === 0;

    function displayCombatantName(combatant) {
        return combatant.monster_species && combatant.ally
            ? `${combatant.name} - Ally`
            : combatant.name;
    }

    initiative.innerHTML = initiativeCombatants.map(combatant =>
        `<span class="token ${combatant.life_state==='dead'?'dead':(!combatant.alive?'down':'')} ${combatant.in_turn ? 'turn' : ''}"
        style="background:${esc(combatant.color)};color:${readableText(combatant.color)}">
        ${esc(displayCombatantName(combatant))} ${!combatant.alive?' ('+esc(combatant.life_state||'down')+')':''} ${effectBadges(combatant)}
    </span>`
    ).join('');

    renderBattleRound(state);

    const activeMonsters = state.monsters.filter(monster =>
        monster.active&&(monster.alive||['down','stable'].includes(monster.life_state)),
    );

    const stage = document.querySelector('#stage');

    if (!activeMonsters.length) {
        for (const timer of removalTimers.values()) {
            clearTimeout(timer);
        }
        removalTimers.clear();
        stage.style.gridTemplateColumns = '';
        stage.style.gridTemplateRows = '';
        stage.innerHTML = '<div class="empty"></div>';
        previous.clear();
        return;
    }

    stage.querySelectorAll(".empty").forEach(element => element.remove());

    const [rows, columns] = gridSize(activeMonsters.length);

    stage.style.gridAutoFlow = 'row';
    stage.style.gridTemplateColumns =
        `repeat(${columns}, minmax(0, 1fr))`;
    stage.style.gridTemplateRows =
        `repeat(${rows}, minmax(0, 1fr))`;
    stage.style.setProperty(
        '--grid-scale',
        String(Math.max(rows, columns)),
    );

    const current = new Map(
        activeMonsters.map(monster => [monster.id, monster]),
    );

    for (const [id] of previous) {
        if (current.has(id)) {
            continue;
        }

        const oldCard = document.getElementById(`m-${id}`);

        if (oldCard && !removalTimers.has(id)) {
            oldCard.classList.add(exitClass(state.display));

            const timer = setTimeout(() => {
                oldCard.remove();
                removalTimers.delete(id);
            }, 750);

            removalTimers.set(id, timer);
        }
    }

    activeMonsters.forEach((monster, index) => {
        if (removalTimers.has(monster.id)) {
            clearTimeout(removalTimers.get(monster.id));
            removalTimers.delete(monster.id);
        }

        let card = document.getElementById(`m-${monster.id}`);

        if (!card) {
            card = document.createElement('article');
            card.id = `m-${monster.id}`;
            card.className = `monster ${entryClass(state.display)}`;
            stage.appendChild(card);

            requestAnimationFrame(() => {
                card.classList.remove('enter-bottom', 'enter-top');
            });
        }

        card.classList.remove("exit-top", "exit-bottom");
        card.classList.toggle("down",!monster.alive);

        const row = Math.floor(index / columns) + 1;
        const column = (index % columns) + 1;

        card.style.gridRow = String(row);
        card.style.gridColumn = String(column);
        card.style.color = monster.color;

        const panel = textPanelStyle(monster.color);
        card.style.setProperty('--text-panel-background', panel.background);
        card.style.setProperty('--text-panel-color', panel.color);

        const stats = [];

        if (monster.show_ac) {
            stats.push(`AC ${monster.ac}`);
        }

        if (monster.show_hp) {
            stats.push(`HP ${monster.hp}/${monster.max_hp}${monster.temp_hp?" + "+monster.temp_hp+" temporary":""}`);
        }

        if (monster.show_initiative && monster.initiative !== null) {
            stats.push(`Initiative ${monster.initiative}`);
        }

        card.innerHTML = `
        ${monster.image_url ? `<img src="${esc(monster.image_url)}" alt="">` : ''}
        <div class="text-panel">
        <h1>${esc(displayCombatantName(monster))}${monster.in_turn ? ' ◀' : ''}</h1>
        <div class="type">${esc(monster.monster_species)}</div>
        <div class="stats">${stats.join(' · ')}</div>
        <div>${!monster.alive?esc(monster.life_state||"down"):""} ${effectBadges(monster)}</div>
        </div>
    `;

    });

    previous = current;
}

function connectDisplay() {
    let socket=null,retryTimer=null,attempt=0,stopped=false;
    let lastSeen=Date.now(),lastRevision=null,lastSnapshot=null,resyncPending=false;
    const indicator=document.querySelector('#displaySync');
    const status=text=>{if(indicator)indicator.textContent=text;};
    function send(message) {
        if(socket?.readyState===WebSocket.OPEN)socket.send(JSON.stringify(message));
    }
    function resync() {
        if(!resyncPending&&socket?.readyState===WebSocket.OPEN){resyncPending=true;send({type:'resync'});}
    }
    function scheduleReconnect() {
        if(stopped||retryTimer!==null)return;
        const delay=Math.min(30000,1000*2**Math.min(attempt++,5));
        status('Reconnecting… (last display retained)');
        retryTimer=setTimeout(()=>{retryTimer=null;open();},delay+Math.floor(Math.random()*250));
    }
    async function checkSignIn() {
        try {
            const response=await fetch('/api/state',{cache:'no-store'});
            if(response.status===401){stopped=true;location.assign('/login');return false;}
        }catch(error){console.debug('Unable to check display session',error);}
        return true;
    }
    function open() {
        if(stopped||socket?.readyState===WebSocket.OPEN||socket?.readyState===WebSocket.CONNECTING)return;
        status(lastSnapshot===null?'Connecting…':'Reconnecting… (last display retained)');
        try {
            socket=new WebSocket(`${location.protocol==='https:'?'wss://':'ws://'}${location.host}/ws`);
        }catch(error){console.warn('Unable to open display WebSocket',error);scheduleReconnect();return;}
        const current=socket;
        resyncPending=false;
        current.onopen=()=>{if(socket===current){lastSeen=Date.now();status('Connected · synchronizing…');}};
        current.onmessage=event=>{
            if(socket!==current||stopped)return;
            let message;
            try{message=JSON.parse(event.data);}catch(error){console.warn('Invalid display WebSocket JSON',error);return;}
            lastSeen=Date.now();
            if(message?.type==='heartbeat') {
                send({type:'pong',revision:lastRevision});
                if(message.revision!==lastRevision){status('Connected · synchronizing…');resync();}
                else status('Live · checked '+new Date().toLocaleTimeString());
                return;
            }
            if(message?.type!=='state'||!message.state)return;
            try {
                const snapshot=JSON.stringify(message.state);
                // A reconnect must not rebuild an unchanged stage or reload its images.
                if(snapshot!==lastSnapshot){render(message.state);lastSnapshot=snapshot;}
                lastRevision=message.revision;resyncPending=false;attempt=0;
                status('Live · updated '+new Date().toLocaleTimeString());
                send({type:'ack',revision:lastRevision});
            }catch(error){console.error('Display state render failed',error);status('Display update failed; retained last screen');}
        };
        current.onclose=async event=>{
            if(socket!==current||stopped)return;
            console.info('Display WebSocket closed',{code:event.code,reason:event.reason,clean:event.wasClean});
            status('Disconnected · last display retained');
            if(event.code===1008&&!(await checkSignIn()))return;
            if(socket!==current||stopped)return;
            scheduleReconnect();
        };
        current.onerror=()=>{
            if(socket===current)console.warn('Display WebSocket transport error; waiting for close/reconnect');
        };
    }
    function resume() {
        if(stopped||document.hidden)return;
        if(socket?.readyState===WebSocket.OPEN){send({type:'ping'});resync();}
        else if(socket?.readyState!==WebSocket.CONNECTING){
            if(retryTimer!==null){clearTimeout(retryTimer);retryTimer=null;}open();
        }
    }
    const statusTimer=setInterval(()=>{
        // A late JS timer may label the screen stale, but must not close a healthy socket.
        if(!stopped&&!document.hidden&&socket?.readyState===WebSocket.OPEN&&Date.now()-lastSeen>45000)
            status('Waiting for server · last display retained');
    },10000);
    document.addEventListener('visibilitychange',resume);
    window.addEventListener('online',resume);
    open();
    return {resync,close(){stopped=true;clearInterval(statusTimer);if(retryTimer!==null)clearTimeout(retryTimer);document.removeEventListener('visibilitychange',resume);window.removeEventListener('online',resume);socket?.close();}};
}

const websocket = connectDisplay();

function applyBattleOrderFontSize(display) {
    const requestedSize = Number(
        display?.battle_order_font_size ?? 16,
    );

    const size = Number.isInteger(requestedSize)
        ? Math.max(12, Math.min(40, requestedSize))
        : 16;

    document.documentElement.style.setProperty(
        '--battle-order-font-size',
        `${size}px`,
    );
}