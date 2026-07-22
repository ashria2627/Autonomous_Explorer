from flask import Flask, render_template_string, jsonify, request
import time

app = Flask(__name__)

robots = {}

@app.route('/update', methods=['POST'])
def update():
    """Receiver ESP32 posts data here"""
    try:
        raw = request.form.get('data', '')
        # Parse: ID:BOT-001,CO:123,AIR:456,TEMP:32,HUM:60,STATUS:NORMAL
        parts = raw.split(',')
        data = {"last_seen": time.strftime("%H:%M:%S"), "cam_ip": None}
        for p in parts:
            if ':' in p:
                k, v = p.split(':', 1)
                data[k.strip()] = v.strip()
        bot_id = data.get('ID', 'BOT-001')
        data['id'] = bot_id
        robots[bot_id] = data
        return 'OK', 200
    except Exception as e:
        return str(e), 400

@app.route('/data')
def data():
    return jsonify(robots)

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Autonomous Explorer</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#f5efeb;--text:#454545;--heading:#2f4156;
  --card:#ffffff;--border:#e0d8d2;
  --danger:#c0392b;--safe:#27ae60;
  --shadow:0 2px 20px rgba(47,65,86,0.08);
}
body{font-family:'Poppins',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
header{
  background:var(--heading);padding:16px 32px;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:10px;position:sticky;top:0;z-index:100;
}
.brand h1{font-size:20px;font-weight:700;color:#fff}
.brand p{font-size:10px;color:#a8bfd4;letter-spacing:2.5px;text-transform:uppercase;margin-top:2px}
.live-badge{
  display:flex;align-items:center;gap:7px;
  background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.15);
  border-radius:20px;padding:5px 14px;color:#fff;font-size:11px;font-weight:500;
}
.dot{width:7px;height:7px;background:#27ae60;border-radius:50%;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.4;transform:scale(1.4)}}
#danger-banner{
  display:none;background:var(--danger);color:#fff;
  text-align:center;padding:10px;font-size:13px;font-weight:600;
  animation:blink-bg 1s infinite;
}
#danger-banner.show{display:block}
@keyframes blink-bg{0%,100%{background:#c0392b}50%{background:#e74c3c}}
main{padding:24px;max-width:1300px;margin:0 auto}
.summary{
  display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
  gap:12px;margin-bottom:28px;
}
.sum-card{
  background:var(--card);border-radius:12px;padding:16px 18px;
  box-shadow:var(--shadow);border:1px solid var(--border);
}
.sum-card .val{font-size:30px;font-weight:700;color:var(--heading);line-height:1}
.sum-card .lbl{font-size:10px;color:var(--text);opacity:0.55;margin-top:5px;text-transform:uppercase;letter-spacing:1px}
.section-title{
  font-size:11px;font-weight:600;color:var(--heading);
  letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;opacity:0.6;
}
.robots-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px}
.robot-card{
  background:var(--card);border-radius:14px;box-shadow:var(--shadow);
  border:1.5px solid var(--border);overflow:hidden;
  transition:transform 0.2s,border-color 0.3s;
}
.robot-card:hover{transform:translateY(-2px)}
.robot-card.danger{border-color:var(--danger);box-shadow:0 0 0 3px rgba(192,57,43,0.12),var(--shadow)}
.robot-header{
  padding:14px 18px;display:flex;align-items:center;
  justify-content:space-between;border-bottom:1px solid var(--border);min-height:60px;
}
.robot-name{font-size:14px;font-weight:600;color:var(--heading)}
.robot-time{font-size:10px;color:var(--text);opacity:0.45;margin-top:2px}
.status-pill{
  padding:4px 11px;border-radius:20px;font-size:10px;font-weight:600;
  white-space:nowrap;min-width:90px;text-align:center;
}
.status-pill.NORMAL{background:#eafaf1;color:#27ae60}
.status-pill.DANGER{background:#fdf0ef;color:var(--danger);animation:blink-pill 0.8s infinite}
@keyframes blink-pill{0%,100%{opacity:1}50%{opacity:0.5}}
.ai-alert{
  height:0;overflow:hidden;background:#fdf0ef;
  font-size:11px;color:var(--danger);font-weight:500;
  display:flex;align-items:center;gap:8px;padding:0 18px;
  transition:height 0.3s ease,padding 0.3s ease;
}
.ai-alert.show{height:36px;padding:0 18px}
.cam-wrap{height:0;overflow:hidden;transition:height 0.3s ease;background:#0d0d1a}
.cam-wrap.show{height:200px}
.cam-wrap img{width:100%;height:200px;object-fit:cover}
.cam-wrap .no-cam{width:100%;height:200px;display:flex;align-items:center;justify-content:center;color:#555;font-size:12px}
.move-bar{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;padding:10px 18px;background:#f0f4f8;border-bottom:1px solid var(--border)}
.move-pill{background:var(--heading);color:#fff;font-size:10px;font-weight:600;padding:4px 10px;border-radius:12px;white-space:nowrap}
.move-dist{font-size:10px;color:var(--text);opacity:0.7;font-family:monospace}
.sensor-grid{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border)}
.sensor-item{background:var(--card);padding:14px 16px;min-height:80px}
.s-label{font-size:9px;text-transform:uppercase;letter-spacing:1.5px;color:var(--text);opacity:0.5;margin-bottom:5px}
.s-val{font-size:24px;font-weight:700;color:var(--heading);line-height:1}
.s-unit{font-size:11px;font-weight:400;opacity:0.45;margin-left:1px}
.bar-track{height:3px;background:var(--border);border-radius:2px;margin-top:8px;overflow:hidden}
.bar-fill{height:3px;border-radius:2px;background:var(--heading);transition:width 0.8s ease}
.bar-fill.high{background:var(--danger)}
.cam-btn{
  background:none;border:1px solid var(--border);border-radius:8px;
  padding:4px 10px;font-size:10px;font-family:'Poppins',sans-serif;
  color:var(--text);cursor:pointer;transition:background 0.2s;
}
.cam-btn:hover{background:var(--border)}
.empty{opacity:0.4;font-size:13px;padding:20px 0}
footer{text-align:center;padding:24px;font-size:10px;color:var(--text);opacity:0.35;letter-spacing:1.5px}
@media(max-width:600px){
  header{padding:12px 16px}
  main{padding:14px}
  .robots-grid{grid-template-columns:1fr}
  .sum-card .val{font-size:24px}
}
</style>
</head>
<body>
<header>
  <div class="brand">
    <h1>Autonomous Explorer</h1>
    <p>Navigate &nbsp;·&nbsp; Detect &nbsp;·&nbsp; Explore</p>
  </div>
  <div style="display:flex;align-items:center;gap:12px">
    <div id="hdr-time" style="font-size:11px;color:#a8bfd4"></div>
    <div class="live-badge"><div class="dot"></div>Live</div>
  </div>
</header>

<div id="danger-banner">⚠️ DANGER DETECTED — AI Anomaly Alert Active</div>

<main>
  <p class="section-title">Fleet Overview</p>
  <div class="summary">
    <div class="sum-card"><div class="val" id="total-bots">0</div><div class="lbl">Active Robots</div></div>
    <div class="sum-card"><div class="val" id="danger-count" style="color:var(--danger)">0</div><div class="lbl">Danger Alerts</div></div>
    <div class="sum-card"><div class="val" id="normal-count" style="color:var(--safe)">0</div><div class="lbl">All Clear</div></div>
    <div class="sum-card"><div class="val" id="avg-temp">--</div><div class="lbl">Avg Temp °C</div></div>
  </div>
  <p class="section-title">Robot Status</p>
  <div class="robots-grid" id="robots-grid">
    <p class="empty">Waiting for robots to connect...</p>
  </div>
</main>

<footer>AUTONOMOUS EXPLORER &nbsp;·&nbsp; BEAR SUMMIT 2026 &nbsp;·&nbsp; SILICON RIVER INITIATIVE</footer>

<script>
const camOpen = {};
function pct(v,max){return Math.min(100,Math.round((parseFloat(v)/max)*100))}

function renderRobots(data){
  const grid = document.getElementById('robots-grid');
  const ids = Object.keys(data);
  if(ids.length===0){
    grid.innerHTML='<p class="empty">Waiting for robots to connect...</p>';
    return;
  }
  let danger=0,normal=0,tempSum=0;
  ids.forEach(id=>{
    const r=data[id];
    const isDanger=r.STATUS==='DANGER';
    if(isDanger) danger++; else normal++;
    tempSum+=parseFloat(r.TEMP||0);
    const coPct=pct(r.CO,1000),airPct=pct(r.AIR,1000);
    const tmpPct=pct(r.TEMP,60),humPct=pct(r.HUM,100);
    const camShown=camOpen[id]?'show':'';
    const camContent=r.cam_ip
      ?`<img src="http://${r.cam_ip}/stream" alt="Live"/>`
      :`<div class="no-cam">📷 No camera connected</div>`;
    const html=`
    <div class="robot-card ${isDanger?'danger':''}" id="card-${id}">
      <div class="robot-header">
        <div>
          <div class="robot-name">${r.id}</div>
          <div class="robot-time">Last seen: ${r.last_seen}</div>
        </div>
        <div style="display:flex;align-items:center;gap:8px">
          <button class="cam-btn" onclick="toggleCam('${id}')">📷 Cam</button>
          <span class="status-pill ${r.STATUS}">${isDanger?'⚠️ DANGER':'✅ NORMAL'}</span>
        </div>
      </div>
      <div class="ai-alert ${isDanger?'show':''}">🧠 AI anomaly detected — unusual sensor pattern</div>
      <div class="cam-wrap ${camShown}" id="cam-${id}">${camContent}</div>
      ${r.MOVE?`
      <div class="move-bar">
        <span class="move-pill">🧭 ${r.MOVE}</span>
        <span class="move-dist">F:${r.DISTF??'--'}cm &nbsp; L:${r.DISTL??'--'}cm &nbsp; R:${r.DISTR??'--'}cm &nbsp; B:${r.DISTB??'--'}cm</span>
      </div>`:''}
      <div class="sensor-grid">
        ${r.CO!==undefined?`
        <div class="sensor-item">
          <div class="s-label">Carbon Monoxide</div>
          <div class="s-val">${r.CO}<span class="s-unit">ppm</span></div>
          <div class="bar-track"><div class="bar-fill ${coPct>70?'high':''}" style="width:${coPct}%"></div></div>
        </div>`:''}
        ${r.AIR!==undefined?`
        <div class="sensor-item">
          <div class="s-label">Air Quality</div>
          <div class="s-val">${r.AIR}<span class="s-unit">aqi</span></div>
          <div class="bar-track"><div class="bar-fill ${airPct>70?'high':''}" style="width:${airPct}%"></div></div>
        </div>`:''}
        ${r.TEMP!==undefined?`
        <div class="sensor-item">
          <div class="s-label">Temperature</div>
          <div class="s-val">${r.TEMP}<span class="s-unit">°C</span></div>
          <div class="bar-track"><div class="bar-fill ${tmpPct>70?'high':''}" style="width:${tmpPct}%"></div></div>
        </div>`:''}
        ${r.HUM!==undefined?`
        <div class="sensor-item">
          <div class="s-label">Humidity</div>
          <div class="s-val">${r.HUM}<span class="s-unit">%</span></div>
          <div class="bar-track"><div class="bar-fill" style="width:${humPct}%"></div></div>
        </div>`:''}
      </div>
    </div>`;
    const existing=document.getElementById('card-'+id);
    if(existing){ existing.outerHTML=html; }
    else{
      const placeholder=grid.querySelector('.empty');
      if(placeholder) placeholder.remove();
      const div=document.createElement('div');
      div.innerHTML=html;
      grid.appendChild(div.firstElementChild);
    }
  });
  document.getElementById('total-bots').innerText=ids.length;
  document.getElementById('danger-count').innerText=danger;
  document.getElementById('normal-count').innerText=normal;
  document.getElementById('avg-temp').innerText=ids.length?(tempSum/ids.length).toFixed(1):'--';
  const banner=document.getElementById('danger-banner');
  danger>0?banner.classList.add('show'):banner.classList.remove('show');
  document.getElementById('hdr-time').innerText=new Date().toLocaleTimeString();
}

function toggleCam(id){
  camOpen[id]=!camOpen[id];
  const el=document.getElementById('cam-'+id);
  if(el) el.classList.toggle('show',camOpen[id]);
}

setInterval(()=>{
  fetch('/data').then(r=>r.json()).then(renderRobots).catch(()=>{});
},1500);
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)