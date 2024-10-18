from fastapi import FastAPI, Depends, HTTPException, Security, Request, status
from sqlalchemy.orm import Session
from .models import Notes, get_db, Labels
from .schemas import CreateNote, CreateLabel, NoteLabel, AddCollaborator, RemoveCollaborator
from fastapi.security import APIKeyHeader
from .utils import auth_user, JwtUtils, JwtUtilsLabels
from loguru import logger
from celery.schedules import crontab
from redbeat import RedBeatSchedulerEntry as Task
from tasks import celery
import requests as http
from sqlalchemy.orm.attributes import flag_modified
from settings import settings
from sqlalchemy import or_

# Initialize FastAPI app with dependency
app = FastAPI(dependencies= [Security(APIKeyHeader(name= "Authorization", auto_error= False)), Depends(auth_user)])


# CREATE Note
@app.post("/notes/")
def create_note(request: Request, note: CreateNote, db: Session = Depends(get_db)):
    '''
    Description: 
    This function creates a new note with the provided title, description and color. The user_id is hardcoded.
    Parameters: 
    note: A CreateNote schema instance containing the note details.
    db: The database session to interact with the database.
    Return: 
    The newly created note instance with its details.
'''
    try:
        data = note.model_dump()
        data.update(user_id = request.state.user["id"])

        # Fetching user email from request state
        user_email = request.state.user["email"]
        
        new_note = Notes(**data)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        # Importing class for create and store notes in this it takes name:user_id(str), key:note_id and value:note data
        JwtUtils.save(name=f"user_{request.state.user['id']}", key=f"note_{new_note.id}", value=new_note.to_dict)
        logger.info(f"Fetching the note form the cache memory using user ID and note ID")

        # If note is having reminder
        if new_note.reminder:
            
            # Reminder timestamp as a string
            reminder_str = new_note.reminder
            task_name = f"reminder_task_{new_note.id}"
            
            logger.info(f"schedule creater")
            entry = Task(
                name=task_name,
                task= 'tasks.reminder_email', 
                schedule= crontab(
                    minute= reminder_str.minute, 
                    hour= reminder_str.hour,
                    day_of_month= reminder_str.day,
                    month_of_year= reminder_str.month
                ),
                app= celery,
                args=(user_email, new_note.id, new_note.title)
            )
            entry.save()

        logger.info(f"Note is created successfully with Note_id: {new_note.id}")

        # Return the success message
        return {
            "message": "Note created successfully",
            "status": "success",
            "data": new_note
        }
    except Exception as error:
        logger.error(f"Failed to create new note : {error}")
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Unable to create the note")

