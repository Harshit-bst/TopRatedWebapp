import datetime
import json
import logging

from google.appengine.ext import db

from bs4 import BeautifulSoup

from top_rated_app.models import AndroidApp
from google.appengine.api import urlfetch, memcache


def add_apps_to_db(apps_data, category):
    for app in apps_data:
        try:
            image = app.find("img", attrs={"class": ["T75of", "QNCnCf"]}).attrs['data-src']
            name = app.find("div", attrs={"class": ["WsMG1c", "nnK0zc"]}).text
            pkg = app.find("div", attrs={"class": ["WsMG1c", "nnK0zc"]}).parent.attrs["href"].split("id=")[-1]
            corporation = app.find("div", attrs={"class": ["KoLSrc"]}).text

            android_app_obj = AndroidApp.get_by_key_name(pkg)
            if not android_app_obj:
                android_app_obj = AndroidApp(key_name=pkg)
            android_app_obj.image_url = image
            android_app_obj.name = name
            android_app_obj.corporation = corporation
            android_app_obj.pkg = pkg
            android_app_obj.category = category
            android_app_obj.updated_on = datetime.datetime.now()
            android_app_obj.disabled = False
            android_app_obj.put()
        except Exception as e:
            logging.exception("Failed to Scrape app data to database. Content: " + str(app))


def map_image_urls(button):
    attrs = list(button.children)[0].attrs
    if attrs.get("srcset"):
        return attrs['srcset']
    return attrs["data-src"]


def get_app_detail_json_formatted_data(data):
    icon = data.find("img", attrs={"alt": "Cover art"}).attrs["src"]
    name = data.find("h1", attrs={"class": ["AHFaub"]}).text
    rating = data.find("div", attrs={"role": "img"}).attrs['aria-label'].split(" ")[1]
    total_ratings = list(data.find("span", attrs={"class": ["AYi5wd", "TBRnV"]}).children)[0].text
    genre = data.find("a", attrs={"itemprop": "genre", "class": ["hrTbp", "R8zArc"]}).text
    corporation = data.find("span", attrs={"class": ["T32cc", "UAO9ie"]}).text
    download_url = data.find("meta", attrs={"itemprop": "url"}).attrs["content"]
    content = data.find("div", attrs={"jsname": "sngebd"}).text
    image_urls = list(map(map_image_urls, list(data.find("div", attrs={"class": ["SgoUSc"]}).children)))
    video_button = data.find("button", attrs={"aria-label": "Play trailer"})
    if video_button:
        video_url = video_button.attrs['data-trailer-url']
    else:
        video_url = None
    response = {
        "icon_url": icon,
        "name": name,
        "rating": rating,
        "total_ratings": total_ratings,
        "genre": genre,
        "corporation": corporation,
        "download_url": download_url,
        "content": content,
        "image_urls": image_urls,
        "video_url": video_url
    }
    return response


def get_app_details(request, *args, **kwargs):
    request.response.headers.add('Access-Control-Allow-Origin', '*')
    id = dict(request.str_params).get("id")
    if not id:
        return request.response.out.write(json.dumps({"error": "id is required"}))
    response_data = memcache.get("details_" + id)
    website = "https://web.archive.org/web/20220408090905/https://play.google.com/store/apps/details?id="+str(id)
    try:
        if not response_data:
            response = urlfetch.fetch(website)
            try:
                soup = BeautifulSoup(response.content, "html.parser")
                response_data = soup.find("c-wiz", attrs={"class": ["zQTmif", "SSPGKf", "I3xX3c", "drrice"]})
                response_data = get_app_detail_json_formatted_data(response_data)
            except Exception as e:
                response_data = {"error": "Unable to get details for package "+ str(id)}
            memcache.set("details_" + id, response_data, 21600)
        request.response.out.write(json.dumps({"data": response_data}))
    except Exception as e:
        logging.exception("Unable to scrape data from " + website + ".Please try again later")

def save_new_apps(request):
    # https://web.archive.org/web/20220408090905/https://play.google.com/store/apps/top
    # https://web.archive.org/web/20220409232016/https://play.google.com/store/apps/top
    # https://web.archive.org/web/20220413103059/https://play.google.com/store/apps/top
    website = "https://web.archive.org/web/20220413103059/https://play.google.com/store/apps/top"
    try:
        response = urlfetch.fetch(website)
        soup = BeautifulSoup(response.content, "html.parser")
        top_free_apps, top_paid_apps, top_grossing_apps, top_free_games, top_paid_games, top_grossing_games = list(soup.findAll("div", attrs={"class": ['ZmHEEd', 'fLyRuc']}))
        all_apps = db.GqlQuery("SELECT * "
                               "FROM AndroidApp "
                               "WHERE disabled = FALSE ")
        for app in all_apps:
            app.disabled = True
            app.put()
        add_apps_to_db(top_free_apps.children, "top_free_apps")
        add_apps_to_db(top_paid_apps.children, "top_paid_apps")
        add_apps_to_db(top_grossing_apps.children, "top_grossing_apps")
        add_apps_to_db(top_free_games.children, "top_free_games")
        add_apps_to_db(top_paid_games.children, "top_paid_games")
        add_apps_to_db(top_grossing_games.children, "top_grossing_games")
        request.response.out.write(json.dumps({"success": True}))
        request.response.headers.add('Access-Control-Allow-Origin', '*')
        # reset memcache
        memcache.delete("latest_60_apps")
    except Exception as e:
        logging.exception("Unable to scrape data from " + website + ".Please try again later")
        request.response.out.write(json.dumps({"success": False}))


def get_all_apps(request):
    response_data = memcache.get("latest_60_apps")
    if not response_data:
        all_apps = db.GqlQuery("SELECT * "
                                "FROM AndroidApp "
                                "WHERE disabled = FALSE "
                                "ORDER BY updated_on DESC LIMIT 60")
        response_data = {}
        for app in all_apps:
            data = {
                "icon_url": app.image_url,
                "name": app.name,
                "corporation": app.corporation,
                "pkg": app.pkg
            }
            category = app.category
            if response_data.get(category):
                response_data[category].append(data)
            else:
                response_data[category] = [data]
        memcache.set("latest_60_apps", response_data, 21600)
    request.response.out.write(json.dumps({"data": response_data}))
    request.response.headers.add('Access-Control-Allow-Origin', '*')
