from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from anthropic import Anthropic
import json, re

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

client = Anthropic()

# ── RECIPE SCHEMA ────────────────────────────────────────────────
RECIPE_SCHEMA = """{
  "name": "Recipe Name",
  "description": "One-sentence description",
  "prepTime": "15 min",
  "cookTime": "30 min",
  "servings": 4,
  "difficulty": "Easy | Medium | Hard",
  "ingredients": [{"item": "name", "amount": "1 cup", "onHand": true}],
  "steps": ["Step 1"],
  "groceryList": [{"item": "name", "amount": "2 tbsp", "estimatedCost": "$2"}],
  "tips": "A helpful tip",
  "nutrition": {"calories": "~450", "protein": "~25g", "carbs": "~35g", "fat": "~20g"}
}"""

# ── GENERATE ROUTE ───────────────────────────────────────────────
@app.post("/api/generate")
async def generate(request: Request):
    try:
        body = await request.json()
        mode = body.get("mode")

        if mode == "fridge":
            ingredients = body.get("ingredients", "").strip()
            if not ingredients:
                return JSONResponse({"error": "No ingredients provided"}, status_code=400)
            system = (
                f"Precise, creative meal planner. Build the best recipe from listed ingredients. "
                f"Steps: active voice, no filler. "
                f"Rules: use most ingredients (onHand:true), groceryList essentials only, accurate nutrition. "
                f"Return ONLY valid JSON:\n{RECIPE_SCHEMA}"
            )
            user_msg = f"Ingredients I have: {ingredients}"

        elif mode == "goals":
            goal = body.get("goal", "").strip()
            if not goal:
                return JSONResponse({"error": "No goal provided"}, status_code=400)
            system = (
                f"Precise meal planner and nutritionist. Design a meal hitting the stated targets exactly. "
                f"Steps: active voice, no filler. "
                f"Rules: match macros/calories precisely, all onHand:false, full groceryList with realistic costs, accurate nutrition. "
                f"Return ONLY valid JSON:\n{RECIPE_SCHEMA}"
            )
            user_msg = f"Goal: {goal}"

        else:
            return JSONResponse({"error": "Invalid mode. Use 'goals' or 'fridge'."}, status_code=400)

        message = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )

        text = message.content[0].text.strip()

        # Parse JSON — try direct first, then regex fallback
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
        print(f"[generate error] {e}")
        return JSONResponse({"error": "Failed to generate recipe. Please try again."}, status_code=500)

# ── HEALTH CHECK ─────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok"}

# ── STATIC FILES ─────────────────────────────────────────────────
app.mount("/", StaticFiles(directory="static", html=True), name="static")