# GET all notes
@app.get("/notes/")
def get_notes(request: Request, db: Session = Depends(get_db)):
    """
    Description: 
    This function retrieves a list of notes with associated labels and handles caching.
    
    Parameters: 
    - request: The incoming request object containing the user information.
    - db: The database session to interact with the database.

    Return: 
    A list of notes with their labels, retrieved either from cache or database.
    """
    try:
        # Assigning user_id which is stored in request state to user_id
        user_id = request.state.user["id"]

        # Try to retrieve cached notes with labels
        notes_data = JwtUtils.get(name=f"user_{user_id}")
        source = "Cache"

        if not notes_data:
            source = "Database"

            # Query to get all notes for the user, eager load labels
            notes = db.query(Notes).filter(or_(Notes.user_id == user_id, Notes.collaborators.has_key(f"{user_id}"))).all()
            print(notes)

            # Serialize notes and labels to store in cache
            notes_data = [x.to_dict for x in notes]
            logger.info(f"Notes and labels retrieved from Database for user ID: {user_id}")
        else:
            logger.info(f"Notes and labels retrieved from Cache for user ID: {user_id}")

        return {
            "message": "Get all notes with labels",    
            "status": "Success",
            "source": source,
            "data": notes_data
        }

    except Exception as error:
        logger.error(f"Failed to get all notes for user ID: {user_id}. Error: {str(error)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to get all notes")

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
    try:
        # Assigning user id which is stored in request state to user_id
        user_id = request.state.user["id"]

        # For update note finding note based on note is and user id is correct it will update note if note then raise exception
        existing_note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id).first()
        logger.info(f"Featching the note from database using note ID {note_id} for user ID: {user_id}")

        # If note is not existing in database
        if not existing_note:
            logger.info("Note not found")
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Based on key and values pair data is updated 
        for key, value in updated_note.model_dump().items():
            setattr(existing_note, key, value)
        
        # Commit the changes and refresh the database
        db.commit()
        db.refresh(existing_note)
        logger.info(f"Note {note_id} updated successfully")

        # Assigning class for update notes in this it takes name:user_id(str), key:note_id and value:note data
        JwtUtils.save(name=f"user_{user_id}", key=f"note_{note_id}", value=existing_note.to_dict)
        logger.info(f"Note with ID: {note_id} updated successfully for user ID: {user_id}")

        # Fetching user email form request state
        user_email = request.state.user["email"]

        try:
            # Finding the reminder string from existing note
            if existing_note.reminder:
                reminder_str = existing_note.reminder
                task_name = f"reminder_task_{existing_note.id}"
                    
                # Creating the schedular for sending the reminder email to respective user email
                logger.info(f"schedule creater")
                entry = Task(
                        name=task_name,
                        task= 'tasks.reminder_email', 
                        schedule= crontab(
                            minute= reminder_str.minute, 
                            hour= reminder_str.hour,
                            day_of_month= reminder_str.day,
                            month_of_year= reminder_str.month
                        ),
                        app= celery,
                        args=(user_email, existing_note.id, existing_note.title)
                    )
                entry.save()

                logger.info("Note is updated successfully")
            
            # Return the success message
            return {
                "message": "Note updated successfully",
                "status": "success",
                "data": existing_note
            }

        except Exception as error:
            logger.error(f"Unable to update the note : {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falied to update the note")
    
    except Exception as error:
            logger.error(f"Unable to update the note : {error}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Falied to update the note")

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
    try:
        # Assigning user id which is stored in request state to user_id
        user_id = request.state.user["id"]

        # For deletetion purpose it finds the note based on note_ id and user_id respectively both
        note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id).first()

        if not note:
            logger.info(f"Note with Note ID: {note_id} not found for user ID: {user_id} ")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Note {note_id} not found for user {user_id} ")

        logger.info(f"Deleting Note {note_id} for user {user_id}")

        # Assigning class for delete notes in this it takes name:user_id(str), key:note_id
        JwtUtils.delete(name=f"user_{user_id}", key=f"note_{note_id}")
        logger.info(f"Delete Note {note_id} for user {user_id} from cache")
        
        db.delete(note)
        db.commit()

        # Declaration for removal of note from database
        logger.info(f"Note {note_id} for user {user_id} successfully removed")

        # Return the success response
        return {
            "message": "Note deleted successfully!",
            "source" : "Success"
            }
    
    except Exception as error:
        logger.error(f"Error while deleting note : {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error while deleting note : {error}")

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
    try:
        # Assigning user id which is stored in request state to user_id
        user_id = request.state.user["id"]
        
        # Before archiving note it will check note with note id, user id and also check that note should note in trash 
        note = db.query(Notes).filter(Notes.id == note_id,  Notes.user_id == user_id, Notes.is_trash == False).first()
        logger.info(f"Fetching note from database using user id and not trash notes")

        # If note not found in databse raise exception
        if not note:
            logger.info("Notes not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        # To toggel the archived note between true and false
        note.is_archive = not note.is_archive  

        # Commit the chages and refresh the databse with note 
        db.commit()
        db.refresh(note)
        logger.info(f"Changes are saved into database succesfully.")

        # Returning the success message
        return{
            "message" : "Note is archived successfully,",
            "status" : "Successs",
            "data": note
        }
    
    except Exception as error:
        logger.exception(f"Error while archiving the note : {error}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Error while archiving the note : {error}")

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
    try:
        # Assigning user id which is stored in request state to user_id
        user_id = request.state.user["id"]

        # To get the archived notes it will check with note id and user id and note should be in archived section
        note = db.query(Notes).filter(Notes.user_id == user_id, Notes.is_archive == True).all()
        logger.info(f"Fetching notes from databse using user ID: {user_id} and archived notes only")

        # Returning the success message
        return{
            "message" : "Archived notes sucessfully.",
            "status" : "Success",
            "data" : note
        }
    
    except Exception as error:
        logger.error(f"Error while getting archived notes : {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error for getting archived notes")

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
    try:
        # Assigning user id which is stored in request state to user_id
        user_id = request.state.user["id"]

        # Before putting note in trash it will check note with note id, user id and also check that note should note in archived 
        note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id, Notes.is_archive == False).first()
        logger.info(f"Note is find from database and it is not archive")

        # If note is not found
        if not note:
            logger.info("Note not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
        
        # To toggel the trash
        note.is_trash = not note.is_trash
        logger.info(f"Note is trash successfully")

        # Commit the changes in database
        db.commit()
        db.refresh(note)
        logger.info(f"Putting the note in trash for user ID: {user_id}")

        # Return the success message
        return{
            "message" : "Note is trashed successfully.",
            "status" : "Success",
            "data" : note
        }
    except Exception as error:
        logger.error(f"Error while adding note to trash for user ID:{user_id} : {error}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user and note not found user ID: {user_id} and note ID: {note_id}")

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
    try:
        # Assigning user id which is stored in request state to user_id
        user_id = request.state.user["id"]
    
        # To get the trash notes it will check with note id and user id and note should be in trash section
        note = db.query(Notes).filter(Notes.user_id == user_id, Notes.is_trash == True).all()
        logger.info("Note is trash successfully.")

        # Return the success message
        return{
            "message" : "Note trashed successfully.",
            "status" : "Success",
            "data" : note
        }
    
    except Exception as error:
        logger.error(f"Error while getting trash note : {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty trash section")
    
# Creation of new lables
@app.post('/create/label')
def create_label(request :Request, label : CreateLabel, db : Session = Depends(get_db)):
    """
    Description : This function is call for creation of new lables in database
    Parameters : 
    requerst : Request type for requesting user data by authentication
    label : schemas is assigned for new label creation
    db : Database session to interact with labels database
    """
    try:
        # To create new lable and getting user information from request.state as user id 
        data = label.model_dump()
        data.update(user_id = request.state.user["id"])
        logger.info(f"Getting user id form store request state in")
        
        # New lable is created and dict of data passed to the Lables model | ** is dictionary unpacking
        new_label = Labels(**data)
        db.add(new_label)
        logger.info(f"Creating new label and data is added to label")

        # Commit the changes and refreshing the DB
        db.commit()
        db.refresh(new_label)
        logger.info("Adding new label to database and refreshing the database")

        # Updating the cache data with new label
        JwtUtilsLabels.save(name=f"user_{request.state.user['id']}", key=f"lable_{new_label.id}", value=new_label.to_dict)
        logger.info(f"New label is created successfully in cache memory.")

        # Returning the success message
        return {
            "message": "Lable is created successfully",
            "source": "Success",
            "data": new_label
        }
    except Exception as error:
        logger.error(f"Error to create new label : {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error to create new label")

# Fetching labels from databas and cache memory
@app.get('/get/labels')
def get_label(request : Request, db : Session = Depends(get_db)):
    """
    Description: This function is called for getting all created labels for respective user
    Parameter:
    request : Takes Request type 
    db : create database session to interact with database
    """
    try:
        # user data gets all user information which stores in request.state.user
        # from all information usder id is assgin with actual id of user
        user_id = request.state.user["id"]

        # By using redis calss geting name with property of user_id in the string format
        labels = JwtUtilsLabels.get(name=f"user_{user_id}")
        logger.info(f"Fetching labels from the cache")
        source = "cache"

        # If label is not found in cache memory then find in database
        if not labels:
            source = "Database"
            labels = db.query(Labels).filter(Labels.user_id == user_id).all()
            logger.info(f"Fetching labels from the databse")

        # Returing the success message
        return{
                "message" : "Get all lables",
                "status" : "success",
                "source" : source,
                "data" : labels
            }
    except Exception as error:
        logger.error(f"Error to getting labels : {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error to getting labels")

# Updating the labels
@app.put('/label/update/{label_id}')
def update_label(request : Request, label_id : int, update_label : CreateLabel, db : Session = Depends(get_db)):
    """
    Description: This finction is called for update the label using lable id 
    Parameter:
    request : Assign Request type
    lable id : which is in int format
    update label : Take create label scchemas
    db : create database session to interact with database
    """
    try:
        # user data gets all user information which stores in request.state.user
        # from all information usder id is assgin with actual id of user
        user_id = request.state.user["id"]
        
        # db query is run for finding out labels with lable id also user id user id from stored state
        label = db.query(Labels).filter(Labels.id == label_id, Labels.user_id == user_id ).first()
        if not label_id:
            logger.info("Label is not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Label is not found")
        
        # if labels is found with lable id then setting values according to ket and value pair
        for key, value in update_label.model_dump().items():
            setattr(label, key, value)
            logger.info(f"Updating label ID: {label_id} for user ID: {user_id}")

        # Commit the changes in databse and refresh the DB
        db.commit()
        db.refresh(label)
        logger.info(f"Updating and refreshing database for {label}")

        # Updating the cache memory for label
        put_lable = JwtUtilsLabels.save(name=f"user_{user_id}", key=f"lable_{label_id}", value=label.to_dict)
        logger.info(f"Updating label ID: {label_id} for user ID: {user_id} in cache memory")

        # Returning the success message 
        return{
            "message" : "Lable updated successfully.",
            "Source" : "Success",
            "data" : put_lable
        }
    except Exception as error:
        logger.error(f"Error while updating note for user ID: {user_id} : {error}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Error to updating label for user ID: {user_id}")

@app.delete('/lable/delete/{lable_id}')
def delete_lable(request : Request, label_id : int, db : Session = Depends(get_db)):
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
        label = db.query(Labels).filter(Labels.id == label_id, Labels.user_id == user_id).first()

        # Assigning class for delete lable in this it takes name:user_id(str), key:lable_id
        JwtUtilsLabels.delete(name=f"user_{user_id}", key=f"lable_{label_id}")
        logger.info(f"Deleting label with label ID: {label_id} for user ID: {user_id}")

        # If lable is is not there then it will rasie exception
        if not label_id:
            logger.info(f"Lable is not found for label ID: {label_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Lable with {label_id} this id not found")
        
        db.delete(label)
        db.commit()
        logger.info(f"Delete label with Label ID: {label_id}")

        # Return the success message
        return{
            "message" : "Lable is deleted sucessfully.",
            "status" : "Success"
        }
    
    except Exception as error:
        logger.error(f"Error while deleting labels for user {user_id}: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error for deleting labels")
    
    except Exception:
        logger.exception("Unauthorized access")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access")      

# POST api for adding labesl to the notes
@app.post('/notes/{note_id}/add-labels')
def add_labels(request:Request, note_id:int, payload : NoteLabel,  db : Session = Depends(get_db)):
    """
    Description:
    This function is used for adding desired labels to notes
    Parameters:
    request : The incoming request object.
    note_id : The ID of the note to which labels will be added.
    label_ids : A list of label IDs to be added to the note.
    db : The database session dependency.
    Return:
    Return the success message with labels added to notes
    """
    logger.info(f"Adding labels {payload.label_id} to note {note_id} for user.")

    # Getting user_id from request state
    user_id = request.state.user["id"]

    # Finding note from database using not id and user id
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id).first()

    # If note not found in database it will raise the exception
    if not note:
        logger.error(f"Note with id {note_id} not found for user {user_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # Finding labels from database using label id given by user and matching user id
    labels = db.query(Labels).filter(Labels.id.in_(payload.label_id), Labels.user_id == user_id).all()
    if len(labels) != len(payload.label_id):
        logger.info("Not all labels are found for particular user")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="labels not found")
    
    try:
        note.labels.extend(labels)
        db.commit()
        db.refresh(note)
        logger.info(f"Labels {payload.label_id} added successfully to note {note_id} for user {user_id}.")

        # Store the serialized note with labels in the cache
        JwtUtils.save(name=f"user_{user_id}", key=f"note_{note.id}", value=note.to_dict)
        logger.info(f"Labels {payload.label_id} added successfully to  cache with note {note_id} for user {user_id}.")

        # Returning success message
        return{
            "Message": "Lables added successfully",
            "Status" : "Success",
            "Data" : note.labels
        }
    except Exception as error:
        logger.error(f"Error while adding labels from note {note_id} for user {user_id}: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error for adding labels")

