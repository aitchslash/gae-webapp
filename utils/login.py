import os
import webapp2
import jinja2
import random
import string
import re
import hashlib
import logging
import datetime
import time
from google.appengine.ext import db
from google.appengine.api import memcache

template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class LoginHandler(Handler):
    def get(self):
        self.render('login.html', username='', password='', pwInvalid='')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        user_data = db.GqlQuery("SELECT * FROM Users WHERE username =:1", username).get()
        if not (username and password):
            pwInvalid = "Invalid login0"
        elif not user_data:
            pwInvalid = "Invalid login1"
        elif make_pw_hash(username, password, user_data.userHash.split('|')[1]).split('|')[0] != user_data.userHash.split('|')[0]:
            pwInvalid = "Invalid login3"
        else:
            pwInvalid = ""

        if pwInvalid:
            self.render('login.html', username="", password="", pwInvalid=pwInvalid)
        else:
            self.response.headers.add_header('Set-Cookie', 'usercookie=' + str(username) +
                                             '|' + str(user_data.userHash.split('|')[0]) + '; Path=/')
            self.redirect('/')


class SignupHandler(Handler):
    def get(self, username='', password='', verify='', email='', unerror="", pwInvalid='', noMatch='', emailErr=''):
        self.render('signup.html',
                    username=username,
                    password=password,
                    verify=verify,
                    email=email,
                    unerror=unerror,
                    pwInvalid=pwInvalid,
                    noMatch=noMatch,
                    emailErr=emailErr)

    def post(self):
        username = self.request.get('username')
        unerror = checkUN(username)

        password = self.request.get('password')
        pwInvalid = checkPwd(password)

        verify = self.request.get('verify')
        if pwInvalid == "":
            noMatch = checkMatch(password, verify)
        else:
            noMatch = ""

        email = self.request.get('email')
        emailErr = checkEmail(email)

        if (unerror or pwInvalid or noMatch or emailErr):
            password = ""
            verify = ""
            self.render('signup.html',
                        username=username,
                        password=password,
                        verify=verify,
                        email=email,
                        unerror=unerror,
                        pwInvalid=pwInvalid,
                        noMatch=noMatch,
                        emailErr=emailErr)
        else:
            user_str = str(username)
            salt = make_salt()  # will this fix it?
            hash_raw = make_pw_hash(user_str, password, salt)
            hash_val = hash_raw.split('|')[0]

            a = Users(username=user_str, userHash=hash_raw, email=email)
            # user_id = a.put()  # Key('Blog', id) #old key generating line
            a.put()

            self.response.headers.add_header('Set-Cookie', 'usercookie=' + user_str +
                                             '|' + hash_val + '; Path=/')

            time.sleep(.5)  # to allow user db to update - newuser is throwing a "no hash error"
            self.redirect('/')


class Permalink(Handler):
    def get(self, event_id):
        key = "top"  # was event_id
        entry = memcache.get(event_id)
        # self.write("here first")
        if entry is None:
            # logging.error("DB QUERY") #test line
            s = Event.get_by_id(int(event_id))
            memcache.set(event_id, (s, time.time()))

        entry = memcache.get(event_id)

        time_cached = time.time() - entry[1]  # not currently in use
        event = entry[0]
        self.render("permalink.html", event=event, time_cached=time_cached)

    def post(self, event_id, title='', content='', date=''):
        title = self.request.get('title')
        content = self.request.get('content')
        date = self.request.get('date')
        if not (title and content and date):
            error = "title, content, and date required"
            self.render('permalink.html', title=title, content=content, date=date, error=error)
        else:
            date = make_date(date)
            # t = Event(key_name=event.key().id_or_name(), title=title, content=content) #create object
            s = Event.get_by_id(int(event_id))
            # s.delete()
            # t = Event(id=int(event_id), date = date, content=content, title=title)
            s.date = date
            s.content = content
            s.title = title

            s.put()
            memcache.set(event_id, (s, time.time()))  # might need this but try flushing instead
            # memcache.flush_all()  # because the update isn't working
            get_top(True)  # memcacache line to update

            # try to force memcache update by reproducing get_top(True)
            logging.error("DB QUERY")
            entries = db.GqlQuery("SELECT * FROM Event WHERE date >= :1 ORDER BY date LIMIT 10", datetime.date.today())
            key = "top"
            entries = list(entries)
            memcache.set(key, (entries, time.time()))
            entry_cache = memcache.get(key)
            # end of force

            self.redirect("/flush")  # flushes the cache redirects home.  can get rid of most of the above lines


