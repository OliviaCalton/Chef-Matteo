# Chef Matteo — AI Meal Planner

An AI-powered meal planning web app. Two input modes: plan from a fitness goal, or cook from what you already have.

Built by Olivia Calton.

---

## Stack

- **Backend:** FastAPI (Python 3.12)
- **AI:** Anthropic Claude (claude-sonnet-4-5)
- **Frontend:** Single-file vanilla HTML/CSS/JS — no build step

---

## Local Development

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/chef-matteo.git
cd chef-matteo
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your Anthropic API key
```bash
export ANTHROPIC_API_KEY=your_key_here
```

### 4. Run the server
```bash
uvicorn server:app --host 0.0.0.0 --port 5000 --reload
```

### 5. Open the app
Visit http://localhost:5000

---

## Deploy to Render (recommended)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) and click **New → Web Service**
3. Connect your GitHub repo
4. Set the following:
   - **Environment:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `ANTHROPIC_API_KEY` = your key from [console.anthropic.com](https://console.anthropic.com)
6. Click **Create Web Service** — Render gives you a public URL in under 2 minutes

> **Free tier note:** Render's free tier spins down after 15 minutes of inactivity. The first request after a cold start takes ~30 seconds. Upgrade to the $7/mo Starter plan for always-on.

---

## API

| Method | Route | Description |
|---|---|---|
| POST | `/api/generate` | Generate a recipe |
| GET | `/api/health` | Health check |

### POST /api/generate

**Goals mode:**
```json
{ "mode": "goals", "goal": "2000 cal, high protein, no dairy" }
```

**Fridge mode:**
```json
{ "mode": "fridge", "ingredients": "chicken, spinach, garlic, lemon" }
```

**Response:**
```json
{
  "recipe": {
    "name": "...",
    "description": "...",
    "prepTime": "15 min",
    "cookTime": "30 min",
    "servings": 4,
    "difficulty": "Easy",
    "ingredients": [...],
    "steps": [...],
    "groceryList": [...],
    "tips": "...",
    "nutrition": { "calories": "...", "protein": "...", "carbs": "...", "fat": "..." }
  }
}
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | Your Anthropic API key from console.anthropic.com |
| `PORT` | Render only | Injected automatically by Render |