# DELETE api for deleting desired labels from the notes
@app.delete('/notes/{note_id}/remove-labels')
def remove_labels(request:Request, note_id:int, payload : NoteLabel, db : Session = Depends(get_db)):
    """
    Description:
    This function is used for removing desired labels to notes
    Parameters:
    request : The incoming request object.
    note_id : The ID of the note to which labels will be added.
    payload : A NoteLable schema add to access lable id.
    db : The database session dependency.
    Return:
    Return the success message with labels remove from notes
    """
    # Getting user_id from request state
    user_id = request.state.user["id"]

    # Finding note from database using not id and user id
    note = db.query(Notes).filter(Notes.id == note_id, Notes.user_id == user_id).first()

    # If note not found in database it will raise the exception
    if not note:
        logger.error(f"Note with id {note_id} not found for user {user_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    # Finding labels from database using label id given by user and matching user id
    labels = db.query(Labels).filter(Labels.id.in_(payload.label_id), Labels.user_id == user_id).all()
    if not labels:
        logger.info("Not all labels are found for particular user")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="labels not found")
    
    try:
        # Checking label for in find labels
        for label in labels:
            # if label are there then delete it
            if label in note.labels:
                note.labels.remove(label)
                logger.info(f"Label {payload.label_id} is deleted form the database")

        # Commiting the changes and refreshing database       
        db.commit()
        db.refresh(note)
        logger.info(f"Labels {payload.label_id} removed successfully to note {note_id} for user {user_id}.")
        
        # Deleteing labels from note in cache database 
        cached_notes = JwtUtils.get(name = f"user_{user_id}")
        if cached_notes:
            for cached_note in cached_notes:
                if cached_note["id"] == note_id: #Assign note id from cached_note to note id
                    updated_labels = [lebel for lebel in cached_note['labels'] if lebel["id"] not in payload.label_id]
                    cached_note['labels'] = updated_labels  #updating cached labesl and saving it
                    logger.info(f"Labels {payload.label_id} removed successfully to note {note_id} for user {user_id}.")

                    # Saving the updated note and lables in cache 
                    JwtUtils.save(name = f"user_{user_id}", key=f"note_{note_id}", value=cached_note)
                    logger.info(f"Labels updated and save successfully to note {note_id} for user {user_id}.")
        
        # Returning the success message
        return{
            "Mesaage" : "Lables are deleted successfully",
            "Status" : "Success",
            "Data" : cached_note
        }
    except Exception as error:
        logger.error(f"Error while removing labels from note {note_id} for user {user_id}: {error}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error removing labels")

