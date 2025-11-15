import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Developer, Project, Message

app = FastAPI(title="Developer Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Django Developer Portfolio API"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
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

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Seed endpoint to insert default profile if empty
@app.post("/seed")
def seed_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Check if developer profile exists
    existing = db["developer"].find_one({})
    if existing:
        return {"status": "ok", "message": "Profile already exists"}

    dev = Developer(
        name="Alex Carter",
        title="Senior Django Developer",
        bio=(
            "I build scalable, secure backend systems with Django and FastAPI. "
            "I love clean architecture, TDD, and DevOps automation."
        ),
        location="Remote • GMT+1",
        years_experience=7,
        skills=[
            "Python", "Django", "Django REST Framework", "PostgreSQL", "Redis",
            "Celery", "Docker", "Kubernetes", "AWS", "FastAPI", "GraphQL",
            "CI/CD", "TDD"
        ],
        social={
            "github": "https://github.com/example",
            "linkedin": "https://www.linkedin.com/in/example/",
            "website": "https://example.dev"
        },
        email="alex@example.dev"
    )
    create_document("developer", dev)

    projects = [
        Project(
            name="SaaS Subscription Platform",
            description="Multi-tenant billing, plans, and subscriptions with Stripe integration.",
            tech_stack=["Django", "DRF", "PostgreSQL", "Redis", "Celery", "Stripe"],
            repo_url="https://github.com/example/saas-platform",
            live_url="https://saas.example.dev",
            highlights=[
                "Role-based access control", "Event-driven architecture", "Zero-downtime deploys"
            ]
        ),
        Project(
            name="Real-time Analytics Dashboard",
            description="Stream processing with Kafka and WebSockets for live metrics.",
            tech_stack=["Django", "Channels", "Kafka", "ClickHouse", "Tailwind"],
            repo_url="https://github.com/example/analytics",
            highlights=["<100ms updates", "Horizontal scaling", "90th percentile p95<200ms"]
        ),
        Project(
            name="Headless CMS",
            description="Content platform with rich permissions and GraphQL API.",
            tech_stack=["Django", "DRF", "GraphQL", "PostgreSQL"],
            repo_url="https://github.com/example/headless-cms",
            highlights=["Audit logs", "Workflows", "Versioned content"]
        )
    ]
    for p in projects:
        create_document("project", p)

    return {"status": "ok", "message": "Seeded profile and projects"}

# Public API
class ContactIn(BaseModel):
    name: str
    email: str
    message: str

@app.get("/profile")
def get_profile():
    if db is None:
        return {"name": "Your Name", "title": "Django Developer", "bio": "Update database to enable persistence."}

    doc = db["developer"].find_one({}, {"_id": 0})
    if not doc:
        return {"name": "Your Name", "title": "Django Developer", "bio": "Use /seed to insert sample data."}
    return doc

@app.get("/projects")
def get_projects():
    if db is None:
        return []
    items = get_documents("project", {}, limit=50)
    # strip _id for frontend simplicity
    for i in items:
        i.pop("_id", None)
    return items

@app.post("/contact")
def send_message(payload: ContactIn):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    msg = Message(**payload.model_dump())
    create_document("message", msg)
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
