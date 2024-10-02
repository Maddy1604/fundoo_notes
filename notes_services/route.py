from fastapi import FastAPI, Depends, HTTPException, Security, Request, status
from sqlalchemy.orm import Session
from .models import Notes, get_db 
from .schemas import CreateNote
from fastapi.security import APIKeyHeader
from .utils import auth_user

# Initialize FastAPI app with dependency
app = FastAPI(dependencies= [Security(APIKeyHeader(name= "Authorization", auto_error= False)), Depends(auth_user)])

@app.get("/")
def read_root():
    '''
    Discription: This is the handler function that gets called when a request is made to the root endpoint
    Parameters: None
    Return: A dictionary with a welcome message.
    '''
    return {"message": "Welcome to the Notes services API!"}

# CREATE Note
@app.post("/notes/")
def create_note(request: Request, note: CreateNote, db: Session = Depends(get_db)):
    '''
    Description: 
    This function creates a new note with the provided title, description and color. The user_id is hardcoded.
    Parameters: 
    note: A `CreateNote` schema instance containing the note details.
    db: The database session to interact with the database.
    Return: 
    The newly created note instance with its details.
'''
    data = note.model_dump()
    data.update(user_id = request.state.user["id"])
    
    new_note = Notes(**data)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return {
        "message": "Note created successfully",
        "status": "success",
        "data": new_note
    }

# GET all notes
@app.get("/notes/")
def get_notes(request: Request,  db: Session = Depends(get_db)):
    '''
    Description: 
    This function retrieves a list of notes with pagination (skip and limit).
    Parameters: 
    db: The database session to interact with the database.
    Return: 
    A list of notes within the given range (based on skip and limit).
    '''
    #print(request.state.user)
    user_data = request.state.user
    
    # Get user_id from response
    user_id = user_data["id"] 
    
    # Query notes that belong to the authenticated user
    notes = db.query(Notes).filter(Notes.user_id == user_id).all()
    
    return notes


# UPDATE Note
@app.put("/notes/{note_id}")
def update_note(note_id: int, updated_note: CreateNote, db: Session = Depends(get_db)):
    '''
    Description: 
    This function updates an existing note's details by its ID. If not found, raises a 404 error.
    Parameters: 
    note_id: The ID of the note to update.
    updated_note: A `CreateNote` schema instance containing the updated details.
    db: The database session to interact with the database.
    Return: 
    The updated note object after saving the changes.
    '''
    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    for key, value in updated_note.model_dump().items():
        setattr(note, key, value)
    
    db.commit()
    db.refresh(note)
    return {
        "message": "Note updated successfully",
        "status": "success",
        "data": note
    }

# DELETE Note
@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    '''
    Description: 
    This function deletes a note by its ID. If not found, raises a 404 error.
    Parameters: 
    note_id: The ID of the note to delete.
    db: The database session to interact with the database.
    Return: 
    A success message confirming the deletion of the note.
    '''

    note = db.query(Notes).filter(Notes.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return {
        "message": "Note deleted successfully!",
        "status": "success",
        "data": note
        }

@app.patch('/notes/{note_id}/archive')
def toggle_archive(request : Request, note_id : int, db : Session = Depends(get_db), user : dict = Depends(auth_user)):
    note = db.query(Notes).filter(Notes.id == note_id,  Notes.user_id == user["id"]).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    note.is_archive = not note.is_archive   
    db.commit()
    db.refresh(note)
    return{
        "message" : "Note is archived successfully,",
        "status" : "Successs",
        "data": note
    }
    
@app.get('/notes/archived')
def archived_notes(user : dict = Depends(auth_user), db : Session = Depends(get_db)):
    note = db.query(Notes).filter(Notes.user_id == user["id"], Notes.is_archive == True).all()
    return{
        "message" : "Archived notes sucessfully.",
        "status" : "Success",
        "data" : note
    }

@app.patch('/notes/{note_id}/trash')
def toggle_trash(note_id : int, db : Session = Depends(get_db), user : dict = Depends(auth_user)):
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user["id"]).first()
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    note.is_trash = not note.is_trash
    db.commit()
    db.refresh(note)
    return{
        "message" : "Note is trashed successfully.",
        "status" : "Success",
        "data" : note
    }

@app.get('/notes/trash')
def trashed_note(user : dict = Depends(auth_user), db : Session = Depends(get_db)):
    note = db.query(Notes).filter(Notes.user_id == user["id"], Notes.is_trash ==True).all()
    return{
        "message" : "Note trashed successfully.",
        "status" : "Success",
        "data" : note
    }