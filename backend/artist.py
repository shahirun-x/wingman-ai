import urllib.parse
import random

# The "Artist" Agent Function (Free Version via Pollinations.ai)
def generate_romantic_image(prompt_description: str):
    print(f"🎨 Artist Agent Triggered (Free Mode): {prompt_description}")
    
    try:
        # 1. Clean up the prompt for the URL
        # We add "anime style" and "warm lighting" to ensure it fits the Hello Kitty vibe
        full_prompt = f"anime style, cute romantic boyfriend, soft pastel colors, {prompt_description}"
        encoded_prompt = urllib.parse.quote(full_prompt)
        
        # 2. Generate a random seed (so the image changes every time)
        seed = random.randint(1, 10000)
        
        # 3. Construct the Pollinations URL
        # We use the 'flux' model which is great for anime
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&seed={seed}&model=flux"
        
        return image_url
        
    except Exception as e:
        print(f"❌ Artist Error: {e}")
        return None