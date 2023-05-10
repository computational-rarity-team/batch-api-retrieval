# flask imports
from flask import Flask, render_template, request, session
# misc system imports
import os
import urllib3
# music DB API imports
import musicbrainzngs
import discogs_client
# CSV imports
import pandas as pd
from werkzeug.utils import secure_filename
# dotenv import
from dotenv import load_dotenv

# FLASK CONFIG
app = Flask(__name__)

# Define folder to save uploaded files to process further
UPLOAD_FOLDER = os.path.join('static', 'uploads')
 
# Define allowed files (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__, template_folder='templates', static_folder='static')
# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define secret key to enable session
load_dotenv()

app.secret_key = os.environ.get("USER_TOKEN")

# musicbrainz User Agent Setup
musicbrainzngs.set_useragent(
    "batch-api-retrieval",
    "0.1",
    "https://github.com/computational-rarity-team/batch-api-retrieval/",
)
d = discogs_client.Client('ExampleApplication/0.1', user_token=app.secret_key)


@app.route('/')
def index():
    return render_template('index.html')

 
@app.route('/',  methods=("POST", "GET"))
def upload_file():
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
def show_data():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
 
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)
 
    # pandas dataframe to html table flask
    uploaded_df_html = uploaded_df.to_html()
    return render_template('show_data.html', data_var = uploaded_df_html)


@app.route('/check_fields')
def check_fields():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
 
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # first check fields of CSV with search params of MB and Discogs
    # !!!! for this version let's just do artist and title/release
    return render_template('check_fields.html', column_values = uploaded_df.columns)


# then use verified field values to search for each entry in MB and Discogs

@app.route('/show_entries')
def show_entries():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)

    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # return the entries found
    # !!!! for this version we'll just return the first entry
    mbresults = [musicbrainzngs.search_release_groups('\'"'+row[1]+'" AND "'+row[2]+'"\'') for row in uploaded_df.values]
    dcresults = [d.search(row[2], type='release') for row in uploaded_df.values]

    # grab just the first entry of each row
    mbresult = [row['release-group-list'][0]['id'] if len(row['release-group-list']) > 0 else 'not found' for row in mbresults]
    dcresult = [row[0].id for row in dcresults]

    # each entry should be formatted clearly and have a link
    # to its entry on MB and Discogs respectively
    # !!!! for this version let's start with just a link

    # the results should also be available as a downloadable CSV
    # !!!! for this version let's get this going only if it feels necessary

    results_list = (mbresult, dcresult)

    return render_template('show_entries.html', results = results_list)


@app.route('/find_matches')
def find_matches():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
 
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # get the results
    # note: here we're using double quotes to get an EXACT match of what entered, we'll have to add some fuzziness
    # this will also return several (looks like default 25) results according to how they match
    # perhaps we should give the user the option to browse each result as it comes in!
    # also depending on the columns included in the csv, we should search for each one
    mbresults = [musicbrainzngs.search_release_groups('\'"'+row[1]+'" AND "'+row[2]+'"\'') for row in uploaded_df.values]
    # for now let's just search using the title
    dcresults = [d.search(row[2], type='release') for row in uploaded_df.values]

    the_results = (mbresults, dcresults)

    return render_template('find_matches.html', data_var = the_results)


if __name__ == '__main__':
    app.run(debug=True)
    