# Add collaborators to note
@app.patch('/notes/add-collaborators')
def add_collaborators(request : Request, payload : AddCollaborator, db : Session = Depends(get_db)):
    """
    Description:
    This function is used for adding collaborators from notes
    Parameters:
    request : The incoming request object.
    payload : A AddCollaborator schema add to access user ids.
    db : The database session dependency.
    Return:
    Return the success message with collaborator add from notes
    """
    try:
        # Fetching user id from request.state
        user_id = request.state.user["id"]

        # Fetching note for particular user based on note id provided by user
        note = db.query(Notes).filter(Notes.id == payload.note_id, Notes.user_id == user_id).first()
        logger.info(f"Feteching note based Note ID : {payload.note_id} and user ID : {user_id}")

        # If note not found
        if not note:
            logger.info(f"Note is not found for note ID : {payload.note_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Note not found in database for user ID : {user_id} wiht note ID: {payload.note_id}")

        # User can not add themselves as collaborator
        if user_id in payload.user_ids:
            logger.info(f"User ID {user_id} cannot add themselves as a collaborator.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot add yourself as a collaborator.") 
        
        # Making HTTP request to user_Services to validate the users 
        user_service_url = settings.USER_SERVICE_URL
        response = http.get(user_service_url, params = {"user_ids" : payload.user_ids})
       
        # It chaecks the response is not satisfying then raise error
        if response.status_code != 200:
            logger.info(f"Some of the users are not found of user ID : {payload.user_ids}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Some of the uses not found")
        
        # Getting user data in json format form response  
        user_data = response.json()["data"]

        # Checking for all user data is retrived from user services or not
        if len(user_data) != len(payload.user_ids):
            logger.info("Some of the users are not found from databse")
            raise HTTPException("Some of the users are not found from databse")
       
        # Adding user to notes as collaborators.
        for user in user_data:
            note.collaborators[user['id']] = {"email" : user["email"], "access" : payload.access}
            logger.info(f"Adding collaborators to notes {note.collaborators}")
        flag_modified(note, "collaborators")    
    
        db.commit()
        db.refresh(note)
        logger.info("Chages are made and saved in database")

        JwtUtils.save(name=f"user_{user_id}", key=f"note_{note.id}", value=note.to_dict)
        logger.info(f"Collaborator {note.collaborators} added successfully to cache with note {note.id} for user {user_id}.")

        # Return the success message
        return{
            "Message" : "Collaborators added successfully.",
            "status" : "Success",
            "Data" : note.collaborators
        }
    
    except Exception as error:
        logger.error(f"Unable to add collaborators to note ID : {payload.note_id} for user ID : {user_id} ")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to add collaborators : {error}")

