# flask imports
from flask import Flask, render_template, request, session
# misc system imports
import os
import requests
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

app.secret_key = os.environ.get("CONSUME_SECRET")

# musicbrainz User Agent Setup
musicbrainzngs.set_useragent(
    "batch-api-retrieval",
    "0.1",
    "https://github.com/computational-rarity-team/batch-api-retrieval/",
)
d = discogs_client.Client('computational-rarity-test/1.0', user_token=os.environ.get("USER_TOKEN"))
#d = discogs_client.Client(
#    'computational-rarity-batch/1.0',
#    consumer_key=os.environ.get("CONSUME_KEY"),
#    consumer_secret=os.environ.get("CONSUME_SECRET")
#)

the_frame = pd.DataFrame()

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

# then use verified field values to search for each entry on Discogs
@app.route('/get_options')
def get_options():
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
 
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # load the pre-formatted field names for the headers
    the_fields = ["catno", "artist", "title", "label", "format", "year", "release_id"]

    # to populate the fields properly, we'll have to combine the artist fields, stripping any spaces
    # first make a new array to fill with the new artist values
    combined_artists = []
    # then fill that array with the new artist values
    for entry,row in uploaded_df.iterrows():
        #print(str(row['artist_first']),file=sys.stderr)
        #print(str(row['artist_last']),file=sys.stderr)
        if isinstance(row['artist_first'], str) and isinstance(row['artist_last'], str):
            combined_artists.append(row['artist_first']+' '+row['artist_last'])
        else:
            if row['artist_first'] and not row['artist_last']:
                combined_artists.append(row['artist_first'])
            elif not row['artist_first'] and row['artist_last']:
                combined_artists.append(row['artist_last'])
            else:
                combined_artists.append('')
            
    # then create a new dataframe with the combined artist array as a column replacing the other two
    new_dict = dict(zip([None]*len(the_fields), the_fields))
    # create a dictionary
    field_list = [[row[field] if field != 'artist' else combined_artists[num] for field in the_fields] for num,row in uploaded_df.iterrows()]
    #print(field_list)
    field_list = pd.DataFrame(field_list).T.values.tolist()
    #[[dist_fields[num].append(field) for num,field in entry] for entry in field_list]
    #[[print(field) for field in entry] for entry in field_list]
    new_dict = dict(zip(the_fields, field_list))

    #print(new_dict)

    # create new data frames from dictionary
    new_df = pd.DataFrame(data=new_dict)
    global the_frame
    the_frame = new_df.copy()

    #print(new_df)

    #search each entry on discogs, show results, let user select most accurate one
    the_results = []
    the_entries = []
    the_titles = []
    the_artists = []
    the_years = []
    the_images = []
    # even though we don't use it, the "num" in the for call below is necessary!!!!
    for num,entry in the_frame.iterrows():
        d_query = ""
        for field in the_fields:
            if isinstance(entry[field], str):
                d_query += field+"="+entry[field]+","
        this_entry = entry['title']+" - "+entry['artist']
        the_results = ['test'] * 25
        this_result = d.search(d_query,type="release")
        
        if (len(this_result) > 0 and len(this_result) < 25):
            for item in this_result:
                the_titles.append(item.title)
                the_artists.append(item.artists[0].name)
                the_years.append(item.year)
                if item.images is not None: the_images.append(item.images[0]['resource_url'])
                the_results.append(item.id)
        elif (len(this_result) >= 25):
            count = 0
            for item in this_result:
                the_results.append(item.id)
                the_titles.append(item.title)
                the_artists.append(item.artists[0].name)
                the_years.append(item.year)
                if item.images is not None: the_images.append(item.images[0]['resource_url'])
                count += 1
                if count > 24: break
        else:
            the_results.append(str(num))
        the_entries.append(this_entry)
    #print(the_results)
    return render_template('get_options.html', results = the_results, entries = the_entries, titles = the_titles, artists = the_artists, years = the_years, images = the_images)

@app.route('/custom_search', methods=['POST'])
def custom_search():
    if request.method == 'POST':
        print(request.arts.get())

@app.route('/search_further', methods=['GET'])
def search_further():
    if request.method == 'GET':
        global the_frame

        num = request.args.get("num")

        # load the pre-formatted field names for the headers
        the_fields = ["catno", "artist", "title", "label", "format", "year", "release_id"]

        entry = the_frame.iloc[int(num), :]
        print(entry)
        this_entry = entry['title']+" - "+entry['artist']
        print(entry['title'])
        
        d_query = ""
        the_titles = []
        the_artists = []
        the_years = []
        the_images = []
        ind_ids = []
        ind_results = []
        for field in the_fields:
            if isinstance(entry[field], str):
                if field == 'title':
                    #print(entry['title'])
                    result = d.search(entry['title'],type="release")
                    #print(len(result))
                    if len(result) > 0:  
                        if len(result) < 2:
                            ind_results.append(result)
                            the_titles.append(result.title)
                            the_artists.append(result.artists[0].name)
                            the_years.append(result.year)
                            the_images.append(result.images[0]['resource_url'])
                        else:
                            for item in result:
                                ind_results.append(item)
                                the_titles.append(item.title)
                                the_artists.append(item.artists[0].name)
                                the_years.append(item.year)
                                if item.images is not None: the_images.append(item.images[0]['resource_url'])
                    print(ind_results)
        if len(ind_results) > 0:
            ind_ids = [result.id for result in ind_results]
    return render_template('search_further.html', results = ind_ids, entry = this_entry, titles = the_titles, artists = the_artists, years = the_years, images = the_images)

