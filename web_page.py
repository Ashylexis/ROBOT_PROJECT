# file: web_page.py
 
def webpage():
    return """<!DOCTYPE html>
<html lang="de">
 
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pico Robot Control</title>
 
    <style>
        body {
            font-family: sans-serif;
            display: flex;
            justify-content: center;
            background: #f0f0f0;
        }
 
        .container {
            width: 350px;
            border: 2px solid #800080;
            background: white;
            padding: 10px;
        }
 
        .header {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            border-bottom: 2px solid #800080;
            margin-bottom: 10px;
        }
 
        .header button {
            padding: 10px;
            border: 1px solid #ccc;
            background: none;
            cursor: pointer;
        }
 
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 10px;
            align-items: center;
            text-align: center;
        }
 
        .servo-btns {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
 
        .circle-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            border: 2px solid #800080;
            background: white;
            cursor: pointer;
        }
 
        .slider-container {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
 
        input[type=range][orient=vertical] {
            writing-mode: bt-lr;
            -webkit-appearance: slider-vertical;
            width: 20px;
            height: 150px;
        }
 
        .control-panel {
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1.5fr 1fr;
            gap: 5px;
            align-items: center;
        }
 
        .state-panel {
            margin-top: 20px;
            padding: 10px;
            border: 1px solid #800080;
            border-radius: 8px;
            background: #faf4ff;
        }

        .state-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-bottom: 10px;
        }

        .state-box {
            padding: 12px;
            border: 2px solid #800080;
            border-radius: 8px;
            background: white;
            font-weight: bold;
        }

        .state-box.active {
            background: #f5d7ff;
            box-shadow: 0 0 0 3px rgba(128, 0, 128, 0.15);
        }

        .transition-list {
            font-size: 0.85em;
            line-height: 1.4;
        }

        .transition-list span {
            display: block;
            margin-bottom: 4px;
        }
 
        .arrows-h, .arrows-v {
            display: flex;
            border: 1px solid #800080;
        }
 
        .arrows-v {
            flex-direction: column;
        }
 
        .start-btn {
            height: 50px;
            font-weight: bold;
            border: 2px solid #800080;
            background: white;
            cursor: pointer;
        }
 
        .status-bar {
            margin-top: 15px;
            display: flex;
            justify-content: space-around;
            font-size: 0.9em;
            border-top: 1px solid #ccc;
            padding-top: 5px;
        }
 
        .debug {
            margin-top: 5px;
            font-size: 0.8em;
            color: red;
            text-align: center;
        }
    </style>
</head>
 
<body>
 
<div class="container">
 
    <div class="header">
        <button onclick="sendCommand('p1')">P1</button>
        <button onclick="sendCommand('p2')">P2</button>
        <button onclick="sendCommand('p3')">P3</button>
        <button onclick="sendCommand('load_guns')">L</button>
        <button onclick="sendCommand('reset_all')" style="color:red">R</button>
    </div>
 
    <div class="main-grid">
 
        <div class="servo-btns">
            <button class="circle-btn" onclick="sendCommand('s1')">S1</button>
            <button class="circle-btn" onclick="sendCommand('s2')">S2</button>
        </div>
 
        <div class="slider-container">
            <span>90°</span>
            <input type="range" min="0" max="90" value="0"
                   orient="vertical" onchange="sendSlider(this.value)">
            <span>0°</span>
            <button onclick="sendSlider(0)">R</button>
        </div>
 
        <div class="servo-btns">
            <button class="circle-btn" onclick="sendCommand('s3')">S3</button>
            <button class="circle-btn" onclick="sendCommand('s4')">S4</button>
        </div>
 
    </div>
 
    <div class="control-panel">
        <div class="arrows-h">
            <button onclick="sendCommand('left')">←</button>
            <button onclick="sendCommand('right')">→</button>
        </div>
        <button class="start-btn" onclick="sendCommand('start')">START</button>
        <div class="arrows-v">
            <button onclick="sendCommand('up')">↑</button>
            <button onclick="sendCommand('down')">↓</button>
        </div>
    </div>

    <div class="state-panel">
        <div class="state-grid">
            <div class="state-box" id="state-startup">Startup</div>
            <div class="state-box" id="state-idle">Idle</div>
            <div class="state-box" id="state-loading_guns">Loading Guns</div>
            <div class="state-box" id="state-fight">Fight</div>
            <div class="state-box" id="state-finished">Finished</div>
        </div>
        <div class="transition-list">
            <span>Startup → Idle</span>
            <span>Idle → Loading Guns</span>
            <span>Idle → Fight</span>
            <span>Loading Guns → Idle</span>
            <span>Fight → Finished</span>
            <span>Finished → Idle</span>
        </div>
    </div>

    <div class="status-bar">
        <span>X: <b id="valX">0</b></span>
        <span>Y: <b id="valY">0</b></span>
        <span>R: <b id="valR">0°</b></span>
    </div>
 
    <div id="debug" class="debug">Bereit</div>
 
</div>
 
<script>
let currentPreset = null;
const baseUrl = window.location.origin;
 
function sendCommand(cmd) {
    console.log("Sending:", cmd);
    document.getElementById('debug').innerText = "Sende: " + cmd;
 
    // Preset-Button markieren
    if (cmd === 'p1' || cmd === 'p2' || cmd === 'p3') {
        ['p1', 'p2', 'p3'].forEach(id => {
            let btn = document.querySelector("button[onclick=\\"sendCommand('" + id + "')\\"]");
            if (btn) btn.style.background = "white";
        });
        let activeBtn = document.querySelector("button[onclick=\\"sendCommand('" + cmd + "')\\"]");
        if (activeBtn) activeBtn.style.background = "#dfafff";
        currentPreset = cmd;
    }
 
    // Reset-Button Feedback
    if (cmd === 'reset_all') {
        let rBtn = document.querySelector("button[onclick=\\"sendCommand('reset_all')\\"]");
        if (rBtn) {
            rBtn.style.background = "red";
            setTimeout(function() { rBtn.style.background = ""; }, 300);
        }
    }
 
    fetch(baseUrl + '/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({cmd: cmd})
    })
    .then(function(response) { return response.text(); })
    .then(function(data) {
        if (cmd !== 'status') {
            document.getElementById('debug').innerText = "OK";
        }
        updateStatus(data, cmd === 'status');
        if (cmd === 'start') {
            ['p1', 'p2', 'p3'].forEach(id => {
                let btn = document.querySelector("button[onclick=\\"sendCommand('" + id + "')\\"]");
                if (btn) btn.style.background = "white";
            });
        }
    })
    .catch(function(error) {
        document.getElementById('debug').innerText = "FEHLER: " + error;
        console.error('Fehler:', error);
    });
}
 
function setActiveState(state) {
    document.querySelectorAll('.state-box').forEach(function(box) {
        box.classList.remove('active');
    });
    var active = document.getElementById('state-' + state);
    if (active) {
        active.classList.add('active');
    }
}

function updateStatus(data, suppressDebug) {
    let parts = data.split('|');
    if (parts.length === 4) {
        var state = parts[0];
        var x = parts[1];
        var y = parts[2];
        var r = parts[3];
        document.getElementById('valX').innerText = x;
        document.getElementById('valY').innerText = y;
        document.getElementById('valR').innerText = r + "°";
        setActiveState(state);
        if (!suppressDebug) {
            document.getElementById('debug').innerText = "Status: " + state;
        }
    } else if (parts.length === 3) {
        document.getElementById('valX').innerText = parts[0];
        document.getElementById('valY').innerText = parts[1];
        document.getElementById('valR').innerText = parts[2] + "°";
    }
}

function sendSlider(val) {
    document.getElementById('debug').innerText = "Slider: " + val;
    fetch(baseUrl + '/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({slider: val})
    })
    .then(function(response) { return response.text(); })
    .then(function(data) {
        updateStatus(data, true);
    })
    .catch(function(error) {
        document.getElementById('debug').innerText = "FEHLER: " + error;
    });
}

function pollStatus() {
    fetch(baseUrl + '/', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({cmd: 'status'})
    })
    .then(function(response) { return response.text(); })
    .then(function(data) {
        updateStatus(data, true);
        setTimeout(pollStatus, 1000);
    })
    .catch(function(error) {
        document.getElementById('debug').innerText = "FEHLER: " + error;
        setTimeout(pollStatus, 3000);
    });
}

pollStatus();
</script>
 
</body>
</html>
"""