# Remove collaboraotrs form notes. 
@app.patch('/notes/remove-collaborators')
def remove_collaborators(request: Request, payload: RemoveCollaborator, db: Session = Depends(get_db)):
    """
    Description:
    This function is used for removing collaborators from notes
    Parameters:
    request : The incoming request object.
    payload : A RemoveCollaborator schema add to access user ids.
    db : The database session dependency.
    Return:
    Return the success message with collaborator remove from notes
    """
    try:
        # Fetching user id from request.state
        user_id = request.state.user["id"]

        # Fetching the note for the particular user based on note id provided by the user
        note = db.query(Notes).filter(Notes.id == payload.note_id, Notes.user_id == user_id).first()
        logger.info(f"Fetching note based on Note ID: {payload.note_id} and User ID: {user_id}")

        # If note is not found
        if not note:
            logger.info(f"Note not found for Note ID: {payload.note_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Note not found in database for User ID: {user_id} with Note ID: {payload.note_id}")

        # Checking if collaborators exist in the note
        if not note.collaborators:
            logger.info(f"No collaborators found for Note ID: {payload.note_id}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No collaborators found to remove.")


        # Removing specified users from collaborators
        for remove_user_id in payload.user_ids:
            if str(remove_user_id) in note.collaborators:
                note.collaborators.pop(str(remove_user_id))  # Remove user from collaborators
                logger.info(f"Removed user with ID {remove_user_id} from collaborators")
            
            if str(remove_user_id) not in note.collaborators:
                logger.info(f"User with ID {remove_user_id} is not a collaborator")
                raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED, detail=f"User with ID {remove_user_id} is not a collaborator")

        # Flagging collaborators field as modified
        flag_modified(note, "collaborators")

        # Commit the changes to the database
        db.commit()
        db.refresh(note)
        logger.info("Changes saved in the database")

        # Cache Invalidation or Update
        cached_notes = JwtUtils.get(name = f"user_{user_id}")
        
        # Deleting collaborators form note in cache
        if cached_notes:
            for cached_note in cached_notes:
                if cached_note["id"] == payload.note_id:
                    cached_note["collaborators"] = note.collaborators  # Update collaborators in cache
            JwtUtils.save(name = f"user_{user_id}", key=f"note_{payload.note_id}", value=cached_note)
            logger.info(f"Updated cache for user {user_id} after removing collaborators")
        else:
            logger.info(f"No cache found for user {user_id}")

        # Return success message
        return {
            "Message": "Collaborators removed successfully.",
            "status": "Success",
            "Data": note.collaborators
        }

    except Exception as error:
        logger.error(f"Unable to remove collaborators from Note ID: {payload.note_id} for User ID: {user_id} : {error}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unable to remove collaborators: {error}")

