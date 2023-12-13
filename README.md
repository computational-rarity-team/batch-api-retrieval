# batch-api-retrieval
This is a web page which takes in a CSV file of a collection of music, and cross references each entry in the CSV file against the Discogs and Musicbrainz Databases to provide collectors/archivists with more information about materials in their collection.

## the page

The web page is built on the Flask framework and uses both Discogs and Musicbrainz APIs to access their databases, using User Tokens for the [Computational Rarity Team](https://github.com/computational-rarity-team).

The tutorial at [https://thinkinfi.com/flask-upload-display-file/](https://thinkinfi.com/flask-upload-display-file/) was used to figure out the uploading CSV file functionality.

## the input

To use the batch retrieval tool, create a CSV with the minimum required fields and upload to the site, which will then attempt to fill as many of the fields as possible with the information from Discogs and Musicbrainz.

## the output

The output can be downloaded as a CSV or viewed on the page.

# current ISSUES 🥅 🐐

- Discogs API a bit confusing
- Musicbrainz even more so
- how to show each release in a batch as a dynamic page
  - figure out system for users to confirm matches
  - figure out system for users to perform searches

## appendix

### Musicbrainz API with musicbrainzngs

More info at: 
[https://python-musicbrainzngs.readthedocs.io/en/latest/api/](https://python-musicbrainzngs.readthedocs.io/en/latest/api/)

For this application, since we are trying to get as many releases as possible but not things that are "like" the pertinent release in the collection, we must be very specific with our query.

Below are some very helpful search functions in `musicbrainzngs` which we can use in Python to query the Musicbrainz database.

`musicbrainzngs.search_recordings(query='', limit=None, offset=None, strict=False, **fields)`
*Search for recordings and return a dict with a ‘recording-list’ key.*

>Available search fields: alias, arid, artist, artistname, comment, country, creditname, date, dur, format, isrc, number, position, primarytype, qdur, recording, recordingaccent, reid, release, rgid, rid, secondarytype, status, tag, tid, tnum, tracks, tracksrelease, type, video

`musicbrainzngs.search_release_groups(query='', limit=None, offset=None, strict=False, **fields)`
*Search for release groups and return a dict with a ‘release-group-list’ key.*

>Available search fields: alias, arid, artist, artistname, comment, creditname, primarytype, reid, release, releasegroup, releasegroupaccent, releases, rgid, secondarytype, status, tag, type

`musicbrainzngs.search_releases(query='', limit=None, offset=None, strict=False, **fields)`
*Search for recordings and return a dict with a ‘release-list’ key.*

>Available search fields: alias, arid, artist, artistname, asin, barcode, catno, comment, country, creditname, date, discids, discidsmedium, format, label, laid, lang, mediums, primarytype, quality, reid, release, releaseaccent, rgid, script, secondarytype, status, tag, tracks, tracksmedium, type

After some experimentation, it seems that `search_release_groups` is the best function for our purposes here.

Since we do not have much control over what CSVs come in, we should try our best to match each column of the given CSV with the available fields for `search_release_groups`.

You can use `search_release_groups` without specifying the parameters, by just submitting a query: `musicbrainzngs.search_release_group('"robert ashley" AND "yellow man with heart with wings"')`.

So for example, we could search based on just the artist and title, and then search everything else as optional, or search specific terms first, then if there are no results, search without double quotes/exact modifiers.

More in-depth information about Queries is available on the [package description website about Lucene Search Syntax](https://lucene.apache.org/core/7_7_2/queryparser/org/apache/lucene/queryparser/classic/package-summary.html#package.description).

### Discogs API

More info at: [https://python3-discogs-client.readthedocs.io/en/latest/fetching_data.html](https://python3-discogs-client.readthedocs.io/en/latest/fetching_data.html)

We can use the `search` function like so:
`d.search(release_title, type='release')`

This returns a `release` object, which has the following parameters:
- artists
- formats
- genres
- images
- tracklist
- title

As an example, to print the primary image associated with a release, one would:

`results = d.search(ex_title, type='release')`
`print(d.results.images[0])`
