"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

# Portfolio-specific schemas

class SocialLinks(BaseModel):
    github: Optional[HttpUrl] = None
    linkedin: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

class Developer(BaseModel):
    """
    Developer profile schema
    Collection name: "developer"
    """
    name: str = Field(..., description="Full name")
    title: str = Field(..., description="Professional title")
    bio: str = Field(..., description="Short biography")
    location: Optional[str] = Field(None, description="Location")
    years_experience: Optional[int] = Field(0, ge=0, le=60)
    skills: List[str] = Field(default_factory=list)
    social: SocialLinks = Field(default_factory=SocialLinks)
    email: Optional[EmailStr] = None

class Project(BaseModel):
    """
    Projects collection schema
    Collection name: "project"
    """
    name: str
    description: str
    tech_stack: List[str] = Field(default_factory=list)
    repo_url: Optional[HttpUrl] = None
    live_url: Optional[HttpUrl] = None
    image_url: Optional[HttpUrl] = None
    highlights: List[str] = Field(default_factory=list)

class Message(BaseModel):
    """
    Contact messages collection schema
    Collection name: "message"
    """
    name: str
    email: EmailStr
    message: str

# Example schemas (kept for reference and potential future use):
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
