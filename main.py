"""Web app for Google app engine."""

import os
import jinja2
import webapp2
import time
import datetime
import logging

from utils.login import (Users, checkUN, checkPwd, checkMatch, checkEmail,
                         make_salt, make_pw_hash, valid_pw,
                         LoginHandler, SignupHandler, cookie_check,
                         Permalink, LogoutHandler, make_date, FlushHandler)


from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import mail

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# higher access usernames
users1 = ["xxxxxxxxx", "xxxxxxxx", "xxxxxxxx"]


class Handler(webapp2.RequestHandler):
    """Base Handler Class."""

    def write(self, *a, **kw):
        """Write."""
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """Render str."""
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """Render."""
        self.write(self.render_str(template, **kw))


class MainPage(Handler):
    """Base page class."""

    def render_front(self, title="", entries="", error=""):
        """Front."""
        editor = False
        username, valid = cookie_check(self)
        if username in users1:
            editor = True
        if editor:
            topbar = '''<div style="text-align:right; text-decoration:none; padding-right:30px;">''' + username + '''
                    <a href="/newevent" style="color:#1F5C3D; text-decoration:none;">|| make new event |</a>
                    <a href="/logout" style="color:#1F5C3D; text-decoration:none;">| logout</a></div>'''
        elif valid:
            topbar = '''<div style="text-align:right; text-decoration:none; padding-right:30px;">''' + username + '''
                    <a href="/logout" style="color:#1F5C3D; text-decoration:none;">| logout</a></div>'''
        else:
            topbar = '''<div style="text-align:right; text-decoration:none; padding-right:30px;">
                    <a href="/signup" style="color:#1F5C3D; text-decoration:none;">sign-up |</a>
                    <a href="/admin" style="color:#1F5C3D; text-decoration:none;">login</a></div>'''
        entries, cache_time = get_top()
        time_cached = (time.time() - cache_time)
        self.render("front.html", eventlist=entries, topbar=topbar, time_cached=time_cached, valid=valid, editor=editor)  # editLink=editLink)#valid=valid)

    def get(self):
        self.render_front()


def get_top(update=False):
    key = "top"
    entry_cache = memcache.get(key)

    if entry_cache is None or update:
        logging.error("DB QUERY")
        entries = db.GqlQuery("SELECT * FROM Event WHERE date >= :1 ORDER BY date LIMIT 10", datetime.date.today())

        entries = list(entries)
        memcache.set(key, (entries, time.time()))
        entry_cache = memcache.get(key)
    return entry_cache[0], entry_cache[1]


def get_users():
    user_list = db.GqlQuery("Select * FROM Users")
    user_list = list(user_list)
    return user_list


class AboutPage(Handler):
    def get(self):
        self.render("about.html")


class WorkIPHandler(Handler):
    def get(self):
        self.render("WIP.html")


class NewsletterHandler(Handler):
    def get(self):
        self.render("newsletter.html")


class TravelHandler(Handler):
    def get(self):
        self.render("travelclub.html")