def get_top(update=False):  # duplicated on main, if the line just above is commented out, can be deleted
    key = "top"
    entry_cache = memcache.get(key)

    if entry_cache is None or update:
        logging.error("DB QUERY")
        entries = db.GqlQuery("SELECT * FROM Event WHERE date >= :1 ORDER BY date LIMIT 10", datetime.date.today())

        entries = list(entries)
        memcache.set(key, (entries, time.time()))
        entry_cache = memcache.get(key)
    return entry_cache[0], entry_cache[1]


class FlushHandler(Handler):
    def get(self):
        self.write("Memcache flush in progress")
        memcache.flush_all()
        self.write("Whoosh!")
        self.redirect('/')


class LogoutHandler(Handler):
    def get(self):
        self.write("Logout page")
        if self.request.cookies.get('usercookie'):
            self.response.headers.add_header('Set-Cookie', 'usercookie=; Path=/')
        self.redirect('/')


class Users(db.Model):
    username = db.StringProperty(required=True)
    userHash = db.TextProperty(required=True)
    email = db.StringProperty(required=False)
    created = db.DateTimeProperty(auto_now_add=True)


class Event(db.Model):
    date = db.DateProperty(required=True)  # datetime.date object (year, month, date attributes)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)


def checkUN(username):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    match = USER_RE.match(username)
    foo = db.GqlQuery("SELECT * FROM Users WHERE username =:1",  username).get()

    if not match:
        unerror = "That's not a valid username"
    elif foo:
        unerror = "That user already exists"
    else:
        unerror = ""
    return unerror


def checkPwd(password):
    USER_RE = re.compile(r"^.{3,20}$")
    match = USER_RE.match(password)
    if match:
        pwInvalid = ''
    else:
        pwInvalid = "That wasn't a valid password"
    return pwInvalid


def checkMatch(password, verify):
    errors = 0
    if len(password) != len(verify):
        errors += 1
    for character in range(0, min(len(password), len(verify))):
        if password[character] != verify[character]:
            errors += 1
    if errors == 0:
        noMatch = ""
    else:
        noMatch = "You passwords didn't match"
    return noMatch


def checkEmail(email):
    USER_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    match = USER_RE.match(email)
    if (match or email==""):
        emailErr = ''
    else:
        emailErr = "That's not a valid email"
    return emailErr


def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt=""):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s|%s' % (h, salt)


def valid_pw(name, pw, h):
    hash_val, salt = h.split('|')[0], h.split("|")[1]
    hash_test_raw = make_pw_hash(name, pw, salt)
    hash_test = hash_test_raw.split('|')[0]
    if hash_val == hash_test:
        return True


def cookie_check(self):
    username_cookie = self.request.cookies.get('usercookie')
    if username_cookie:
        user_cookie, cookie_hash = username_cookie.split('|')[0], username_cookie.split('|')[1]

        user_data = db.GqlQuery("SELECT * FROM Users WHERE username=:1", str(user_cookie)).get()
        hash_comp = user_data.userHash.split('|')[0]

        if cookie_hash == hash_comp:
            # self.write("got here %s <br>" % user_cookie) #old line
            return user_cookie, True
        else:
            return user_cookie, False
    else:
        user_cookie = ""
        return user_cookie, False


def make_date(htmldate):  # move to utils
    date = str(htmldate)
    f = date.split("-")  # date as array
    newdate = datetime.date(int(f[0]), int(f[1]), int(f[2]))
    return newdate
