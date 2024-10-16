# Importing pydantic modules for validation
from pydantic import BaseModel
from datetime import datetime
from typing import List

# Schema for creating new note | schemas means basically structure with validating rules
class CreateNote(BaseModel):
    title: str
    description: str
    color: str
    is_archive: bool= False
    is_trash: bool= False
    reminder: datetime | None = None
    
class CreateLabel(BaseModel):
    name : str
    color : str
    
class NoteLabel(BaseModel):
    label_id : List[int]

class Collaborator(BaseModel):
    user_id : int
    access : str

class AddCollaborator(BaseModel):
    note_id : int
    user_ids : List[int]
    access : str

class RemoveCollaborator(BaseModel):
    note_id : int
    user_ids : List[int]

