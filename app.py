#!/usr/bin/env python

import pickle
# import mysql.connector
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
# import flask_login


#Leon Lam, 11 Jul 2016
#To-do: Implement flask-login (plus different access levels?), populate database with experiment/timestamp data, implement form input -> SQL query parsing

#We might not actually need socket.io, unless we want real-time tracking of experiment duration/steps without user input.

#Do we want an additional line for direct SQL queries? If so, implement safeguards against SQL injection

###################
#      Init       #
###################

#I have very little idea what this actually does. We want to set async_mode to 'eventlet' if possible, apparently. Some sort of event handler?


async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary if this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

app = Flask(__name__, template_folder='Templates')
app.config['SECRET_KEY'] = 'fookin \'ell, m8, i\'ll correspondence yer \'ead in, swear on me mum'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while 1==2:
        time.sleep(10)
        count += 1
        print count
        socketio.emit('my response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')



###################
#      Login      #
###################

#this is ok for a single user on the app - if there's multiple users we want to make sure some can be logged on as admin while the rest aren't.
#can we use flask-login?

global administrator
administrator = False


def login_success(user,pw): #user puts in their username and password here
    login_data = pickle.load(open('pw.txt','r')) #login data is a dictionary with username:(password, name)
    try:
        if login_data[user][0] == pw:
            return True
        else:
            return False
    except:
        return False


###################
#    Sitemap      #
###################
"""
A basic site for now. Login, search/add experiments, search/add/edit protocol.
"""

# pickle.dump(login_data,open('pw.txt','w'))

@app.route('/', methods = ['GET','POST'])
@app.route('/index', methods = ['GET','POST'])
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    administrator = False
    if request.method == "POST": 
        try:
            if login_success(request.form['user'],request.form['pw']):
                administrator = True
                return render_template('/index.html', admin = administrator)
            else:
                return render_template('/index.html', admin = administrator)
        except KeyError:
            print 'KeyError'
            return render_template('/index.html', admin = administrator)
    else:
        print 'method GET'
        return render_template('/index.html', admin = administrator)

@app.route('/changeuser.html',methods = ['GET','POST'])
def changeuser():
    return render_template('/changeuser.html', admin = administrator)

@app.route('/experiment_dashboard.html',methods = ['GET','POST'])
def experiment_dashboard():
    # experiments = SQL_query(username) #more pseudocode
    return render_template('/experiment_dashboard.html', admin = administrator) # , experiments = experiments

@app.route('/experiment_search.html', methods = ['GET','POST'])
def experiment_search():
    # return render_template('/experiment_search.html', admin = administrator)
    if request.method == "GET":
        return render_template('/experiment_search.html', admin = administrator) 
        # this one brings up the search interface, and experiment_search.html will post to itself when the Search button is clicked
    else:
    #     # experiments = SQL_query(conditions) #pseudocode for now
        x = request.form
        # print sorted(zip(x,[request.form[k] for k in x]))
        print compileToSQL(sorted(zip(x,[request.form[k] for k in x])))
        return render_template('/experiment_dashboard.html', admin = administrator, experiments = compileToSQL(sorted(zip(x,[request.form[k] for k in x])))) # , experiments = experiments
    #     #Do we want an additional line for direct SQL queries? If so, implement safeguards against SQL injection


#each line of the request form starts with a number now. 

# if we can get request.form to work the way we need it, socketio might not be needed - just query the database on post to experiment_search.
@socketio.on('search_experiment', namespace='/test')
def search_experiments(message): #message is one the built-in events that flask-socketIO has. A named custom event might work better - we want to control and log. 
    session['receive_count'] = session.get('receive_count', 0) + 1
    # print "message: ", message['data']
    # print query_SQL("select * from person where first_name is not null")
    # emit('my response',
    #      {'data': message['data'], 'count': session['receive_count']})

###################
#Form data to SQL #
###################
"""
We're gonna get form data from searches/edits/adding of experiments/protocols/stations/users/readers etc.

Translation to SQL will hopefully happen here.
"""

def compileToSQL(data): #data is a list of (input name, input value) tuples. Input value strings are utf-8 encoded and might need decoding, I think.
    """
    We want to translate form data from the search form into an SQL command.
    The first line should be "SELECT * FROM destination", so we can put that somewhere else.
    The rest of it will be "WHERE filter1 == value1 AND filter2 == value2 AND..."
    Then "ORDER BY order1 [desc], order2 [desc]"

    Do we want to blur out the 'is/is not option' for 'sort by' queries? Then just have options asc/desc. Lemme figure out how to do that.
    """
    queryStore = []
    for i in range(0,len(data),4): #4 because currently we have (action, filter, is/is not, value) for 4 columns
        searchRow = data[i:i+4] #right now, searchRow is a smaller list of (input name, input value) tuples that makes up a query. 
        queryStore.append(parse(searchRow))
    return queryStore #queryStore is gonna need to be reorganized so that all the parameters for the SELECT come first, then all the parameters for ORDER BY

