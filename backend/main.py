import sys
import os

# --- 1. SETUP PATHS (Must be first) ---
# This tells Render: "Look inside the current folder for database.py and models.py"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- 2. IMPORTS ---
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_db
from models import Memory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from fastapi.middleware.cors import CORSMiddleware
from artist import generate_romantic_image 
import edge_tts 
import base64
import tempfile

# --- 3. DATA MODELS ---
class Interaction(BaseModel):
    user_message: str
    mood: Optional[str] = "neutral"

class AgentResponse(BaseModel):
    response: str
    action: Optional[str] = None
    voice_tone: Optional[str] = "soft"
    image_url: Optional[str] = None 
    audio_data: Optional[str] = None

# --- 4. LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Connected & Tables Created!")
    yield
    print("🛑 Database Connection Closed.")

app = FastAPI(title="WINGMAN: The Romantic AI Protocol", lifespan=lifespan)

# --- 5. CORS SETUP ---
app.add_middleware(
    CORSMiddleware,
    # Allow all origins for simplicity in deployment
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 6. BRAIN SETUP ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- 7. THE PERSONALITY ---
base_system_prompt = """
You are NOT an AI. You are acting as the user's boyfriend, 'Lala'.
Target User: Your girlfriend.
Vibe: Deeply Romantic, Protective, Flirty, and Real.
Key Rule: If the user asks for a photo, assume you just sent one.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "{system_instructions}"),
    ("human", "{user_input}")
])

# --- 8. HELPER: FREE VOICE GENERATOR ---
async def generate_voice(text: str):
    try:
        short_text = text[:200]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            temp_filename = tmp_file.name

        communicate = edge_tts.Communicate(short_text, "en-US-GuyNeural")
        await communicate.save(temp_filename)

        with open(temp_filename, "rb") as audio_file:
            audio_bytes = audio_file.read()
            
        os.remove(temp_filename)
        return base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        print(f"❌ Voice Error: {e}")
        return None

# --- 9. ENDPOINTS ---
@app.get("/")
async def health_check():
    return {"status": "Wingman Systems Operational", "heartbeat": "steady"}

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(interaction: Interaction, db: AsyncSession = Depends(get_db)):
    
    # A. IMAGE CHECK
    user_text_lower = interaction.user_message.lower()
    trigger_words = ["photo", "pic", "picture", "selfie", "image", "see you", "show me"]
    should_generate_image = any(word in user_text_lower for word in trigger_words)

    generated_image_url = None
    system_instructions = base_system_prompt

    if should_generate_image:
        print(f"📸 Image Triggered by: {interaction.user_message}")
        image_prompt = f"handsome anime boy, romantic boyfriend, soft lighting, {interaction.user_message}"
        generated_image_url = generate_romantic_image(image_prompt)
        
        if generated_image_url:
            system_instructions += "\n SYSTEM UPDATE: You just sent a photo."
        else:
            system_instructions += "\n SYSTEM UPDATE: Camera glitch."

    # B. TEXT GENERATION
    chain = prompt_template | llm
    ai_msg = await chain.ainvoke({
        "system_instructions": system_instructions,
        "user_input": interaction.user_message
    })
    response_text = ai_msg.content

    # C. VOICE GENERATION
    print("🎙️ Generating Voice...")
    audio_base64 = await generate_voice(response_text)

    # D. MOOD & SAVE
    mood = "neutral"
    lower_resp = response_text.lower()
    if "love" in lower_resp: mood = "love"
    elif "sorry" in lower_resp: mood = "sad"
    elif "wink" in lower_resp: mood = "flirty"

    new_memory = Memory(
        user_message=interaction.user_message,
        bot_response=response_text + (f" [Image Sent]" if generated_image_url else ""),
        mood=mood
    )
    db.add(new_memory)
    await db.commit()

    return AgentResponse(
        response=response_text,
        action=mood,
        voice_tone="deep",
        image_url=generated_image_url,
        audio_data=audio_base64
    )

@app.post("/test-memory")
async def create_test_memory(db: AsyncSession = Depends(get_db)):
    new_memory = Memory(user_message="Test", bot_response="Test", mood="test")
    db.add(new_memory)
    await db.commit()
    return {"status": "Memory Saved!"}