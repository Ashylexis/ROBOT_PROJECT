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
            grid-template-columns: repeat(3, 1fr) 0.5fr;
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
 
    <div class="status-bar">
        <span>X: <b id="valX">0</b></span>
        <span>Y: <b id="valY">0</b></span>
        <span>R: <b id="valR">0°</b></span>
    </div>
 
    <div id="debug" class="debug">Bereit</div>
 
</div>
 
<script>
let currentPreset = null;
 
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
 
    fetch('http://192.168.4.1/', {
        method: 'POST',
        body: 'cmd=' + cmd
    })
    .then(function(response) { return response.text(); })
    .then(function(data) {
        document.getElementById('debug').innerText = "OK: " + data;
        let parts = data.split('|');
        if (parts.length === 3) {
            document.getElementById('valX').innerText = parts[0];
            document.getElementById('valY').innerText = parts[1];
            document.getElementById('valR').innerText = parts[2] + "°";
        }
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
 
function sendSlider(val) {
    document.getElementById('debug').innerText = "Slider: " + val;
    fetch('http://192.168.4.1/', {
        method: 'POST',
        body: 'slider=' + val
    })
    .then(function(response) { return response.text(); })
    .then(function(data) {
        document.getElementById('debug').innerText = "OK: " + data;
        let parts = data.split('|');
        if (parts.length === 3) {
            document.getElementById('valR').innerText = parts[2] + "°";
        }
    })
    .catch(function(error) {
        document.getElementById('debug').innerText = "FEHLER: " + error;
    });
}
</script>
 
</body>
</html>
"""