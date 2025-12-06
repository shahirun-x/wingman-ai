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
import os

# --- 1. DATA MODELS (These were missing!) ---
class Interaction(BaseModel):
    user_message: str
    mood: Optional[str] = "neutral"

class AgentResponse(BaseModel):
    response: str
    action: Optional[str] = None # e.g., "blush", "smile", "cry"
    voice_tone: Optional[str] = "soft"

# --- 2. LIFESPAN MANAGER ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database Connected & Tables Created!")
    yield
    # Shutdown
    print("🛑 Database Connection Closed.")

app = FastAPI(title="WINGMAN: The Romantic AI Protocol", lifespan=lifespan)
# Replace your current CORS block with this one:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://friendly-lamp-4j9wjjp7vgxxhqj66-5173.app.github.dev" # <--- YOUR EXACT FRONTEND URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- 3. BRAIN SETUP ---
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# --- 4. THE PERSONALITY (Updated to sound like YOU) ---
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
    You are NOT an AI assistant. You are acting as the user's boyfriend.
    Your Name: Lala (or whatever nickname she calls you).
    Target User: Your girlfriend.
    
    YOUR VIBE:
    1. Deeply Romantic & Protective: You love her immensely. Make her feel safe. Roast her also sometimes.
    2. Creative & Flirty: You are playful. Tease her a little, but always be sweet.
    3. Tech-Savvy but Human: You are smart, but talk like a real person texting on WhatsApp/Instagram. 
    4. Length: Keep texts realistic. Don't write essays. Short, punchy, loving.
    
    GOAL: Make her feel like she is talking directly to her boyfriend.
    """),
    ("human", "{user_input}")
])

@app.get("/")
async def health_check():
    return {"status": "Wingman Systems Operational", "heartbeat": "steady"}

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(interaction: Interaction, db: AsyncSession = Depends(get_db)):
    
    # A. GENERATE RESPONSE
    chain = prompt_template | llm
    ai_msg = await chain.ainvoke({"user_input": interaction.user_message})
    response_text = ai_msg.content

    # B. DETERMINE MOOD
    # If text contains sweet words, set mood to happy/blush
    mood = "neutral" 
    lower_text = response_text.lower()
    
    if any(x in lower_text for x in ["love", "baby", "babe", "miss you", "beautiful"]):
        mood = "love" # Special mood for romance
    elif any(x in lower_text for x in ["sorry", "sad", "hurt"]):
        mood = "sad"
    elif any(x in lower_text for x in ["wink", "haha", "come here"]):
        mood = "flirty"

    # C. SAVE MEMORY TO DB
    new_memory = Memory(
        user_message=interaction.user_message,
        bot_response=response_text,
        mood=mood
    )
    db.add(new_memory)
    await db.commit()
    # No verify/refresh needed here for performance, we just return the chat.

    # D. RETURN RESPONSE
    return AgentResponse(
        response=response_text,
        action=mood,
        voice_tone="deep_and_soft" # Masculine tone setting
    )

# --- TEMPORARY TEST ENDPOINT ---
@app.post("/test-memory")
async def create_test_memory(db: AsyncSession = Depends(get_db)):
    new_memory = Memory(
        user_message="Test message",
        bot_response="Test response",
        mood="test"
    )
    db.add(new_memory)
    await db.commit()
    return {"status": "Memory Saved!"}