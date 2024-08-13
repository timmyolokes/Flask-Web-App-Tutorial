from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from google.cloud import storage


views = Blueprint('views', __name__)


# Initialize Google Cloud Storage client
storage_client = storage.Client()

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            # Upload note content to Cloud Storage
            upload_note_to_storage(note)

            # Add note to the database
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)

def upload_note_to_storage(note_content):
    # Define the name of the bucket and the filename to store the note
    bucket_name = 'ece-428-mynotes'
    filename = 'note.txt'  # You can use any filename you prefer

    # Get the bucket and blob object
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)

    # Upload the note content to Cloud Storage
    blob.upload_from_string(note_content)

""" @views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user) """


@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})
