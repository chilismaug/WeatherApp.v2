#!/usr/bin/env python
from pprint import pprint as pp
from flask import Flask, flash, redirect, render_template, request, url_for
from weather import query_api
import json
import os
import logging

app = Flask(__name__)

@app.route('/')
def index():
    filename = 'cities.json'

#    jsonFile = os.path.join( "static", "data", filename)
    jsonFile = os.path.join(os.path.split(__file__)[0], 'data/cities.json')

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
