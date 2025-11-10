import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from database import create_document
from schemas import ContactSubmission

app = FastAPI(title="Interior Designer Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Portfolio API running"}

# Lightweight content served by backend to keep frontend simple
class Project(BaseModel):
    slug: str
    title: str
    year: str
    location: Optional[str] = None
    cover: str
    area: Optional[str] = None
    scope: Optional[str] = None
    excerpt: Optional[str] = None
    images: Optional[List[str]] = None

# Static demo data (images from unsplash placeholders)
PROJECTS: List[Project] = [
    Project(
        slug="calm-townhouse",
        title="Calm Townhouse",
        year="2023",
        location="Brooklyn, NY",
        cover="https://images.unsplash.com/photo-1505691723518-36a5ac3b2d51?q=80&w=1600&auto=format&fit=crop",
        area="2,100 sq ft",
        scope="Full Remodel",
        excerpt="A warm, edited palette with natural light and crafted finishes.",
        images=[
            "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=2000&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=2000&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=2000&auto=format&fit=crop",
        ],
    ),
    Project(
        slug="quiet-loft",
        title="Quiet Loft",
        year="2022",
        location="SoHo, NY",
        cover="https://images.unsplash.com/photo-1524758631624-e2822e304c36?q=80&w=1600&auto=format&fit=crop",
        area="1,450 sq ft",
        scope="Furnishing & Styling",
        excerpt="Soft textures and layered neutrals in a sunlit loft.",
        images=[
            "https://images.unsplash.com/photo-1493666438817-866a91353ca9?q=80&w=2000&auto=format&fit=crop",
            "https://images.unsplash.com/photo-1501045661006-fcebe0257c3f?q=80&w=2000&auto=format&fit=crop",
        ],
    ),
]

@app.get("/api/projects", response_model=List[Project])
def get_projects():
    return PROJECTS

@app.get("/api/projects/{slug}", response_model=Project)
def get_project(slug: str):
    for p in PROJECTS:
        if p.slug == slug:
            return p
    raise HTTPException(status_code=404, detail="Project not found")

# Contact endpoint using database
def collection_name(model_cls) -> str:
    return model_cls.__name__.lower()

@app.post("/api/contact")
def submit_contact(payload: ContactSubmission):
    try:
        doc_id = create_document(collection_name(ContactSubmission), payload)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
