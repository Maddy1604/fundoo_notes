# Importing pydantic modules for validation
from pydantic import BaseModel
from datetime import datetime

# Schema for creating new note | schemas means basically structure with validating rules
class CreateNote(BaseModel):
    title: str
    description: str
    color: str
    is_archive: bool= False
    is_trash: bool= False
    reminder: datetime | None = None
    
class CreateLable(BaseModel):
    name : str
    color : str
    