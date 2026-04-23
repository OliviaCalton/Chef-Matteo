from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic
import json, re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
client = Anthropic()

RECIPE_SCHEMA = """{"name":"string","description":"string","prepTime":"15 min","cookTime":"30 min","servings":4,"difficulty":"Easy|Medium|Hard","ingredients":[{"item":"string","amount":"string","onHand":true}],"steps":["string"],"groceryList":[{"item":"string","amount":"string","estimatedCost":"$2"}],"tips":"string","nutrition":{"calories":"string","protein":"string","carbs":"string","fat":"string"}}"""

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chef Matteo · Meal Planner</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --black:#0A0A0A;
  --gold:#C9A84C;
  --gold-dim:rgba(201,168,76,0.12);
  --white:#FFFFFF;
  --bg:#F8F7F4;
  --card:#FFFFFF;
  --border:#E8E6E0;
  --text:#1A1A1A;
  --text-muted:#888;
  --error:#C0392B;
  --radius:12px;
  --shadow:0 2px 16px rgba(0,0,0,0.07);
}
body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;display:flex;flex-direction:column}

/* HEADER */
header{background:var(--black);padding:0 24px;height:58px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;border-bottom:1px solid rgba(255,255,255,0.06)}
.logo-btn{display:flex;align-items:center;gap:10px;background:none;border:none;cursor:pointer;padding:0}
.logo-btn:hover{opacity:0.8}
.logo-name{font-family:'Playfair Display',serif;font-weight:700;color:var(--white);font-size:15px}
.logo-tag{font-size:9px;color:var(--gold);letter-spacing:.2em;text-transform:uppercase;margin-left:6px;opacity:.85}
.hdr-right{display:flex;align-items:center;gap:12px}
.tagline{font-size:11px;color:#666;font-style:italic;letter-spacing:.02em}
.back-btn{display:none;align-items:center;gap:6px;background:none;border:1px solid rgba(255,255,255,0.15);border-radius:8px;cursor:pointer;font-family:'DM Sans',sans-serif;font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:#aaa;padding:7px 14px;transition:all .15s}
.back-btn:hover{color:var(--white);border-color:rgba(255,255,255,.4)}
.back-btn svg{flex-shrink:0}

/* VIEWS */
.view{display:none;flex:1;flex-direction:column}
.view.active{display:flex}

/* LANDING */
.hero{padding:64px 24px 40px;text-align:center;max-width:600px;margin:0 auto;width:100%}
.hero-eyebrow{font-size:10px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin-bottom:16px}
.hero-title{font-family:'Playfair Display',serif;font-size:clamp(32px,6vw,52px);font-weight:700;line-height:1.15;color:var(--text);margin-bottom:16px}
.hero-desc{font-size:15px;color:var(--text-muted);line-height:1.6;max-width:420px;margin:0 auto 40px}
.cards{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:640px;margin:0 auto;padding:0 24px 24px;width:100%}
@media(max-width:520px){.cards{grid-template-columns:1fr}}
.card{background:var(--card);border:1.5px solid var(--border);border-radius:var(--radius);padding:28px 24px;cursor:pointer;text-align:left;transition:all .2s;box-shadow:var(--shadow)}
.card:hover{border-color:var(--gold);box-shadow:0 4px 24px rgba(201,168,76,0.15);transform:translateY(-2px)}
.card-icon{width:36px;height:36px;background:var(--gold-dim);border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.card-label{font-size:9px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--gold);margin-bottom:6px}
.card-title{font-family:'Playfair Display',serif;font-size:17px;font-weight:700;margin-bottom:8px;color:var(--text)}
.card-desc{font-size:13px;color:var(--text-muted);line-height:1.55}
.card-cta{font-size:12px;font-weight:600;color:var(--gold);margin-top:14px;display:flex;align-items:center;gap:4px}

/* HOW IT WORKS */
.how{background:var(--black);padding:32px 24px;margin-top:8px}
.how-inner{max-width:640px;margin:0 auto}
.how-label{font-size:9px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin-bottom:20px;text-align:center}
.how-steps{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
@media(max-width:520px){.how-steps{grid-template-columns:1fr 1fr}}
.how-step{text-align:center}
.how-num{width:28px;height:28px;border-radius:50%;background:var(--gold-dim);border:1px solid rgba(201,168,76,0.3);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:var(--gold);margin:0 auto 8px}
.how-step-title{font-size:12px;font-weight:600;color:var(--white);margin-bottom:3px}
.how-step-desc{font-size:11px;color:#666;line-height:1.4}

/* INPUT VIEWS */
.input-wrap{flex:1;padding:40px 24px;max-width:600px;margin:0 auto;width:100%}
.view-eyebrow{font-size:9px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin-bottom:10px}
.view-title{font-family:'Playfair Display',serif;font-size:26px;font-weight:700;margin-bottom:8px}
.view-desc{font-size:14px;color:var(--text-muted);line-height:1.55;margin-bottom:32px;max-width:460px}
.input-label{font-size:10px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px}
textarea{width:100%;min-height:120px;padding:14px 16px;border:1.5px solid var(--border);border-radius:var(--radius);font-family:'DM Sans',sans-serif;font-size:14px;color:var(--text);background:var(--white);resize:vertical;transition:border .15s;line-height:1.55}
textarea:focus{outline:none;border-color:var(--gold)}
textarea::placeholder{color:#bbb}
.gen-btn{width:100%;margin-top:12px;padding:15px;background:var(--gold);border:none;border-radius:var(--radius);font-family:'DM Sans',sans-serif;font-size:14px;font-weight:700;letter-spacing:.04em;color:var(--black);cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;gap:8px}
.gen-btn:hover{background:#d4b05a;transform:translateY(-1px)}
.gen-btn:disabled{opacity:0.6;cursor:not-allowed;transform:none}
.cmd-hint{font-size:11px;color:var(--text-muted);margin-top:8px;text-align:center}
.error-msg{display:none;align-items:center;gap:8px;background:#fdf2f2;border:1px solid #f5c6c6;border-radius:8px;padding:10px 14px;font-size:13px;color:var(--error);margin-top:10px}
.switch-link{text-align:center;margin-top:24px}
.switch-link button{background:none;border:none;cursor:pointer;font-family:'DM Sans',sans-serif;font-size:13px;color:var(--text-muted);text-decoration:underline;text-underline-offset:3px}
.switch-link button:hover{color:var(--gold)}

/* ACCORDION */
.accord{border:1.5px solid var(--border);border-radius:var(--radius);margin-top:24px;overflow:hidden;background:var(--white)}
.accord-trigger{width:100%;background:none;border:none;cursor:pointer;padding:14px 18px;display:flex;align-items:center;justify-content:space-between;font-family:'DM Sans',sans-serif}
.accord-trigger:hover{background:#fafaf9}
.accord-left{display:flex;align-items:center;gap:10px}
.accord-dot{width:7px;height:7px;border-radius:50%;background:var(--gold)}
.accord-label{font-size:13px;font-weight:600;color:var(--text)}
.accord-chevron{transition:transform .2s;color:var(--text-muted)}
.accord-chevron.open{transform:rotate(180deg)}
.accord-body{display:none;padding:0 18px 16px;font-size:13px;color:var(--text-muted);line-height:1.6;border-top:1px solid var(--border)}
.accord-body ul{padding-left:18px;margin-top:8px}
.accord-body li{margin-bottom:4px}

/* SPINNER */
.spinner{width:14px;height:14px;border:2px solid rgba(0,0,0,0.2);border-top-color:var(--black);border-radius:50%;animation:spin .7s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* RECIPE VIEW */
.recipe-wrap{flex:1;padding:32px 24px;max-width:720px;margin:0 auto;width:100%}
.recipe-by{font-size:9px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);margin-bottom:8px}
.recipe-title{font-family:'Playfair Display',serif;font-size:clamp(22px,4vw,32px);font-weight:700;line-height:1.2;margin-bottom:8px}
.recipe-desc{font-size:14px;color:var(--text-muted);margin-bottom:16px;line-height:1.55}
.recipe-meta{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:20px}
.meta-item{display:flex;align-items:center;gap:5px;font-size:12px;color:var(--text-muted);font-weight:500}
.diff-badge{padding:3px 10px;border-radius:20px;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.diff-easy{background:#e8f5e9;color:#2e7d32}
.diff-medium{background:#fff3e0;color:#e65100}
.diff-hard{background:#fce4ec;color:#c62828}
.save-btn{display:flex;align-items:center;gap:7px;background:none;border:1.5px solid var(--border);border-radius:8px;padding:8px 16px;font-family:'DM Sans',sans-serif;font-size:12px;font-weight:600;color:var(--text-muted);cursor:pointer;transition:all .15s;margin-bottom:28px}
.save-btn:hover{border-color:var(--gold);color:var(--gold)}
.save-btn.saved{border-color:var(--gold);color:var(--gold);background:var(--gold-dim)}
.recipe-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px;margin-bottom:32px}
@media(max-width:560px){.recipe-grid{grid-template-columns:1fr}}
.section-label{font-size:9px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:var(--text-muted);margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--border)}
.ing-list{list-style:none;display:flex;flex-direction:column;gap:8px}
.ing-item{display:flex;align-items:flex-start;gap:10px;font-size:13px}
.ing-dot{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.ing-dot.on-hand{background:#e8f5e9;color:#2e7d32}
.ing-dot.to-buy{background:#fff3e0;color:#e65100}
.steps-list{list-style:none;display:flex;flex-direction:column;gap:14px}
.step-item{display:flex;gap:12px;font-size:13px;line-height:1.55}
.step-n{width:22px;height:22px;border-radius:50%;background:var(--gold-dim);border:1px solid rgba(201,168,76,0.3);display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:700;color:var(--gold);flex-shrink:0;margin-top:1px}
.divider{border-top:1px solid var(--border);padding-top:24px;margin-bottom:24px}
.grocery-grid{display:flex;flex-direction:column;gap:8px;margin-top:4px}
.grocery-row{display:flex;justify-content:space-between;align-items:center;font-size:13px;padding:8px 0;border-bottom:1px solid var(--border)}
.grocery-row:last-child{border-bottom:none}
.grocery-cost{font-weight:600;color:var(--gold);font-size:12px}
.info-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:4px}
@media(max-width:560px){.info-grid{grid-template-columns:1fr}}
.info-card{background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius);padding:16px}
.info-card-label{font-size:9px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--text-muted);margin-bottom:10px}
.info-card-text{font-size:13px;color:var(--text);line-height:1.55;font-style:italic}
.nutrition-row{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;border-bottom:1px solid var(--border)}
.nutrition-row:last-child{border-bottom:none}
.nutrition-label{color:var(--text-muted)}

/* FOOTER */
footer{background:var(--black);padding:16px 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-top:auto}
.footer-left{font-size:11px;color:#555}
.footer-by{color:var(--gold)}
.footer-right{font-size:11px;color:#444}
</style>
</head>
<body>

<!-- HEADER -->
<header>
  <button class="logo-btn" id="logoBtn">
    <svg width="26" height="29" viewBox="0 0 48 54" fill="none">
      <path d="M24 3 L44 10 L44 30 Q44 44 24 51 Q4 44 4 30 L4 10 Z" fill="rgba(201,168,76,0.1)" stroke="#C9A84C" stroke-width="1.6"/>
      <ellipse cx="24" cy="20" rx="7.5" ry="4" fill="rgba(201,168,76,0.2)" stroke="#C9A84C" stroke-width="1.3"/>
      <ellipse cx="24" cy="16.5" rx="5" ry="6" fill="rgba(201,168,76,0.15)" stroke="#C9A84C" stroke-width="1.3"/>
      <line x1="24" y1="24" x2="24" y2="38" stroke="#C9A84C" stroke-width="1.4" stroke-linecap="round"/>
      <line x1="18" y1="29" x2="30" y2="29" stroke="#C9A84C" stroke-width="1.3" stroke-linecap="round"/>
    </svg>
    <span class="logo-name">Chef Matteo</span>
    <span class="logo-tag">Meal Planner</span>
  </button>
  <div class="hdr-right">
    <span class="tagline">Plan smarter. Eat better.</span>
    <button class="back-btn" id="backBtn">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M3 12h18M3 12l6-6M3 12l6 6"/></svg>
      Back
    </button>
  </div>
</header>

<!-- VIEW: LANDING -->
<div class="view active" id="viewLanding">
  <div class="hero">
    <div class="hero-eyebrow">AI Meal Planner</div>
    <h1 class="hero-title">Your personal<br>meal planner.</h1>
    <p class="hero-desc">Two ways to plan. One result: the right meal, built around your goals and what you already have.</p>
  </div>
  <div class="cards">
    <button class="card" id="cardGoals">
      <div class="card-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
      </div>
      <div class="card-label">Groceries to Fridge</div>
      <div class="card-title">Plan toward your goals.</div>
      <div class="card-desc">Share your nutrition target or fitness goal. Matteo designs the meal and hands you the exact shopping list.</div>
      <div class="card-cta">Start here <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg></div>
    </button>
    <button class="card" id="cardFridge">
      <div class="card-icon">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#C9A84C" stroke-width="2" stroke-linecap="round"><rect x="4" y="2" width="16" height="20" rx="2"/><line x1="4" y1="10" x2="20" y2="10"/><line x1="9" y1="6" x2="9" y2="8"/><line x1="9" y1="14" x2="9" y2="18"/></svg>
      </div>
      <div class="card-label">Fridge to Meal</div>
      <div class="card-title">Cook from what you have.</div>
      <div class="card-desc">Tell Matteo what's in your fridge. He builds a full recipe around it and flags the few extras worth grabbing.</div>
      <div class="card-cta">Start here <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg></div>
    </button>
  </div>
  <div class="how">
    <div class="how-inner">
      <div class="how-label">How it works</div>
      <div class="how-steps">
        <div class="how-step"><div class="how-num">1</div><div class="how-step-title">You describe</div><div class="how-step-desc">Your goal or ingredients</div></div>
        <div class="how-step"><div class="how-num">2</div><div class="how-step-title">Matteo plans</div><div class="how-step-desc">Maps nutrition and flavour</div></div>
        <div class="how-step"><div class="how-num">3</div><div class="how-step-title">Recipe built</div><div class="how-step-desc">Full steps and grocery list</div></div>
        <div class="how-step"><div class="how-num">4</div><div class="how-step-title">You cook</div><div class="how-step-desc">Exactly what you need</div></div>
      </div>
    </div>
  </div>
</div>

<!-- VIEW: GOALS INPUT -->
<div class="view" id="viewGoals">
  <div class="input-wrap">
    <div class="view-eyebrow">Groceries to Fridge</div>
    <h2 class="view-title">Plan toward your goals.</h2>
    <p class="view-desc">Describe your nutrition target, fitness goal, or dietary needs. Matteo designs the right meal and hands you the exact shopping list.</p>
    <div class="input-label">Your goal or macro targets</div>
    <textarea id="goalsInput" placeholder="e.g. High-protein post-workout meal, 600 cal, 45g protein, no dairy. Or: light Mediterranean dinner under 400 cal..."></textarea>
    <button class="gen-btn" id="goalsBtn">Generate Recipe</button>
    <div class="error-msg" id="goalsError"></div>
    <div class="cmd-hint">⌘ + Enter to generate</div>
    <div class="accord" id="accordGoals">
      <button class="accord-trigger" data-body="accordGoalsBody">
        <div class="accord-left"><div class="accord-dot"></div><div class="accord-label">How Matteo plans</div></div>
        <svg class="accord-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      <div class="accord-body" id="accordGoalsBody">
        Matteo reads your calorie and macro targets, then designs a single meal that hits them precisely. You get a full recipe with step-by-step instructions, a complete grocery list with estimated costs, and a nutrition breakdown.
      </div>
    </div>
    <div class="switch-link">
      <button id="switchToFridge">Switch to Fridge to Meal instead</button>
    </div>
  </div>
</div>

<!-- VIEW: FRIDGE INPUT -->
<div class="view" id="viewFridge">
  <div class="input-wrap">
    <div class="view-eyebrow">Fridge to Meal</div>
    <h2 class="view-title">Cook from what you have.</h2>
    <p class="view-desc">List the ingredients you have on hand. Matteo builds a full recipe around them, minimises waste, and notes any extras worth grabbing.</p>
    <div class="input-label">What's in your fridge</div>
    <textarea id="fridgeInput" placeholder="e.g. Chicken thighs, garlic, lemon, cherry tomatoes, fresh basil, olive oil, parmesan..."></textarea>
    <button class="gen-btn" id="fridgeBtn">Generate Recipe</button>
    <div class="error-msg" id="fridgeError"></div>
    <div class="cmd-hint">⌘ + Enter to generate</div>
    <div class="accord" id="accordFridge">
      <button class="accord-trigger" data-body="accordFridgeBody">
        <div class="accord-left"><div class="accord-dot"></div><div class="accord-label">How Matteo plans</div></div>
        <svg class="accord-chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      <div class="accord-body" id="accordFridgeBody">
        Matteo uses what you have as the foundation, flags each ingredient as on-hand, and keeps the grocery list to absolute essentials. No waste, no over-shopping.
      </div>
    </div>
    <div class="switch-link">
      <button id="switchToGoals">Switch to Groceries to Fridge instead</button>
    </div>
  </div>
</div>

<!-- VIEW: RECIPE RESULT -->
<div class="view" id="viewRecipe">
  <div class="recipe-wrap" id="recipeContent"></div>
</div>

<!-- FOOTER -->
<footer>
  <span class="footer-left">Chef Matteo &middot; built by <span class="footer-by">Olivia Calton</span></span>
  <span class="footer-right">Powered by Claude AI &middot; Every plan made fresh</span>
</footer>

<script>
// ── NAVIGATION ────────────────────────────────────────────────
function showView(id) {
  document.querySelectorAll('.view').forEach(v => { v.style.display = 'none'; v.classList.remove('active'); });
  const el = document.getElementById(id);
  el.style.display = 'flex';
  el.classList.add('active');
  window.scrollTo(0, 0);
  document.getElementById('backBtn').style.display = (id === 'viewLanding') ? 'none' : 'flex';
}

function goHome() { showView('viewLanding'); }

// ── WIRE UP ALL BUTTONS ───────────────────────────────────────
document.getElementById('logoBtn').onclick = goHome;
document.getElementById('backBtn').onclick = goHome;
document.getElementById('cardGoals').onclick = function() { showView('viewGoals'); };
document.getElementById('cardFridge').onclick = function() { showView('viewFridge'); };
document.getElementById('switchToFridge').onclick = function() { showView('viewFridge'); };
document.getElementById('switchToGoals').onclick = function() { showView('viewGoals'); };
document.getElementById('goalsBtn').onclick = function() { generateRecipe('goals'); };
document.getElementById('fridgeBtn').onclick = function() { generateRecipe('fridge'); };

// Keyboard shortcut
document.getElementById('goalsInput').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) generateRecipe('goals');
});
document.getElementById('fridgeInput').addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) generateRecipe('fridge');
});

// ── ACCORDIONS ────────────────────────────────────────────────
document.querySelectorAll('.accord-trigger').forEach(function(btn) {
  btn.onclick = function() {
    var bodyId = btn.getAttribute('data-body');
    var body = document.getElementById(bodyId);
    var chevron = btn.querySelector('.accord-chevron');
    var isOpen = body.style.display === 'block';
    body.style.display = isOpen ? 'none' : 'block';
    chevron.classList.toggle('open', !isOpen);
  };
});

// ── GENERATE RECIPE ───────────────────────────────────────────
async function generateRecipe(mode) {
  var isGoals = mode === 'goals';
  var inputEl = document.getElementById(isGoals ? 'goalsInput' : 'fridgeInput');
  var btn = document.getElementById(isGoals ? 'goalsBtn' : 'fridgeBtn');
  var errEl = document.getElementById(isGoals ? 'goalsError' : 'fridgeError');
  var input = inputEl.value.trim();

  if (!input) {
    errEl.textContent = 'Please enter ' + (isGoals ? 'your goal or macro targets.' : 'your ingredients.');
    errEl.style.display = 'flex';
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<div class="spinner"></div> Matteo is planning\\u2026';
  errEl.style.display = 'none';

  try {
    var body = isGoals
      ? { mode: 'goals', goal: input, servings: 4 }
      : { mode: 'fridge', ingredients: input, servings: 4 };

    var res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    var data = await res.json();
    if (!res.ok || data.error) throw new Error(data.error || 'Something went wrong.');

    renderRecipe(data.recipe);
    showView('viewRecipe');
  } catch(e) {
    errEl.textContent = e.message || 'Something went wrong. Please try again.';
    errEl.style.display = 'flex';
  } finally {
    btn.disabled = false;
    btn.innerHTML = 'Generate Recipe';
  }
}

// ── RENDER RECIPE ─────────────────────────────────────────────
function renderRecipe(r) {
  var diffClass = { Easy: 'diff-easy', Medium: 'diff-medium', Hard: 'diff-hard' }[r.difficulty] || 'diff-medium';
  var onHand = (r.ingredients || []).filter(function(i) { return i.onHand; }).length;
  var total = (r.ingredients || []).length;

  var ingHTML = (r.ingredients || []).map(function(ing) {
    return '<li class="ing-item"><div class="ing-dot ' + (ing.onHand ? 'on-hand' : 'to-buy') + '">'
      + (ing.onHand
        ? '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><path d="M20 6L9 17l-5-5"/></svg>'
        : '<svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 001.99 1.61h9.72a2 2 0 001.99-1.61L23 6H6"/></svg>')
      + '</div><span><strong>' + ing.amount + '</strong> ' + ing.item + '</span></li>';
  }).join('');

  var stepsHTML = (r.steps || []).map(function(s, i) {
    return '<li class="step-item"><div class="step-n">' + (i + 1) + '</div><p>' + s + '</p></li>';
  }).join('');

  var grocHTML = '';
  if ((r.groceryList || []).length > 0) {
    grocHTML = '<div class="divider"><div class="section-label">Grocery List</div><div class="grocery-grid">'
      + (r.groceryList || []).map(function(g) {
          return '<div class="grocery-row"><span><strong>' + g.item + '</strong> <span style="color:var(--text-muted);font-size:11px">(' + g.amount + ')</span></span><span class="grocery-cost">' + g.estimatedCost + '</span></div>';
        }).join('')
      + '</div></div>';
  }

  var nutHTML = '';
  if (r.nutrition) {
    nutHTML = '<div class="info-card"><div class="info-card-label">Nutrition per serving</div>'
      + '<div class="nutrition-row"><span class="nutrition-label">Calories</span><strong>' + r.nutrition.calories + '</strong></div>'
      + '<div class="nutrition-row"><span class="nutrition-label">Protein</span><strong>' + r.nutrition.protein + '</strong></div>'
      + '<div class="nutrition-row"><span class="nutrition-label">Carbs</span><strong>' + r.nutrition.carbs + '</strong></div>'
      + '<div class="nutrition-row"><span class="nutrition-label">Fat</span><strong>' + r.nutrition.fat + '</strong></div>'
      + '</div>';
  }

  var tipHTML = r.tips
    ? '<div class="info-card"><div class="info-card-label">Chef\\'s Tip</div><div class="info-card-text">&ldquo;' + r.tips + '&rdquo;</div></div>'
    : '';

  document.getElementById('recipeContent').innerHTML =
    '<div class="recipe-by">Matteo recommends</div>'
    + '<div class="recipe-title">' + r.name + '</div>'
    + '<div class="recipe-desc">' + r.description + '</div>'
    + '<div class="recipe-meta">'
    + '<span class="meta-item"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg> Prep ' + r.prepTime + '</span>'
    + '<span class="meta-item"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2a7 7 0 017 7c0 5-7 13-7 13S5 14 5 9a7 7 0 017-7z"/></svg> Cook ' + r.cookTime + '</span>'
    + '<span class="meta-item"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/></svg> ' + r.servings + ' servings</span>'
    + '<span class="diff-badge ' + diffClass + '">' + r.difficulty + '</span>'
    + '</div>'
    + '<button class="save-btn" id="saveBtn" onclick="toggleSave(this)">'
    + '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg>'
    + ' Save recipe</button>'
    + '<div class="recipe-grid">'
    + '<div><div class="section-label">Ingredients' + (onHand > 0 ? ' <span style="font-weight:400;font-size:9px;color:var(--text-muted);text-transform:none;letter-spacing:0">(' + onHand + '/' + total + ' on hand)</span>' : '') + '</div><ul class="ing-list">' + ingHTML + '</ul></div>'
    + '<div><div class="section-label">Method</div><ol class="steps-list">' + stepsHTML + '</ol></div>'
    + '</div>'
    + grocHTML
    + '<div class="divider"><div class="section-label">Details</div><div class="info-grid">' + tipHTML + nutHTML + '</div></div>';
}

function toggleSave(btn) {
  btn.classList.toggle('saved');
  var saved = btn.classList.contains('saved');
  btn.innerHTML = saved
    ? '<svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg> Saved'
    : '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z"/></svg> Save recipe';
}
</script>
</body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(content=HTML)

@app.post("/api/generate")
async def generate(request: Request):
    try:
        body = await request.json()
        mode = body.get("mode", "")

        if mode == "fridge":
            ingredients = body.get("ingredients", "").strip()
            if not ingredients:
                return JSONResponse({"error": "No ingredients provided"}, status_code=400)
            system = f"Precise, creative meal planner. Build the best recipe from listed ingredients. Steps: active voice, no filler. Rules: use most ingredients (onHand:true), groceryList essentials only, accurate nutrition. Return ONLY valid JSON:\n{RECIPE_SCHEMA}"
            user_msg = f"Ingredients I have: {ingredients}"

        elif mode == "goals":
            goal = body.get("goal", "").strip()
            if not goal:
                return JSONResponse({"error": "No goal provided"}, status_code=400)
            system = f"Precise meal planner and nutritionist. Design a meal hitting the stated targets exactly. Steps: active voice, no filler. Rules: match macros/calories precisely, all onHand:false, full groceryList with realistic costs, accurate nutrition. Return ONLY valid JSON:\n{RECIPE_SCHEMA}"
            user_msg = f"Goal: {goal}"

        else:
            return JSONResponse({"error": "Invalid mode."}, status_code=400)

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )

        text = message.content[0].text.strip()
        try:
            recipe = json.loads(text)
        except Exception:
            m = re.search(r'\{[\s\S]*\}', text)
            if m:
                recipe = json.loads(m.group(0))
            else:
                return JSONResponse({"error": "Could not parse recipe"}, status_code=500)

        return JSONResponse({"recipe": recipe})

    except Exception as e:
        print(f"[error] {e}")
        return JSONResponse({"error": "Failed to generate recipe. Please try again."}, status_code=500)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
