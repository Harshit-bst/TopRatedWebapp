from google.appengine.ext import db


class AndroidApp(db.Model):
    pkg = db.StringProperty()
    name = db.StringProperty()
    corporation = db.StringProperty()
    image_url = db.StringProperty()
    details = db.StringProperty()
    category = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now=True)