class ScratchHandler(Handler):  # this is just for screwing around
    def get(self, error=""):

        # memcache testing
        '''
        key = "top"
        entries = memcache.get(key)
        self.write("memcache is of type: " + str(type(entries)))
        self.write("tuple is of length:" + str(len(entries)))
        self.write("the first of two elements is of type" + str(type(entries[0])))
        self.write("<br><br>the list at entry[0] is of length: "  + str(len(entries[0])) + "<br>")
        self.write("the [0] element is of type: " + str(type(entries[0][0])) +"<br>")
        self.write("the [1] element is of type: " + str(type(entries[0][1])) +"<br>")
        self.write("the [2] element is of type: " + str(type(entries[0][2])) +"<br>")
        gettop1, gettop2 = get_top()
        if gettop1 == entries[0]:
            self.write("True")
        else:
            self.write("False")
        self.write("gettop1 is of type: " + str(type(gettop1)))
        self.write("type is of length:" + str(len(gettop1)))
        self.write("the [0] element is of type: " + str(type(gettop1[0])) +"<br>")
        self.write("the [1] element is of type: " + str(type(gettop1[1])) +"<br>")
        self.write("the [2] element is of type: " + str(type(gettop1[2])) +"<br>")
        '''
        # trial = memcache.get("5891733057437696")
        # self.write("trial is of type: " + str(type(trial)))
        # self.write("tuple is of length:" + str(len(trial)))
        # self.write("the first of two elements is of type" + str(type(trial[0])))
        # self.write("the second of two elements is of type" + str(type(trial[1])))
        # self.write(trial[1])

        username, valid = cookie_check(self)
        if username in users1 and valid:
            self.write("valid user")
        else:
            self.write("Not quite right")

        user_list = get_users()
        for user in user_list:
            self.write(user.username + "<br>")
            # self.write(make_date(user.created) + "<br>") # need to format the time
            self.write(user.email + "<br>")

        self.render("scratch.html")

    def post(self, date='', error=''):
        message = mail.EmailMessage(sender="KCSC webadmin <admin@kcseniorscentre.appspot.com>",
                                    subject="Test email")

        message.to = "Ben Field <benjamin.field@gmail.com>"
        message.body = "One of our submarines is missing..."
        message.send()

        '''
        # date stuff
        date = self.request.get("eventdate")
        if not date:
            self.write(str(type(date)))
            self.write(date)
            self.write("Please enter a date")
        else:
            self.write("You entered a date")
            self.write(str(type(date)))
            self.write(date)
            self.write("<br><br>")
            date = str(date)
            self.write(date)
            dateArray = date.split("-")
            f = dateArray
            self.write(dateArray)
            self.write("<br><br>")
            year = dateArray[0]
            month = dateArray[1]
            day = dateArray[2]
            self.write("<br><br>")
            self.write("year is: " + year + "<br>")
            self.write("month is: " + month + "<br>")
            self.write("day is: " + day + "<br><br>")
            t = (int(year), int(month), int(day), 0,0,0,0,0,0)
            pytime = time.mktime(t)
            self.write("<br><br>")
            e = datetime.date(int(f[0]), int(f[1]), int(f[2]))
            self.write("e is of type: " + str(type(e)) + "<br>")
            self.write(e.strftime('%A'))
            self.write(e.strftime('%b'))
            self.write(e.strftime('%d'))
            self.write("<br><br>")
            self.write(e.strftime('%A %b %d'))
            self.write(date)
            newdate = make_date(date)
            self.write(newdate)
            self.write("this is of type" + str(type(newdate)))

            #memcache.flush_all()
            '''


class Event(db.Model):
    date = db.DateProperty(required=True)  # datetime.date object (year, month, date attributes)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


class NewEventHandler(Handler):
    def get(self):
        username, valid = cookie_check(self)
        if username in users1 and valid:
            self.render("newevent.html", title='', content='', error='')
        else:
            self.write("You don't have permission to enter a new event.")

    def post(self, title='', content='', date=''):
        title = self.request.get('title')
        content = self.request.get('content')
        date = self.request.get('date')
        if not (title and content and date):
            error = "title, content, and date required"
            self.render('newevent.html', title=title, content=content, date=date, error=error)
        else:
            date = make_date(date)
            a = Event(title=title, content=content, date=date)
            b_key = a.put()  # Key('Event', id)
            memcache.flush_all()  # because the update isn't working, might be overkill w/ the redirect
            # get_top(update=True) # memcacache line to update

            # self.redirect("/%d" % b_key.id())
            self.redirect("/flush")


app = webapp2.WSGIApplication([('/', MainPage),
                               ('/scratch', ScratchHandler), # get rid of this eventually
                               ('/admin', LoginHandler),
                               ('/signup', SignupHandler),
                               ('/newevent', NewEventHandler),
                               ('/(\d+)', Permalink),
                               # ('/preview', PreviewHandler), #might not want this at all
                               ('/about', AboutPage),
                               ('/newsletter', NewsletterHandler),
                               ('/logout', LogoutHandler),
                               ('/programs', WorkIPHandler),
                               ('/travelclub', TravelHandler),
                               ('/contact', WorkIPHandler),
                               ('/flush', FlushHandler)
                               ], debug=True)
