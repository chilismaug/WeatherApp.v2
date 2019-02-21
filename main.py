#!/usr/bin/env python
import json
import os
import logging
from pprint import pprint as pp
from flask import Flask, flash, redirect, render_template, request, url_for
from weather import query_api
from google.cloud import storage

app = Flask(__name__)

# Configure this environment variable via app.yaml
CLOUD_STORAGE_BUCKET = os.environ['CLOUD_STORAGE_BUCKET']
CLOUD_STORAGE_FOLDER = "data"

@app.route('/')
def index():
    file_name = "cities.json"

#    jsonFile = os.path.join( "static", "data", filename)
#    jsonFile = os.path.join(os.path.split(__file__)[0], 'data/cities.json')

    # create Goo Cloud Storage client to get that json from
    gcs = storage.Client()
    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)

    list_blobs(CLOUD_STORAGE_BUCKET)

    # the data file will be known as a blob to us henceforth
    myblob = bucket.get_blob(CLOUD_STORAGE_FOLDER + "/"+ file_name)

    print("we have blob!")
    print(myblob.name)
    b = myblob.download_as_string()
    print("what's in b, a blob?")
    print(b)


    here_data = [{'name':'Canberra'},
               {'name':'Kathmandu'},
               {'name':'Kyoto'},
               {'name':'Montreal'},
               {'name':'Quebec'},
               {'name':'Reykjavik'},
               {'name':'Timbuktu'},
               {'name':'Toronto'},
               {'name':'Vancouver'}]

    try:
        print("gonna try to download blob into b, load as json...")
        file_data = json.loads(b)
    except:
        file_data = [{"name":"json file read failed"}]

    print(file_data)

    if len(file_data) > 1:
        data = file_data
    else:
        data = here_data

    return render_template(
        'weather.html',
        data=data,
        phase='ask',
        jsinfo=file_data)


@app.route("/result", methods=["GET", "POST"])
def result():
    data = []
    error = None
    select = request.form.get('comp_select')
    resp = query_api(select)
    pp(resp)
    if resp:
       data.append(resp)
    if len(data) != 2:
        error = 'Bad Response from Weather API'
    return render_template(
        'result.html',
        data=data,
        error=error,
        phase='answer')


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


def list_blobs(bucket_name):
    """Lists all the blobs in the bucket."""
    print("listing bucket blobs")
    gcs = storage.Client()
    bucket = gcs.get_bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        print(blob.name)

def _read_file(blob, format):
        """Reads a non-notebook file.

        blob: instance of :class:`google.cloud.storage.Blob`.
        format:
          If "text", the contents will be decoded as UTF-8.
          If "base64", the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        bcontent = blob.download_as_string()

        if format is None or format == "text":
            # Try to interpret as unicode if format is unknown or if unicode
            # was explicitly requested.
            try:
                return bcontent.decode("utf8"), "text"
            except UnicodeError:
                if format == "text":
                    raise web.HTTPError(
                        400, "%s is not UTF-8 encoded" %
                             blob.file_name,
                        reason="bad format",
                    )
        return base64.encodebytes(bcontent).decode("ascii"), "base64"


if __name__=='__main__':
    app.run(debug=True)
