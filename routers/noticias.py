from fastapi import APIRouter, HTTPException
import os
import httpx
router = APIRouter()

@router.get("/", response_description="Obtener noticias")
async def get_noticias(q: str = "tecnología", language: str = "es"):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "language": language,
        "apiKey": os.getenv("NEWS_API_KEY")
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=str(e))
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))
