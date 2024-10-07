from fastapi import FastAPI, Depends, HTTPException, Security, Request, status
from sqlalchemy.orm import Session
from .models import Notes, get_db, Labels
from .schemas import CreateNote, CreateLable
from fastapi.security import APIKeyHeader
from .utils import auth_user, JwtUtils, JwtUtilsLables


# Initialize FastAPI app with dependency
app = FastAPI(dependencies= [Security(APIKeyHeader(name= "Authorization", auto_error= False)), Depends(auth_user)])

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

    # Importing class for create and store notes in this it takes name:user_id(str), key:note_id and value:note data
    JwtUtils.save(name=f"user_{request.state.user['id']}", key=f"note_{new_note.id}", value=new_note.to_dict)
    
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
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]

    # By using redis calss geting name with property of user_id in the string format
    notes = JwtUtils.get(name=f"user_{user_id}")
    source = "cache"

    # Query notes that belong to the authenticated user
    if not notes:
        source = "Database"
        notes = db.query(Notes).filter(Notes.user_id == user_id).all()
    
    
    return {
        "message" : "Get all notes",    
        "status" : "Success",
        "source" : source,
        "data" : notes
    }


# UPDATE Note
@app.put("/notes/{note_id}")
def update_note(request:Request, note_id: int, updated_note: CreateNote, db: Session = Depends(get_db)):
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
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]

    # for update note finding note based on note is and user id is correct it will update note if note then raise exception
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Based on key and values pair data is updated 
    for key, value in updated_note.model_dump().items():
        setattr(note, key, value)
    
    db.commit()
    db.refresh(note)

    # Assigning class for update notes in this it takes name:user_id(str), key:note_id and value:note data
    JwtUtils.save(name=f"user_{user_id}", key=f"note_{note_id}", value=note.to_dict)
    return {
        "message": "Note updated successfully",
        "status": "success",
        "data": note
    }

# DELETE Note
@app.delete("/notes/{note_id}")
def delete_note(request:Request, note_id: int, db: Session = Depends(get_db)):
    '''
    Description: 
    This function deletes a note by its ID. If not found, raises a 404 error.
    Parameters: 
    note_id: The ID of the note to delete.
    db: The database session to interact with the database.
    Return: 
    A success message confirming the deletion of the note.
    '''
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]

    # For deletetion purpose it finds the note based on note_ id and user_id respectively both
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id).first()

    # Assigning class for delete notes in this it takes name:user_id(str), key:note_id
    JwtUtils.delete(name=f"user_{user_id}", key=f"note_{note_id}")
    
    # If note is not found in database it will rasie exception
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()

    return {
        "message": "Note deleted successfully!",
        "source" : "Success"
        }

# Archive notes by note id
@app.patch('/notes/archive/{note_id}')
def toggle_archive(request : Request, note_id : int, db : Session = Depends(get_db)):
    """
    Description: 
    This function archives the note by its ID. If not found, raises a 404 error.
    It takes parameter as request wiht Request type, note_is as int type, db as session wiht dependency with get_db
    Parameters: 
    request : Request type
    note_id: The ID of the note to archived note.
    db: The database session to interact with the database.
    Return: 
    A success message wiht all archied notes for respective user.
    """
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]
    try:
        # Before archiving note it will check note with note id, user id and also check that note should note in trash 
        note = db.query(Notes).filter(Notes.id == note_id,  Notes.user_id == user_id, Notes.is_trash == False).first()
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        # if note is not archive is aasigned to archived_notes  
        note.is_archive = not note.is_archive   
        db.commit()
        db.refresh(note)
        return{
            "message" : "Note is archived successfully,",
            "status" : "Successs",
            "data": note
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unathorized user")

# Get all archived note    
@app.get('/notes/archived')
def archived_notes(request : Request, db : Session = Depends(get_db)):
    """
    Description: 
    This function shows archive notes. If not found, raises a 400 error.
    Parameters: 
    request : Request type
    db: The database session to interact with the database.
    Return: 
    A success message conformation and show all archived notes.
    """
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]
    try:
        # To get the archived notes it will check with note id and user id and note should be in archived section
        note = db.query(Notes).filter(Notes.user_id == user_id, Notes.is_archive == True).all()

        return{
            "message" : "Archived notes sucessfully.",
            "status" : "Success",
            "data" : note
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty archived section")

# Trash notes by notes id
@app.patch('/notes/trash/{note_id}')
def toggle_trash(request : Request, note_id : int, db : Session = Depends(get_db)):
    """
    Description: 
    This function trash the notes by its ID. If not found, raises a 404 error.
    Parameters: 
    request : Request type
    note_id: The ID of the note to archived note.
    db: The database session to interact with the database.
    Return: 
    A success message wiht trash notes for respective user.
    """
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]
    try:
        # Before putting note in trash it will check note with note id, user id and also check that note should note in archived 
        note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id, Notes.is_archive == False).first()
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
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")

