import os
import datetime
import pickle
import urllib.parse
from flask import Flask, redirect, render_template, request, url_for
import psycopg2


## Useful Resources ##

## https://devcenter.heroku.com/articles/heroku-postgresql
## ^ How to get postgres working for the heroku app

## http://initd.org/psycopg/docs/usage.html
## ^ How to use psycopg2 to connect to/access/edit a postgres database.


## Init ##

app = Flask(__name__)

current_time = datetime.datetime.now()
display_month = current_time.month-1
display_year = current_time.year


## Database access/edit ##

urllib.parse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])


def generate_random_key(): #change this to gfycat-style 3-word concatenation when it actually becomes necessary
    from random import random
    return random()


def make_conn():
    global url
    conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port)
    return conn


def interact_with_database(instruction, debug=False):
    """
    debug = True: returns a string that tells you what you just did.
    debug = False: returns only cursor contents.
    """
    store = None
    conn = make_conn()
    with conn.cursor() as cur:
        # try:
        cur.execute(instruction)
        store = [row for row in cur]
        # except:
            # pass
    conn.commit()
    conn.close()
    if debug:
        if store:
            return "Your instruction was " + str(instruction) + " . Cursor output (if any) is: " + str(store)
        else:
            return "Your instruction was " + str(instruction) + " . No cursor output."
    else:
        return store


def add_event_into_database(data):
    """
    data must be a tuple, and its format must follow the table's format.
    data[0] should be the data that needs to be in the leftmost column of table, data[1] should be the next one and so on.
    """
    flag = None
    instruction = "insert into events values (%s, %s, %s, %s, %s, %s, %s, %s)"
    values = data
    conn = make_conn()
    with conn.cursor() as cur:
        try:
            cur.execute(instruction, values)
            flag = 1
        except:
            flag = cur.mogrify(instruction, values)
    conn.commit()
    conn.close()
    return flag #flag tells us if the query succeeded.


def add_form_to_database(form):
    """
    Form is an ImmutableMultiDict with keys: 
        event_name, event_taglist, startDate, startTime, endDate, endTime, event_location, event_summary and event_link
    Our current table is set up such that the columns from left to right are as follows:
        event_ID, event_name, event_taglist, event_start, event_end, event_location, event_summary, event_link
    """
    import random
    event_ID = random.random()
    data = (str(event_ID),form['event_name'],form['event_taglist'],str(form['startDate']+" "+form['startTime']), str(form['endDate']+" "+form['endTime']),form['event_location'],form['event_summary'], form['event_link'],)
    flag = add_event_into_database(data)
    if flag == 1:
        return str(event_ID)
    else:
        return flag


## Site Map ##


@app.route('/',methods = ["GET","POST"])
@app.route('/index',methods = ["GET","POST"])
@app.route('/index.html',methods = ["GET","POST"])
def index():
    global display_month
    global display_year
    if request.method == "GET":
        display_month = current_time.month-1
        display_year = current_time.year
        return render_template('index.html', month=current_time.month-1, year = current_time.year)
    else:
        if 'direction' in request.form:
            if request.form['direction']=='forward':
                display_month += 1
                if display_month > 11:
                    display_year += 1
                    display_month = 0
            elif request.form['direction']=='backward':
                display_month -= 1
                if display_month < 0:
                    display_year -= 1
                    display_month = 11
        else:
            date = request.form['date']
            date_split = date.split('/')
            display_month = str(int(date_split[0])-1)
            display_year = date_split[1]
        return render_template('index.html', month=display_month, year=display_year)


@app.route('/test',methods = ["GET","POST"])
@app.route('/test.html',methods = ["GET","POST"])
def test():
    if request.method == "GET":
        message = "Type something here."
        return render_template('test.html', data = message)
    else:
        if request.form:
            instruction = request.form['request']
            return render_template('test.html', data = interact_with_database(instruction, debug = True))
        else:
            message = "Something went horribly wrong."
            return render_template('test.html', data = message)


