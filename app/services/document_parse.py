import httpx
import os

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")

async def parse_pdf(file_path: str):
    url = "https://api.upstage.ai/v1/document/parse"
    headers = {"Authorization": f"Bearer {UPSTAGE_API_KEY}"}
    files = {"file": open(file_path, "rb")}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()
