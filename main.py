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

@app.route('/')
def index():
    filename = 'cities.json'

#    jsonFile = os.path.join( "static", "data", filename)
#    jsonFile = os.path.join(os.path.split(__file__)[0], 'data/cities.json')

    # create Goo Cloud Storage client to get that json from
    gcs = storage.client
    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(CLOUD_STORAGE_BUCKET)
    # the data file will be known as a blob to us henceforth
    blob = bucket.get_blob('json_data/data/cities.json')
    
    #    goo_cloud_dta_url = 'https://00e9e64bacfaa9cc0617d1a99652a0c37ad7874916782379f3-apidata.googleusercontent.com/download/storage/v1/b/weatherapiflask.appspot.com/o/jsondata%2Fdata%2Fcities.json?qk=AD5uMEvaEIv5MYeC8_uqRLsL9fcjsDsKxIWd_4wkv60NOa1m76ZfK7j3d-h48iUdt7KqSmoMs7pHLwdW0D1_ot60se5bXHssZV44pNlblbXcII6zhapVCN0FEOoMtWhNS97SjmdklBya7DSEToHyL0yiJDjVM7k_q3tdMKjVwZStCLYYhRyxDKMKXu8ovykN6R5iwrtU4h3RcSjrGUThMh0DRkl13fxjDcz4PnTaGXpsJGdIpFDkscAC2icAoowy41abXeAOlwBojjOhYasR2hm7Lun8Ih0v5beo5USJdoxL3Hrpo45al8AOfZVbHjO1s5kiLJftqCLeU8iqerZu9nzj5P0BQs5ZjklXSB83z_5RD7va3btw8kOns3TMGdrsSvKFAsNlMSSg921jTNUlgCtA4o46hK1J9YCOxH0eO9-3uIDTq-ROxB9ySHOS1-tsE86iG2kzeAecaPJrtxumlU21c_B7SVfwFsbI2UaF227sz-Qyj7_QSthHMHDRkwx4l_E5lFFwR7IKlgfiUnm7A5KSpdVzsgLovYnBhCP4Yl1nzVIvzGgrzK3CNLCq-2r4oOIYzKwfCJR9SC8b9oKEthOUNd1ilIHc_fPRzSnVbiWItyiATXZTH8xjhrX776s44BUgE59YoucJdnS8CUlGb_zlAOBf7_LV2QWDAzfaZpqM77gBHw3DDtmm8-8OoawabhyeuVDNKxkGNmW_h_AS9gOmSCphOwaXOCsSdiTJYMMVhHov0dr8vLHtZ0iYxdEaL5GiUDGEJ-jl5UFJjAIETQR3z9cx52ToKArWE0iIA1j1kVq0X_c4PGs'
    jsonFile =  blob  # feb 19, 2019 : amazed if this works, just sayin'
    

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
        with open(jsonFile) as f:
          file_data = json.load(f)
    except:
        file_data = [{"name":"json file read failed"}]

    if len(file_data) > 1:
        data = file_data
    else:
        data = here_data

    return render_template(
        'weather.html',
        data=data,
        phase='ask',
        jsinfo=jsonFile)


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

if __name__=='__main__':
    app.run(debug=True)
