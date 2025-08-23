import httpx
from app.core.config import settings

async def parse_pdf(file_path: str):
    url = "https://api.upstage.ai/v1/document/parse"
    headers = {"Authorization": f"Bearer {settings.UPSTAGE_API_KEY}"}
    files = {"file": open(file_path, "rb")}

    async with httpx.AsyncClient() as client:
        res = await client.post(url, headers=headers, files=files)
        res.raise_for_status()
        return res.json()