# Get all trash notes
@app.get('/notes/trash')
def trashed_note(request : Request, db : Session = Depends(get_db)):
    """
    Description: 
    This function shows trash notes. If not found, raises a 400 error.
    Parameters: 
    request : Request type
    db: The database session to interact with the database.
    Return: 
    A success message conformation and show all trash notes.
    """
    # Assigning user id which is stored in request state to user_id
    user_id = request.state.user["id"]
    try:
        # To get the trash notes it will check with note id and user id and note should be in trash section
        note = db.query(Notes).filter(Notes.user_id == user_id, Notes.is_trash ==True).all()
        return{
            "message" : "Note trashed successfully.",
            "status" : "Success",
            "data" : note
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty trash section")
    
# Creation of lables
@app.post('/create/lable')
def create_lable(request :Request, lable : CreateLable, db : Session = Depends(get_db)):
    """
    Description : This function is call for creation of new lables in database
    Parameters : 
    requerst : Request type for requesting user data by authentication
    lable : schemas is assigned for new lable creation
    db : Database session to interact with labels database
    """
    # To create new lable and getting user information from request.state as user id 
    data = lable.model_dump()
    data.update(user_id = request.state.user["id"])
    
    # New lable is created and dict of data passed to the Lables model | ** is dictionary unpacking
    new_lable = Labels(**data)
    db.add(new_lable)
    db.commit()
    db.refresh(new_lable)

    JwtUtilsLables.save(name=f"user_{request.state.user['id']}", key=f"lable_{new_lable.id}", value=new_lable.to_dict)

    return {
        "message": "Lable is created successfully",
        "source": "Success",
        "data": new_lable
    }

@app.get('/get/lables')
def get_lable(request : Request, db : Session = Depends(get_db)):
    """
    Description: This function is called for getting all created lables for respective user
    Parameter:
    request : Takes Request type 
    db : create database session to interact with database
    """
    # user data gets all user information which stores in request.state.user
    # from all information usder id is assgin with actual id of user
    user_id = request.state.user["id"]

    # By using redis calss geting name with property of user_id in the string format
    labels = JwtUtilsLables.get(name=f"user_{user_id}")
    
    source = "cache"

    if not labels:
        source = "Database"
        labels = db.query(Labels).filter(Labels.user_id == user_id).all()

    return{
            "message" : "Get all lables",
            "status" : "success",
            "source" : source,
            "data" : labels
        }

@app.put('/lable/update/{lable_id}')
def update_lable(request : Request, lable_id : int, update_lable : CreateLable, db : Session = Depends(get_db)):
    """
    Description: This finction is called for update the label using lable id 
    Parameter:
    request : Assign Request type
    lable id : which is in int format
    update lable : Take create lable scchemas
    db : create database session to interact with database
    """
    try:
        # user data gets all user information which stores in request.state.user
        # from all information usder id is assgin with actual id of user
        user_id = request.state.user["id"]
        
        # db query is run for finding out labels with lable id also user id user id from stored state
        lable = db.query(Labels).filter(Labels.id == lable_id, Labels.user_id == user_id ).first()
        if not lable_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lable is not found")
        
        # if lables is found with lable id then setting values according to ket and value pair
        for key, value in update_lable.model_dump().items():
            setattr(lable, key, value)

        db.commit()
        db.refresh(lable)

        put_lable = JwtUtilsLables.save(name=f"user_{user_id}", key=f"lable_{lable_id}", value=lable.to_dict)
        return{
            "message" : "Lable updated successfully.",
            "Source" : "Success",
            "data" : put_lable
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unathurized access")

@app.delete('/lable/delete/{lable_id}')
def delete_lable(request : Request, lable_id : int, db : Session = Depends(get_db)):
    """
    Description: This finction is called for delete the label using lable id 
    Parameter:
    request : Assign Request type
    lable id : which is in int format
    db : create database session to interact with database
    """
    try:
        # user data gets all user information which stores in request.state.user
        # from all information usder id is assgin with actual id of user
        user_id = request.state.user["id"]

        # db query is run for finding out labels with lable id also user id user id from stored state
        # if not found raise exception
        lable = db.query(Labels).filter(Labels.id == lable_id, Labels.user_id == user_id).first()

        # Assigning class for delete lable in this it takes name:user_id(str), key:lable_id
        JwtUtilsLables.delete(name=f"user_{user_id}", key=f"lable_{lable_id}")

        # If lable is is not there then it will rasie exception
        if not lable_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lable with {lable_id} this id not found")
        
        db.delete(lable)
        db.commit()
        return{
            "message" : "Lable is deleted sucessfully.",
            "status" : "Success"
        }
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized acess")      