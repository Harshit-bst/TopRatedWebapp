from google.appengine.ext import db


class AndroidApp(db.Model):
    __tablename__ = 'android_app'
    id = db.Column(db.Integer, primary_key=True)
    pkg = db.StringProperty()
    name = db.StringProperty()
    corporation = db.StringProperty()
    image_url = db.StringProperty()
    details = db.StringProperty()
    category = db.StringProperty()
    created_on = db.StringProperty()