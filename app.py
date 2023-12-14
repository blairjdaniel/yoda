# app.py
from flask import Flask, request, render_template, session, url_for, redirect, flash
from api2 import ASSISTANT_ID, client, get_response, instruction, add_message_and_run, wait_on_run
from openai import OpenAI
import time
from file_handler import handle_upload
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import send_file
import codecs
from flask import jsonify
import fitz
from datetime import timedelta

app = Flask(__name__)

app.secret_key = 'blairjdaniel'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)  # Set session lifetime
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
ASSISTANT_ID = "asst_iI7puRBKhk6QyA8TJfOg9V5v"
client = OpenAI()


@app.route('/index')
def index():
    return render_template('index.html')
@app.route('/log')
def log():
    return render_template('log.html')
@app.route('/file')
def file():
    uploaded_files = session.get('uploaded_files', [])
    files_details = []

    for filename in uploaded_files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            file_details = {
                'filename': filename,
                'size': os.path.getsize(file_path),
                'creation_time': os.path.getctime(file_path),
                'modification_time': os.path.getmtime(file_path),
                'Uploaded': True,
            }
            files_details.append(file_details)
    
    return render_template('file.html', files=files_details)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    if filename in session.get('uploaded_files', []):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        flash('File not found')
        return redirect(url_for('file'))

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    uploaded_files = session.get('uploaded_files', [])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        uploaded_files = [f for f in uploaded_files if f != filename]
        session['uploaded_files'] = uploaded_files
        flash('File has been deleted successfully')
    else:
        flash('File not found')
    return redirect(url_for('file'))

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_text_file(filepath):
    with codecs.open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()
    
def process_file_with_assistant(filename, file_content):
    try:
        # Be sure to specify the correct assistant ID and settings for your particular assistant.
        response = openai.Completion.create(
            engine=ASSISTANT_ID,
            prompt=file_content,
            max_tokens=150,  # The number of tokens to generate (change as needed).
            temperature=0.7,  # The randomness of the response (change as needed).
            top_p=1,  # Controls diversity via nucleus sampling (change as needed).
            n=1,  # Number of completions to generate.
            stop=None,  # Sequence where the API will stop generating further tokens.
            frequency_penalty=0,  # Adjusts likelihood of new tokens based on their existing frequency in the text.
            presence_penalty=0  # Adjusts likelihood of new tokens based on whether they appear in the text so far.
        )
        # Extract the text of the first completion in the response
        assistant_response = response.choices[0].text.strip()
        return assistant_response
    except openai.error.OpenAIError as e:
        print(e)
        return "There was an error processing your request with the assistant."

    
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with fitz.open(pdf_path) as pdf:
    # Extract text from each page
        text = ""
        for page in pdf:
            text += page.get_text()
    return text
    
@app.route('/use_for_assistant/<filename>', methods=['POST'])
def use_file_for_assistant(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if os.path.exists(file_path):
        file_content = ""
        # Extract content based on the file type
        if filename.lower().endswith('.pdf'):
            file_content = extract_text_from_pdf(file_path)
        elif filename.lower().endswith(('.txt', 'md')):
            file_content = read_text_file(file_path)
        # Other file types handling can be added here

        # The extracted content can now be processed by the assistant
        assistant_response = process_file_with_assistant(filename, file_content)

        # Return the assistant's response as JSON for AJAX handling
        return jsonify({
            'filename': filename,
            'assistant_message': assistant_response
        })
    
    else:
        # If file doesn't exist, return error
        return jsonify({'error': 'File not found'}), 404
    
def process_message(user_input):
    thread_id = session.get('thread_id')
    if not thread_id:
        # Create a new thread if it doesn't exist
        thread = client.beta.threads.create()
        thread_id = thread.id
        session['thread_id'] = thread_id
    thread, run = add_message_and_run(thread_id, user_input)
    wait_on_run(run, thread_id)
    messages = get_response(thread_id)
    #  Extract the assistant's response from messages
    #assistant_response = " ".join([message.content[0].text.value for message in messages if message.role == 'assistant'])
    # Extract the last assistant's response from messages
    messages_list = list(messages)
    assistant_response = ''
    if messages_list:
        # Reverse iterate the messages list to find the last response from the assistant
        for message in reversed(messages_list):
            if message.role == 'assistant':
                assistant_response = message.content[0].text.value
                break
    return assistant_response
    

@app.route('/reset', methods=['POST'])
def reset():
    if 'reset' in request.form and request.form['reset'] == 'true':
        session.clear()  # Clear the session data
        thread = client.beta.threads.create()
        session['thread_id'] = thread.id
        return redirect(url_for('index'))  # Redirect to home after resetting

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'thread_messages' not in session:
        session['thread_messages'] = []  # Initialize thread_messages in session
    
    if request.method == 'POST':
        user_input = request.form.get('message', '').strip()
        if 'message' in request.form:
            # Handle user message
            user_input = request.form['message']
        if 'file' in request.files:
            # Handle file upload
            uploaded_files = session.get('uploaded_files', [])
            file = request.files.get('file')  # Safely get the file
        if file and allowed_file(file.filename):
            filename = handle_upload(file, app.config['UPLOAD_FOLDER'])
            if filename:
                session.modified = True
                if 'uploaded_files' not in session:
                    session['uploaded_files'] = []
                session['uploaded_files'].append(filename)
                flash('File successfully uploaded')
            else:
                flash('An error occurred while uploading the file')
        elif file:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')

        if user_input:
            app.logger.info('Question asked: %s', user_input)
            thread_id = session.get('thread_id')
            if not thread_id:
            # Create a new thread if it doesn't exist
                thread = client.beta.threads.create()
                thread_id = thread.id
                session['thread_id'] = thread_id
            thread, run = add_message_and_run(thread_id, user_input)
            #thread = thread_and_run[0]
            #run = thread_and_run[1]
            wait_on_run(run, thread_id)
            messages = get_response(thread_id)


        session['thread_messages'].append(f"User: {user_input}")
        assistant_response = process_message(user_input)
        session['thread_messages'].append(f"Assistant: {assistant_response}")
        session.modified = True
        #for message in messages:
                #response_content = message.content[0].text.value
                #if user_input not in response_content:  # To avoid echoing user input as part of the assistant's response
                    #session['thread_messages'].append(f"Assistant: {response_content}")
        #    compiled_response = " ".join([message.content[0].text.value for message in messages])
        #else:
        #    compiled_response = ""

            # Render the response in a template
    return render_template('index.html', thread_messages=session['thread_messages'], filenames=uploaded_files)

            #for message in messages:
            #    session['thread_messages'].append(message.content[0].text.value)  # Add each message to session
            #new_messages = [(message.content[0].text.value) for message in messages]
            #session['thread_messages'].extend(new_messages)  # Add new messages to session
            #messages_list = [message for message in messages]
            #answer = messages_list[-1].content[0].text.value
            #return render_template('index.html', answer=answer, filenames=uploaded_files)
    #return render_template('index.html', thread_messages=session['thread_messages'], filenames=uploaded_files)

    
if __name__ == '__main__':
    app.run(port=5000)
