import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
r = httpx.get(
    "https://openrouter.ai/api/v1/auth/key",
    headers={"Authorization": f"Bearer {api_key}"},
)
r.raise_for_status()
data = r.json()["data"]
print(f"Credits remaining: ${data['limit_remaining']:.4f}")
print(f"  Limit:           ${data['limit']:.4f}")
print(f"  Used (total):    ${data['usage']:.4f}")
print(f"  Used (today):    ${data['usage_daily']:.4f}")
