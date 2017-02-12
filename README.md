# Hacking the Library - Community Calendar
### Emily Yeh, Leon Lam


#### Vision
Currently, email is the primary way for people to find out about events that (have happened/are happening/will happen) on campus. We decided to explore an alternative method of event storage and display in the form of a community calendar - a calendar of events arranged by date that the community can access and contribute to.


#### Features
Our app is a standard calendar hosted on Heroku that displays truncated event names under their dates. Clicking on arrows next to the month/date will shift the calendar view to an adjacent month, displaying the events occuring during that new time period. Alternatively, an input box allows users to 'Do the Doctor Who' and jump to other month/year combinations.

![Main page](https://github.com/leonjunwei/htl-calendar/blob/master/Capture_calendar.PNG)
*Calendar page.*


Clicking on the 'Agenda View' button or the number in any box will load an agenda view page with the appropriate events. The 'Agenda View' button will load all events starting in that month, whereas the number in any box will load all events starting on that date.

![Agenda view](https://github.com/leonjunwei/htl-calendar/blob/master/Capture_agenda.PNG)
*Agenda view page.*


Clicking on the 'Submit Event' button will load an event submission page where the user can input the details of their event and submit it. After submission, the event will be stored in Heroku's postgreSQL database where it can be retrieved at a later date.

![Submit event](https://github.com/leonjunwei/htl-calendar/blob/master/Capture_event_submission.PNG)


#### Code
The code is a standard flask webapp. We have a server.py file that acts as the skeleton of the website, some static resources like backgrounds and CSS files, and html templates that display the data to the user.

Global variables (display_month and display_year) are used to keep track of the month and year to display - this has the unfortunate side effect of making one user's actions affect every other user's displayed calendar (since we only tested with one user, this was totally fine).

Data is passed from HTML templates to python by HTML form inputs. Flask receives this as a dictionary request.form, and parses it to retrieve the relevant information. Data is passed back into HTML by way of Flask's render_template method.

The events themselves are stored in a postgreSQL server provided by Heroku (hobby-dev level, 10000 rows available - if necessary, we could purchase a more expensive database plan). We use psycopg2 as a connector between the python code and the database.


#### Running the Code
1. [Create Heroku App](https://devcenter.heroku.com/articles/git) (preferably with GitHub)
2. [Provision postgreSQL database for app](https://devcenter.heroku.com/articles/heroku-postgresql)
3. Push code to app
4. Open app in browser