@app.route('/event_search', methods = ["GET","POST"])
@app.route('/event_search.html', methods = ["GET","POST"])
def event_search():
    return render_template('event_search.html')


@app.route('/event_submission',methods = ["GET","POST"])
@app.route('/event_submission.html',methods = ["GET","POST"]) #page where users can submit events
def event_submission():
    if request.method == "GET":
        return render_template('event_submission.html')
    else:
        return render_template('event_submitted.html', data = interact_with_database("select * from events", debug = False))


@app.route('/event_submitted',methods = ["GET","POST"])
@app.route('/event_submitted.html',methods = ["GET","POST"]) #page afterward that shows submission status
def event_submitted():
    if request.method == "POST":
        # try:
        message = "Request form = " + str(request.form) + " and unique ID = " + add_form_to_database(request.form)  
        # except:
        #     if request.form:
        #         message = "Something went wrong - sorry! Request form = " + str(request.form)
        #     else:
        #         message = "Something went wrong - sorry!"
        return render_template('event_submitted.html', data = message)
    elif request.method == "GET":
        message = "You really shouldn't have gotten here this way."
        return render_template('event_submitted.html', data = message)


@app.route('/agenda_view',methods = ["GET","POST"]) 
@app.route('/agenda_view.html',methods = ["GET","POST"])
def agenda_view():
    events = None
    testData = None
    if request.method == "POST":
        events = interact_with_database('select * from events where event_start between \"%s-%s-%s\" and \"%s-%s-%s\"' 
                                        %(str(display_year), str(display_month+1), str(request.form["day"]),
                                        str(display_year), str(display_month+1), str(int(request.form["day"])+1)), debug = False)
        # testData = [('1','name','tag1 tag2','2000-01-01 12:00','2000-01-01 14:00','location','summary','link'),('2','name2','tag3 tag4','2010-01-01 12:00','2010-01-01 14:00','location2','summary2','link2')]
    else:
        events = interact_with_database('select * from events where YEAR(event_start) = %s and MONTH(event_start) = %s"'
                                        %(str(display_year), str(display_month+1)), debug = False)
    return render_template('agenda_view.html', data = events) 
    #data is a list of event tuples. An event tuple is (event_ID, event_name, event_taglist, event_start, event_end, event_location, event_summary, event_link)



## Run ##

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) #not sure this will work
    app.run(host='0.0.0.0', debug=True, port=port)
    # app.run(host='127.0.0.1', debug=True, port=port)


## Past Planning ##

# Get an agenda page running

# Get each number on a calendar to go to an agenda page for that date
"""
Pull out the day/month/year and query the database for events on that day, then display an agenda page with that info?
"""

# Figure out how the columns of the database should be laid out
"""
1) Unique Event ID (string - maybe allow users to override? What if there's an event by a different user with the same password they want?)
2) Event Name
3) Event Taglist (string like "coding from_website limited_number"? A list of all tags ranked by frequency should be accessible somewhere.)
4) Event start datetime (Allowing users to select date/time of start and date/time of end independently will be good)
5) Event end datetime   (If they don't put an end date we assume it's the same as the start date)
6) Event Location
7) Event Summary
8) Link/email to event (something people can click for even more details.)


CREATE TABLE events (event_ID varchar(255), event_name varchar(255), event_taglist varchar(511), 
                    event_start timestamp, event_end timestamp, event_location varchar(255), event_summary varchar(1023), event_link varchar(511))

should create an empty table for us.

"""

## To-Do ##

## Users may want to search by event name, event tag (submission, official, carpe might be some of the tags), location, 
## any combination of (starts earlier than, starts exactly at, starts later than) and (ends earlier than, ends exactly at, ends later than)
## unique event ID would be good too


## figure out if SQL has >= or whether > works


## python datetime objects can be stored in postgres via psycopg's cursor.execute(instruction,(data1,)). 
## Even if there's only one piece of data it still has to be in a tuple