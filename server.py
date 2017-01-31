import os
import time
import datetime
import pickle


# import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


current_time = datetime.datetime.now()
display_month = current_time.month-1
display_year = current_time.year


# with open('calendar','wb') as file:
#     pickle.dump({},file)


with open('calendar','rb') as file:
    store = pickle.load(file)

print(store)


@app.route('/health')
def health():
    return 'ok'

@app.route('/',methods = ["GET","POST"])
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
        for key in form:
            uniqueID = random.random() #between 0 and 1
            store[uniqueID] = form[key]
    with open('calendar','wb') as file1:
        pickle.dump(store,file1)
    return uniqueID


@app.route('/event_page.html',methods = ["GET","POST"])
def event_page():
    if request.method == "GET":
        print("poo")
        return render_template('event_page.html')
    if request.method == "POST":
        print("event submitted")
        print("Your unique ID for this event is: " + str(add_to_dictionary(request.form)))
        return render_template('event_page.html')



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=True, port=port)

# print current_time.year