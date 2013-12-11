# Copyright (C) 2011 Nitin Pathak (www.popofibo.com)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
import cgi
import logging
import datetime
import time
import wsgiref.handlers
from time import strftime
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import images

authenticate_names = ["popo.fibo@gmail.com",
                      "pathak.nitin@gmail.com"
                      ]

names = {'popo.fibo@gmail.com':"Nitin Pathak",
         'pathak.nitin@gmail.com': "Pathak Nitin"
         }

months = {'01': "January",
          '02': "February",
          '03': "March",
          '04': "April",
          '05': "May",
          '06': "June",
          '07': "July",
          '08': "August",
          '09': "September",
          '010': "October",
          '011': "November",
          '012': "December"
          }

nmonth = {'01': "January",
          '02': "February",
          '03': "March",
          '04': "April",
          '05': "May",
          '06': "June",
          '07': "July",
          '08': "August",
          '09': "September",
          '10': "October",
          '11': "November",
          '12': "December"
          }

days = ["01","02","03","04","05",
        "06","07","08","09","10",
        "11","12","13","14","15",
        "16","17","18","19","20",
        "21","22","23","24","25",
        "26","27","28","29","30",
        "31"]

class MyShout(db.Model) :
    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    
class MyAvatar(db.Model) :
    member = db.UserProperty()
    avatar = db.BlobProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MyAssigned(db.Model) :
    assignedby = db.UserProperty()
    employee = db.StringProperty()
    task = db.TextProperty()
    tobedate = db.StringProperty()
    completedate = db.StringProperty()
    iscomplete = db.BooleanProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MyBirthdays(db.Model) :
    member = db.UserProperty()
    birthmonth = db.StringProperty()
    birthday = db.StringProperty()

class MyMovies(db.Model) :
    author = db.UserProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)

class MyCsv(db.Model) :
    filename = db.StringProperty(multiline=False) 
    inputfile = db.BlobProperty() 
    ext = db.StringProperty(multiline=False) 
    date = db.DateTimeProperty(auto_now_add=True) 

class MoviesOut (webapp.RequestHandler) :
    def get (self) :
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        mymovie = MyMovies()
        mymovies_query = MyMovies.all().order('-date')
        mymovies = mymovies_query.fetch(100)
        myavatars_query = MyAvatar.all().order('-date')
        myavatars = myavatars_query
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'names': names,
            'user': users.get_current_user(),
            'mymovies': mymovies,
            'myavatars': myavatars,
            'url': url,
            'url_linktext': url_linktext,
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'movies.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))
        
class MoviesArchive (webapp.RequestHandler) :
    def post(self) :
        mymovie = MyMovies()
        if users.get_current_user() :
            mymovie.author = users.get_current_user()
        mymovie.content = self.request.get('content')
        mymovie.put()
        self.redirect('/movies')

