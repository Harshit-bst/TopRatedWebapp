import json

from google.appengine.api.taskqueue import taskqueue


def save_new_apps_task_queue(request):
    taskqueue.add(
            method='GET',
            url='/api/v1/save-new-apps'
    )
    request.response.headers.add('Access-Control-Allow-Origin', '*')
    return request.response.out.write(json.dumps({"success": True, "info": "ADDED_REQUEST"}))