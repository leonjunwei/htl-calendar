import os
import datetime
import pickle
import psycopg2
import urllib.parse

# import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


current_time = datetime.datetime.now()
display_month = current_time.month-1
display_year = current_time.year



urllibparse.uses_netloc.append("postgres")
url = urllib.parse.urlparse(os.environ["DATABASE_URL"])


def make_conn():
    conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port)
    return conn

def interact_with_database(message): #this is A VERY BAD IDEA if you don't want SQL injections
    conn = make_conn()
    with conn.cursor() as cur:
        cur.execute(message)
    conn.close()



# with open('calendar','wb') as file:
#     pickle.dump({},file)


# with open('calendar','rb') as file:
#     store = pickle.load(file)

# print(store)


@app.route('/health')
def health():
    return 'ok'


@app.route('/',methods = ["GET","POST"])
@app.route('/index.html',methods = ["GET","POST"])
def home_page():
    global display_month
    global display_year
    if request.method == "GET":
        display_month = current_time.month-1
        display_year = current_time.year
        return render_template('index.html', month=current_time.month-1, year = current_time.year)
    else:
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
        return render_template('index.html', month=display_month, year=display_year)


def add_to_dictionary(form):
    import random
    with open('calendar','rb') as file:
        store = pickle.load(file)
        uniqueID = random.random() #between 0 and 1
        while uniqueID in store:
            uniqueID = random.random()
        store[uniqueID] = form #store contains randomKey:eventDictionary pairs, eventDictionary is another dictionary with event details
    with open('calendar','wb') as file1:
        pickle.dump(store,file1)
    return uniqueID

def read_from_dictionary():
    with open('calendar','rb') as file:
        store = pickle.load(file)
    return str(store)

def wipe_everything():
    with open('calendar','wb') as file:
        pickle.dump({},file)



# @app.route('/event_page.html', methods = ["GET","POST"])
# def event_page():
#     if request.method == "GET":
#         print("poo")
#         return render_template('event_page.html')
#     if request.method == "POST":
#         print("event submitted")
#         print("Your unique ID for this event is: " + str(add_to_dictionary(request.form)))
#         return render_template('event_page.html')


@app.route('/event_submission.html',methods = ["GET","POST"]) #page where users can submit events
def event_submission():
    if request.method == "GET":
        return render_template('event_submission.html')
    else:
        return render_template('event_submitted.html', data = read_from_dictionary())


@app.route('/event_submitted.html',methods = ["GET","POST"]) #page afterward that shows submission status
def event_submitted():
    if request.method == "POST":
        try:
            message = "Your event has been successfully submitted! Your unique ID for this event is: " + str(add_to_dictionary(request.form))        
        except:
            message = "Something went wrong - sorry!"
        return render_template('event_submitted.html', data = message)
    elif request.method == "GET":
        message = "You really shouldn't have gotten here this way."
        return render_template('event_submitted.html', data = message)

@app.route('/wipe_everything.html',methods = ["GET","POST"])
def wipeEverything():
    if request.method == "POST":
        wipe_everything()
        message = "Wiped everything!"
        return render_template('event_submitted.html', data = message)
    elif request.method == "GET":
        message = "You really shouldn't have gotten here this way."
        return render_template('event_submitted.html', data = message)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000)) #not sure this will work
    app.run(host='0.0.0.0', debug=True, port=port)
    # app.run(host='127.0.0.1', debug=True, port=port)

