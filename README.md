# batch-api-retrieval
This is a web page which takes in a CSV file of a collection of music, and cross references each entry in the CSV file against the Discogs and Musicbrainz Databases to provide collectors/archivists with more information about materials in their collection.

## the page

The web page is built on the Flask framework and uses both Discogs and Musicbrainz APIs to access their databases, using User Tokens for the [Computational Rarity Team](https://github.com/computational-rarity-team).

The tutorial at [https://thinkinfi.com/flask-upload-display-file/](https://thinkinfi.com/flask-upload-display-file/) was used to figure out the uploading CSV file functionality.

## the input

To use the batch retrieval tool, create a CSV with the minimum required fields and upload to the site, which will then attempt to fill as many of the fields as possible with the information from Discogs and Musicbrainz.

## the output

The output can be downloaded as a CSV or viewed on the page.

##