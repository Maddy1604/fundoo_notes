from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NoteBase(BaseModel):
    id : int
    title : str
    description : Optional[str]
    color : Optional[str]
    is_archive : Optional[bool] = False
    is_trash : Optional[bool] = False
    reminder : Optional[datetime]
    user_id : Optional[int]

class NoteCreate(NoteBase):
    id : int
    title: str
    description: Optional[str] = None
    color: Optional[str] = None
    reminder: Optional[datetime] = None
    user_id: Optional[int]

class NoteUpdate(NoteBase):
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_archive: Optional[bool] = None
    is_trash: Optional[bool] = None
    reminder: Optional[datetime] = None
    user_id: Optional[int]


class NoteInDB(NoteBase):
    id: int
    user_id: int