class BirthdaysOut(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        month = strftime("%m")
        date = strftime("%d")
        month_int = int(month)+1
        month_next = '0'+str(month_int)
        if month_next == '013':
            month_next = '01'
        month_names = list()
        for key, value in sorted(nmonth.items()):
            month_names.append(value)
        myupdate = MyBirthdays.all().filter('member = ', user).fetch(1)
        mytoday_birthday = MyBirthdays.all().filter('birthmonth = ', nmonth[month]).filter('birthday > ', date).fetch(50)
        mytoday_birthday_next = MyBirthdays.all().filter('birthmonth = ', months[month_next]).fetch(50)
        todays = MyBirthdays.all().filter('birthmonth = ', nmonth[month]).filter('birthday = ', date)
        today = todays.fetch(100)
        myavatars_query = MyAvatar.all().order('-date')
        myavatars = myavatars_query
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'names': names,
            'user': user,
            'days': days,
            'months': month_names,
            'myupdate': myupdate,
            'mybirthdays': mytoday_birthday,
            'mynextbirthdays': mytoday_birthday_next,
            'myavatars': myavatars,
            'today': today,
            'url': url,
            'url_linktext': url_linktext
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'birthdays.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))


class BirthdaysArchive(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        mybirthdays = MyBirthdays()
        if users.get_current_user() :
            mybirthdays.member = users.get_current_user()
        mybirthdays.birthmonth = self.request.get('month')
        mybirthdays.birthday = self.request.get('day')
        mybirthdays.put()
        self.redirect('/bdays')

class TasksOut(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
            email = str(user.email())
            employee = email.lower()
            mytasks_query = MyAssigned.all().filter('employee = ', employee).order('-date')
            mytasks = mytasks_query.fetch(10)
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
            month = strftime("%m")
            template_values = {
                'month': month,
                'names': names,
                'user': user,
                'mytasks': mytasks,
                'url': url,
                'url_linktext': url_linktext
                }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'tasks.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))

class TasksArchive(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        myassigned = MyAssigned()
        if user:
            email = str(user.email())
            employee = email.lower()
            mytasks_query = MyAssigned.all().filter('employee = ', employee).order('-date')
            mytask_key = self.request.get('key')
            for mytask in mytasks_query:
                if str(mytask.key()) == mytask_key:
                    mytask.iscomplete = True
                    mytask.completedate = self.request.get('complete')
                mytask.put()
        myassigned.put()
        self.redirect('/tasks')

class AssignedOut(webapp.RequestHandler):
    def get(self):
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        myassigned_query = MyAssigned.all().filter('assignedby = ', user).order('-date')
        myassigns = myassigned_query.fetch(10)
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'names': names,
            'user': users.get_current_user(),
            'employees': sorted(authenticate_names),
            'myassigns': myassigns,
            'url': url,
            'url_linktext': url_linktext
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'tasksassignment.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))

class AssignedArchive(webapp.RequestHandler):
    def post(self):
        user = users.get_current_user()
        myassigned = MyAssigned()
        if users.get_current_user() :
            myassigned.assignedby = users.get_current_user()
        myassigned.task = self.request.get('task')
        myassigned.employee = self.request.get('users')
        myassigned.tobedate = self.request.get('tobedate')
        myassigned.iscomplete = False
        myassigned.put()
        self.redirect('/assigned')
        
class ImageOut(webapp.RequestHandler) :
    def get(self):
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        myavatar_query = MyAvatar.all().filter('member = ', user).order('-date')
        myimage = myavatar_query.fetch(1)
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'names': names,
            'user': users.get_current_user(),
            'myimage': myimage,
            'url': url,
            'url_linktext': url_linktext,
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'avatar.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))

class ImageArchive(webapp.RequestHandler) :
    def post(self):
        user = users.get_current_user()
        myavatar = MyAvatar()
        try:
            myavatar.member = user
            avatar = images.resize(self.request.get("img"), 100, 100)
            myavatar.avatar = db.Blob(avatar)
        except images.NotImageError, message:
            logging.exception("Image was not selected. Using a default image.")
            myavatar.avatar = None
        except images.BadImageError, message:
            logging.exception("Image selected is corrupt. Using a default image.")
            myavatar.avatar = None
        except images.Error, message:
            logging.exception("Image selected is corrupt. Using a default image.")
            myavatar.avatar = None
        myavatar.put()
        self.redirect('/avatar')

class CsvOut(webapp.RequestHandler) :
    def get(self):
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        myfile = MyCsv.all().order('-date').get()
        if myfile:
            f = db.Blob(myfile.inputfile)
            largest = 0
            comma = 0
            slashn = 0
##            filehandle = open("test", "a")
##            filehandle.write(f)
##            filehandle.close()
##
##            myfile = open('test', 'r')
##            filelist = myfile.readlines()
##            for line in filelist:
##                self.response.out.write(line)
##            filehandle.close()
##            #self.response.out.write('Nitin --> ' + str((str(f)).find('\n')))
            for c in str(f):
                if c == ',':
                    comma += 1
                    if comma >= largest:
                        largest = comma
                if c == '\n':
                    slashn += 1
                    comma = 0
            #filecontent = f.replace('\n', ',')
            string = f.split(',')
##            for s in string:
##                self.response.out.write(s)
##                self.response.out.write('********')
            self.response.out.write(string.pop(200))
            self.response.out.write(str(largest) + str(slashn))
            for s in string:
                self.response.out.write("""
                <tr>""")
            for i in range(0, slashn-1):
                self.response.out.write("""
                <tr>""")
                for j in range(0, largest-1):
                    self.response.out.write('-')
##                      self.response.out.write("""
##                      <td>""" + string.pop(i + j) + """</td>""")
            self.response.out.write(str(i+j))
                                    
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'largest': largest,
            'filecontents': f,
            'user': users.get_current_user(),
            'url': url,
            'url_linktext': url_linktext
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'csv.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))

class CsvArchive(webapp.RequestHandler) :
    def post(self):
        user = users.get_current_user()
        newfile = MyCsv() 
        newfile.filename = self.request.get('filename') 
        newfile.ext = self.request.get('ext') 
        newfile.inputfile = db.Blob(self.request.get('csv')) 
        newfile.put() 
        self.redirect('/csvt')

class ShoutOut (webapp.RequestHandler) :
    def get (self) :
        user = users.get_current_user()
        authenticate = False
        if user:
            logging.debug("User attempting to login with email --> "+user.email())
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        myshout = MyShout()
        myshouts_query = MyShout.all().order('-date')
        myshouts = myshouts_query.fetch(20)
        myavatars_query = MyAvatar.all().order('-date')
        myavatars = myavatars_query
        month = strftime("%m")
        day = strftime("%d")
        if str(int(day)-1) != "0":
            day = str(int(day)-1)
        else:
            month = str(int(month)-1)
        if len(day) == 1:
                day = "0" + day
        if len(month) == 1:
                month = "0" + month
        year_full = strftime("%Y")
        year = strftime("%y")
        mycartoon = str("http://images.ucomics.com/comics/ga/"+year_full+"/ga"+year+month+day+".gif")
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'names': names,
            'user': users.get_current_user(),
            'myshouts': myshouts,
            'myavatars': myavatars,
            'mycartoon': mycartoon,
            'url': url,
            'url_linktext': url_linktext,
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'shoutarchive.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))

class ShoutOutLimit (webapp.RequestHandler) :
    def post (self) :
        user = users.get_current_user()
        authenticate = False
        if user:
            username = str(user.email())
            for name in authenticate_names:
                if username.lower() == name.lower():
                    authenticate = True
        myshout = MyShout()
        if self.request.get('limit') == 'Ten':
            limit = 30
        elif self.request.get('limit') == 'Twenty':
            limit = 40
        else:
            limit = 100
        myshouts_query = MyShout.all().order('-date')
        myshouts = myshouts_query.fetch(limit)
        myavatars_query = MyAvatar.all().order('-date')
        myavatars = myavatars_query
        url = users.create_logout_url('/')
        url_linktext = 'Logout'
        template_values = {
            'names': names,
            'user': users.get_current_user(),
            'myshouts': myshouts,
            'myavatars': myavatars,
            'url': url,
            'url_linktext': url_linktext,
            }
        if authenticate == True:
            path = os.path.join(os.path.dirname(__file__), 'shoutarchive.html')
        else:
            path = os.path.join(os.path.dirname(__file__), 'notauthenticated.html')
        self.response.out.write (template.render(path, template_values))
        
class ShoutArchive (webapp.RequestHandler) :
    def post(self) :
        myshout = MyShout()
        if users.get_current_user() :
            myshout.author = users.get_current_user()
        myshout.content = self.request.get('content')
        myshout.put()
        self.redirect('/user')
        
class Image(webapp.RequestHandler):
    def get(self):
        myavatar = db.get(self.request.get("img_id"))
        if myavatar.avatar:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(myavatar.avatar)
        else:
            self.error(404)
            
class MainPage (webapp.RequestHandler) :
    def get (self) :
        logging.debug("Hit on the MainPage.")
        if users.get_current_user():
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
        else:
            url = users.create_login_url('/user')
            url_linktext = 'Login'
        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            }
        path = os.path.join(os.path.dirname(__file__), 'prelogin.html')
        self.response.out.write (template.render(path, template_values))

class StaticHtml (webapp.RequestHandler) :
    def get (self) :
        logging.debug("Hit on the MainPage.")
        if users.get_current_user():
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
        else:
            url = users.create_login_url('/user')
            url_linktext = 'Login'
        template_values = {
            'url': url,
            'url_linktext': url_linktext,
            }
        path = os.path.join(os.path.dirname(__file__), 'googlehostedservice.html')
        self.response.out.write (template.render(path, template_values))
        
def main() :
    application = webapp.WSGIApplication([
        ('/', MainPage),
        ('/sign', ShoutArchive),
        ('/user', ShoutOut),
        ('/limit', ShoutOutLimit),
        ('/img', Image),
        ('/avatar', ImageOut),
        ('/upload', ImageArchive),
        ('/assigned', AssignedOut),
        ('/assign', AssignedArchive),
        ('/tasks', TasksOut),
        ('/complete', TasksArchive),
        ('/bdays', BirthdaysOut),
        ('/mybday', BirthdaysArchive),
        ('/movies', MoviesOut),
        ('/mymovie', MoviesArchive),
        ('/csvt', CsvOut),
        ('/view', CsvArchive),
        ('/googlehostedservice.html', StaticHtml)
        ], debug=True)
    wsgiref.handlers.CGIHandler().run(application)
if __name__ == "__main__":
    main()
