from fastapi import FastAPI, Depends
from notes_services.schemas import *
from notes_services.models import Notes, get_db, session
from settings import settings
from sqlalchemy.orm import Session


note_app = FastAPI()

@note_app.get('/')
def root_note():
    return {'message' : "Notes_services"}

@note_app.post('/create')
def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    db_note = Notes(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return {
        "message" : "New note is created",
        "data" : db_note.to_dict
    }