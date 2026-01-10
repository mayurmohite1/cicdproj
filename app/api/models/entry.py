from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import uuid4

class Entry(BaseModel):
    
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the entry (UUID)."
    )
    work: str = Field(
        ...,
        max_length=256,
        description="What did you work on today?"
    )
    struggle: str = Field(
        ...,
        max_length=256,
        description="What’s one thing you struggled with today?"
    )
    intention: str = Field(
        ...,
        max_length=256,
        description="What will you study/work on tomorrow?"
    )
    created_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was created."
    )
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the entry was last updated."
    )

    class Config:
        pass
