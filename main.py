import webapp2

from top_rated_app.api.v1.views import get_all_apps, get_app_details, save_new_apps


class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp2 World!')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    webapp2.Route('/api/v1/get-all-apps', get_all_apps, methods=['GET']),
    webapp2.Route('/api/v1/apps/details', get_app_details, methods=['GET']),
    webapp2.Route('/api/v1/save-new-apps', save_new_apps, methods=['GET']),
], debug=True)