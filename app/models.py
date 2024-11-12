# models.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
import pycountry

class UserProfile(BaseModel):
    """User profile data model"""
    name: str = Field(min_length=3, max_length=30)
    age: int = Field(gt=10)
    sex: str = Field(min_length=3)
    weight: float = Field(ge=30)
    height: float = Field(ge=120)
    goals: str = Field(min_length=5)
    country: str = Field(min_length=3)
    
    @validator('country')
    def validate_country(cls, v):
        if not pycountry.countries.get(name=v):
            raise ValueError(f"Invalid country: {v}")
        return v

class WorkoutSession(BaseModel):
    """Workout session data model"""
    date: datetime
    weight: float
    mood: str
    intensity: str
    exercises: List[dict]
    notes: Optional[str]