# then use verified field values to search for each entry in MB and Discogs
@app.route('/show_entries')
def show_entries():
    mb_fields = ["alias", "arid", "artist", "artistname", "comment", "creditname", "primarytype", "reid", "release", "releasegroup", "releasegroupaccent", "releases", "rgid", "secondarytype", "status", "tag", "type"]
    dc_fields = ["type","title","release_title","credit","artist","anv","label","genre","style","country","year","format","catno","barcode","track","submitter","contributor"]

    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)

    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    uploaded_df = pd.read_csv(data_file_path)

    # declare empty arrays, non-pythonic, i know
    mb_results = []
    dc_results = []

    if request.method == 'POST':
        # get user input using request
        mb_matches = request.form['mb_matches']
        dc_matches = request.form['dc_matches']
        # get each user field matched
        new_fields = [request.form[field] for field in request.form['non_matches'] if field != "no_match"]

        for entry in uploaded_df:
            # make new arrays with "correct" columns for mb and dc
            mb_terms = dict(zip(mb_fields, [None]*len(mb_fields)))
            dc_terms = dict(zip(dc_fields, [None]*len(dc_fields)))

            # populate arrays with the given values
            for field in mb_matches:
                mb_terms[field] = entry[field]
            for field in dc_matches:
                dc_terms[field] = entry[field]
            for field in new_fields:
                field_vals = field.split(',')
                if (field_vals[1] == 'mb'):
                    mb_terms[field_vals[0]] = entry[field_vals[2]]
                else:
                    dc_terms[field_vals[0]] = entry[field_vals[2]]

            # create new data frames from dictionaries
            mb_query = pd.DataFrame(data=mb_terms)
            dc_query = pd.DataFrame(data=dc_terms)

            # search by each entry
            #mb_results.append(musicbrainzngs.search_release_groups(alias=mb_query['alias'], arid=mb_query['arid'], artist=mb_query['artist'], artistname=mb_query['artistname'], comment=mb_query['comment'], creditname=mb_query['creditname'], primarytype=mb_query['primarytype'], reid=mb_query['reid'], release=mb_query['release'], releasegroup=mb_query['releasegroup'], releasegroupaccent=mb_query['releasegroupaccent'], releases=mb_query['releases'], rgid=mb_query['rgid'], secondarytype=mb_query['secondarytype'], status=mb_query['status'], tag=mb_query['tag'], type=mb_query['type']))
            #dc_results.append(d.search(type=dc_query['type'],title=dc_query['title'],release_title=dc_query['release_title'],credit=dc_query['credit'],artist=dc_query['artist'],anv=dc_query['anv'],label=dc_query['label'],genre=dc_query['genre'],style=dc_query['style'],country=dc_query['country'],year=dc_query['year'],format=dc_query['format'],catno=dc_query['catno'],barcode=dc_query['barcode'],track=dc_query['track'],submitter=dc_query['submitter'],contributer=dc_query['contributor']))
            
        # grab just the first entry of each row
        #mb_result = [row['release-group-list'][0]['id'] if len(row['release-group-list']) > 0 else 'not found' for row in mb_results]
        #dc_result = [row[0].id for row in dc_results]

    # the results should also be available as a downloadable CSV
    # !!!! for this version let's get this going only if it feels necessary

    #results_list = (mb_result, dc_result)
    results_list = (mb_query, dc_query)

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
    #mbresults = [musicbrainzngs.search_release_groups(artist=artistValue, )]
    # for now let's just search using the title
    dcresults = [d.search(row[2], type='release') for row in uploaded_df.values]

    # let's get results based on the fields we checked
    # first build the query as a string
    #dcquery = []
    #dcresults = [d.search(dcquery) for row in uploaded_df.values]

    the_results = (mbresults, dcresults)

    return render_template('find_matches.html', data_var = the_results)


if __name__ == '__main__':
    app.run(debug=True)
    





def cache_code():
    import feedparser
    import requests
    import ssl
    import time

    from functools import lru_cache, wraps
    from datetime import datetime, timedelta

    if hasattr(ssl, "_create_unverified_context"):
        ssl._create_default_https_context = ssl._create_unverified_context

    def timed_lru_cache(seconds: int, maxsize: int = 128):
        def wrapper_cache(func):
            func = lru_cache(maxsize=maxsize)(func)
            func.lifetime = timedelta(seconds=seconds)
            func.expiration = datetime.utcnow() + func.lifetime

            @wraps(func)
            def wrapped_func(*args, **kwargs):
                if datetime.utcnow() >= func.expiration:
                    func.cache_clear()
                    func.expiration = datetime.utcnow() + func.lifetime

                return func(*args, **kwargs)

            return wrapped_func

        return wrapper_cache

    @timed_lru_cache(10)
    def get_article_from_server(url):
        print("Fetching article from server...")
        response = requests.get(url)
        return response.text

    def monitor(url):
        maxlen = 45
        while True:
            print("\nChecking feed...")
            feed = feedparser.parse(url)

            for entry in feed.entries[:5]:
                if "python" in entry.title.lower():
                    truncated_title = (
                        entry.title[:maxlen] + "..."
                        if len(entry.title) > maxlen
                        else entry.title
                    )
                    print(
                        "Match found:",
                        truncated_title,
                        len(get_article_from_server(entry.link)),
                    )

            time.sleep(5)

    monitor("https://realpython.com/atom.xml")