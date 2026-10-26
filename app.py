from flask import Flask, jsonify, request, render_template_string
import json, os

app = Flask(__name__)
FILE = "/data/scores.json"

def load():
    if os.path.exists(FILE):
        with open(FILE) as f:
            return json.load(f)
    return []

def save(scores):
    os.makedirs("/data", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(scores, f)

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Snake Python Docker</title>
<style>
  body { margin:0; min-height:100vh; display:flex; align-items:center;
         justify-content:center; gap:30px; flex-wrap:wrap; padding:20px;
         box-sizing:border-box; font-family:Arial,sans-serif; color:#fff;
         background:linear-gradient(135deg,#0f2027,#203a43,#2c5364); }
  .game { text-align:center; }
  h1 { margin:0 0 8px; }
  .info { display:flex; gap:25px; justify-content:center; margin-bottom:8px; font-size:18px; }
  canvas { background:#0b1a22; border:3px solid #4caf50; border-radius:10px;
           max-width:95vw; touch-action:none; }
  input { padding:8px; border-radius:8px; border:0; margin-bottom:8px; width:160px; }
  .board { background:rgba(255,255,255,0.08); padding:20px; border-radius:14px; width:260px; }
  .board h2 { margin:0 0 10px; font-size:20px; text-align:center; }
  .board ol { margin:0; padding-left:22px; }
  .board li { padding:6px 0; border-bottom:1px solid rgba(255,255,255,0.12); }
  .board li span { float:right; color:#8bc34a; font-weight:bold; }
  small { color:#9fb8c8; }
</style>
</head>
<body>
<div class="game">
  <h1>Snake Python</h1>
  <div class="info">
    <span>Score: <b id="score">0</b></span>
    <span>Container: <b>{{ host }}</b></span>
  </div>
  <input id="name" maxlength="15" placeholder="Ton nom">
  <br>
  <canvas id="c" width="400" height="400"></canvas>
  <br><small>Fleches / WASD, Espace pour demarrer et rejouer</small>
</div>
<div class="board">
  <h2>Classement</h2>
  <ol id="board"></ol>
</div>
<script>
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
const SIZE = 20, N = cv.width / SIZE;
let snake, dir, nextDir, food, score, state, timer, speed;
const nameInput = document.getElementById('name');
nameInput.value = localStorage.getItem('snakeName') || '';

async function loadBoard() {
  const r = await fetch('/api/scores');
  const data = await r.json();
  const ol = document.getElementById('board');
  ol.innerHTML = '';
  data.forEach(s => {
    const li = document.createElement('li');
    li.textContent = s.name;
    const sp = document.createElement('span');
    sp.textContent = s.score;
    li.appendChild(sp);
    ol.appendChild(li);
  });
}

async function sendScore() {
  const name = nameInput.value.trim() || 'Anonyme';
  localStorage.setItem('snakeName', name);
  await fetch('/api/scores', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({name: name, score: score})
  });
  loadBoard();
}

function reset() {
  snake = [{x:10,y:10},{x:9,y:10},{x:8,y:10}];
  dir = {x:1,y:0};
  nextDir = dir;
  score = 0;
  speed = 130;
  document.getElementById('score').textContent = 0;
  placeFood();
  state = 'ready';
  clearInterval(timer);
  draw();
}

function placeFood() {
  do {
    food = {x: Math.floor(Math.random()*N), y: Math.floor(Math.random()*N)};
  } while (snake.some(s => s.x === food.x && s.y === food.y));
}

function start() {
  state = 'play';
  clearInterval(timer);
  timer = setInterval(step, speed);
}

function setDir(x, y) {
  if (x === -dir.x && y === -dir.y) return;
  nextDir = {x:x, y:y};
  if (state === 'ready') start();
}

document.addEventListener('keydown', e => {
  if (document.activeElement === nameInput) return;
  const k = e.key.toLowerCase();
  if (e.code === 'Space') {
    e.preventDefault();
    if (state === 'dead') reset();
    else if (state === 'ready') start();
    return;
  }
  if (k === 'arrowup' || k === 'w') { e.preventDefault(); setDir(0,-1); }
  if (k === 'arrowdown' || k === 's') { e.preventDefault(); setDir(0,1); }
  if (k === 'arrowleft' || k === 'a') { e.preventDefault(); setDir(-1,0); }
  if (k === 'arrowright' || k === 'd') { e.preventDefault(); setDir(1,0); }
});

let tx = 0, ty = 0;
cv.addEventListener('touchstart', e => {
  e.preventDefault();
  tx = e.touches[0].clientX; ty = e.touches[0].clientY;
  if (state === 'dead') reset();
});
cv.addEventListener('touchend', e => {
  const dx = e.changedTouches[0].clientX - tx;
  const dy = e.changedTouches[0].clientY - ty;
  if (Math.abs(dx) > Math.abs(dy)) setDir(dx > 0 ? 1 : -1, 0);
  else setDir(0, dy > 0 ? 1 : -1);
});

function step() {
  dir = nextDir;
  const head = {x: snake[0].x + dir.x, y: snake[0].y + dir.y};
  if (head.x < 0 || head.y < 0 || head.x >= N || head.y >= N ||
      snake.some(s => s.x === head.x && s.y === head.y)) {
    die();
    return;
  }
  snake.unshift(head);
  if (head.x === food.x && head.y === food.y) {
    score++;
    document.getElementById('score').textContent = score;
    placeFood();
    if (speed > 60) {
      speed -= 4;
      clearInterval(timer);
      timer = setInterval(step, speed);
    }
  } else {
    snake.pop();
  }
  draw();
}

function die() {
  state = 'dead';
  clearInterval(timer);
  if (score > 0) sendScore();
  draw();
}

function draw() {
  ctx.fillStyle = '#0b1a22';
  ctx.fillRect(0, 0, cv.width, cv.height);
  ctx.fillStyle = '#e53935';
  ctx.beginPath();
  ctx.arc(food.x*SIZE + SIZE/2, food.y*SIZE + SIZE/2, SIZE/2 - 2, 0, Math.PI*2);
  ctx.fill();
  snake.forEach((s, i) => {
    ctx.fillStyle = i === 0 ? '#8bc34a' : '#4caf50';
    ctx.fillRect(s.x*SIZE + 1, s.y*SIZE + 1, SIZE - 2, SIZE - 2);
  });
  ctx.fillStyle = '#fff';
  ctx.textAlign = 'center';
  if (state === 'ready') {
    ctx.font = '18px Arial';
    ctx.fillText('Appuie sur une fleche pour commencer', cv.width/2, cv.height/2 + 60);
  }
  if (state === 'dead') {
    ctx.font = 'bold 32px Arial';
    ctx.fillText('Game Over', cv.width/2, cv.height/2 - 10);
    ctx.font = '18px Arial';
    ctx.fillText('Score: ' + score, cv.width/2, cv.height/2 + 20);
    ctx.fillText('Espace pour rejouer', cv.width/2, cv.height/2 + 50);
  }
}

reset();
loadBoard();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    import socket
    return render_template_string(HTML, host=socket.gethostname())

@app.route("/api/scores", methods=["GET"])
def get_scores():
    return jsonify(load())

@app.route("/api/scores", methods=["POST"])
def add_score():
    data = request.get_json(force=True)
    name = str(data.get("name", "Anonyme"))[:15]
    try:
        score = int(data.get("score", 0))
    except (TypeError, ValueError):
        return jsonify(error="score invalide"), 400
    scores = load()
    scores.append({"name": name, "score": score})
    scores = sorted(scores, key=lambda s: s["score"], reverse=True)[:10]
    save(scores)
    return jsonify(ok=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