def parse(row):
    return row



###################
#  Data Handling  #
###################

"""
I doubt we can insert a python datetime object into a mySQL database.

Also, we might want the SQL stuff to work on more than one database. 
In which case, we might need to pass the database info (user,pw,host,database) in as an argument.
"""

def editSQL(instruction, values): # both instruction and values are tuples
    """    
    instruction will be something like:

    ("insert into person "
        "(id,first_name) "
        "values (%s,%s)")

    values will be something like ("1","Jim")
    """
    with open('database_info.txt') as f:
        datalist = f.read().split(',')
    datalist = [k.replace(" ","") for k in datalist]
    cnx = mysql.connector.connect(user = datalist[0], password = datalist[1], host = datalist[2], database = datalist[3])
    cursor = cnx.cursor()
    try:
        cursor.execute(instruction, values)
        print [k for k in cursor]
        cursor.execute("commit") #this line is important if you actually want to make a permanent change to the database!
        cursor.close()
        cnx.close()
        return True
    except: #if the SQL edit fails for some reason, call it off and return False
        cursor.close()
        cnx.close()
        return False      

def querySQL(instruction):
    with open('database_info.txt') as f:
        datalist = f.read().split(',')
    datalist = [k.replace(" ","") for k in datalist]
    cnx = mysql.connector.connect(user = datalist[0], password = datalist[1], host = datalist[2], database = datalist[3])
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute(instruction)
        # print [row for row in cursor]
        result = [row for row in cursor]
        cursor.close()
        cnx.close()
        return result
    except: #if the SQL edit fails for some reason, call it off and return False
        cursor.close()
        cnx.close()
        return False          

# data = querySQL("select * from city where city_id <= 150 and country_id >=50 order by city_id")
# print data



# We might be able to convert a bigInt into a datetime object - then we might be able to use duration and other stuff
def bigIntToTime(bigInt): #we store start/end times as the number of hundredths-of-a-second (bigInt) since a predetermined point in time (the epoch).
    days = int(bigInt/(24 * 3600 * 100.0)) #each day has 24 hours, each hour has 3600 seconds, each second has 100 hundredths
    bigInt -= days * (24 * 3600 * 100.0)
    hours = int(bigInt/(3600 * 100.0))
    bigInt -= hours * (3600 * 100.0)
    minutes = int(bigInt/(60 * 100.0))
    bigInt -= minutes * (60 * 100.0)
    seconds = int(bigInt/(100.0))
    bigInt -= seconds * 100.0
    hundreths = int(bigInt)
    return "{0}d, {1:02}h {2:02}m {3:02}.{4:02}s".format(days,hours,minutes,seconds,hundreths)

# print bigIntToTime(68391758,0)



# class Experiment(object):
#     """I'm thinking maybe timeStart and timeEnd might be datetime objects? We can probably convert from whatever the RFID reader gives us"""
#     def __init__(self,user,experimentID,protocol,timeStart,duration=0,status="In Progress"):
#         self.user = user
#         self.experimentID = experimentID
#         self.protocol = protocol
#         self.timeStart = timeStart
#         self.duration = int(duration)
#         self.status = status
#     def integer_to_time(self):
#         timeInt = self.duration
#         hours = int(timeInt/3600.0)
#         timeInt -= hours * 3600
#         minutes = int(timeInt/60.0)
#         timeInt -= minutes * 60
#         seconds = int(timeInt)
#         return "{0:02}:{1:02}:{2:02}".format(hours,minutes,seconds)
#     def data(self):
#         return vars(self)
#     def data_with_proper_time(self):
#         result = vars(self)
#         result.duration = self.integer_to_time()
#         return result

# a = Experiment("0183503","MPI-001373-503(1)","MPI-001373 - Preparation of X","160608-10:07:02")
# b = Experiment(5,6,7,8)
# experiments = [a,b]
# a.status = "complete"
# a.duration += 100
# print a.data()
# print b.data()


if __name__ == '__main__':
    socketio.run(app, debug=True)

"""
Switch debug to False before actual implementation!
"""

###################
#   Unused Code   #
###################

# def SQL_query(search_conditions): 
# #for now, search conditions should be a dictionary with {filter:value} - something like {username:"100731", duration:(3600,7200), status: "complete"}
# #later on we'll actually have a database to query, hopefully
#     result = []
#     with open('database.txt','r') as f:
#         for k in f.read():
#             if meets_criteria(k,search_conditions):
#                 result.append(k)
#     return result

# def meets_criteria(entry, conditions):
#     pass
