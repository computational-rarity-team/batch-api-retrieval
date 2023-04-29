from flask import Flask, render_template, request, session

import os
import urllib3
import discogs_client
import pandas as pd
from werkzeug.utils import secure_filename

app = Flask(__name__)

#user_token = os.environ.get("USER_TOKEN")
#http = urllib3.PoolManager()
#r = http.request('GET', 'https://musicbrainz.org/ws/2/') # grab music information from musicbrainz


#d = discogs_client.Client('ExampleApplication/0.1', user_token=user_token)

# @app.route("/")
# def find_result():
#     results = d.search('SHAKER LOOPS', type='release')

#     for release in results:
#         return release.title

#*** Flask configuration

# Define folder to save uploaded files to process further
UPLOAD_FOLDER = os.path.join('static', 'uploads')
 
# Define allowed files (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, template_folder='templates', static_folder='static')
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define secret key to enable session
app.secret_key = 'This is your secret key to utilize session in Flask'
 
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/',  methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        # upload file flask
        uploaded_df = request.files['uploaded-file']
 
        # Extracting uploaded data file name
        data_filename = secure_filename(uploaded_df.filename)
 
        # flask upload file to database (defined uploaded folder in static path)
        uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
 
        # Storing uploaded file path in flask session
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
 
        return render_template('success.html')
 
@app.route('/show_data')
def showData():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
 
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)
 
    # pandas dataframe to html table flask
    uploaded_df_html = uploaded_df.to_html()
    return render_template('show_data.html', data_var = uploaded_df_html)
 
if __name__ == '__main__':
    app.run(debug=True)
    