#!/usr/bin/env python

import psycopg2 #postgres connector for python
import time
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import flask_login


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
#    Sitemap      #
###################
"""
Basic site. One page for calendar (searchable, maybe), one page to submit events and maybe one page to view a selected event in detail.
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
                return render_template('/index.html')
            else:
                return render_template('/index.html')
        except KeyError:
            print 'KeyError'
            return render_template('/index.html')
    else:
        print 'method GET'
        return render_template('/index.html')

@app.route('/changeuser.html',methods = ['GET','POST'])
def changeuser():
    return render_template('/changeuser.html')

@app.route('/experiment_dashboard.html',methods = ['GET','POST'])
def experiment_dashboard():
    # experiments = SQL_query(username) #more pseudocode
    return render_template('/experiment_dashboard.html') # , experiments = experiments

@app.route('/experiment_search.html', methods = ['GET','POST'])
def experiment_search():
    # return render_template('/experiment_search.html')
    if request.method == "GET":
        return render_template('/experiment_search.html') 
        # this one brings up the search interface, and experiment_search.html will post to itself when the Search button is clicked
    else:
    #     # experiments = SQL_query(conditions) #pseudocode for now
        x = request.form
        # print sorted(zip(x,[request.form[k] for k in x]))
        print compileToSQL(sorted(zip(x,[request.form[k] for k in x])))
        return render_template('/experiment_dashboard.html', experiments = compileToSQL(sorted(zip(x,[request.form[k] for k in x])))) # , experiments = experiments
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
Get form data from event submission page, turn into SQL-storable stuff
"""








if __name__ == '__main__':
    socketio.run(app, debug=True)

"""
Switch debug to False before actual implementation!
"""
