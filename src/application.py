from flask import Flask, Response, request
from datetime import datetime
import json
from cbs_resource import CBSresource
from flask_cors import CORS
from utils import DTEncoder

# Create the Flask application object.
app = Flask(__name__,
            static_url_path='/',
            static_folder='static/class-ui/',
            template_folder='web/templates')

# CORS(app)
cors = CORS(app, resources={r'/api/*':{'origins':'*'}})


@app.route("/api/user/<id>", methods=["GET"])
def get_user_by_id(id):

    result = CBSresource.get_user_by_key(id)

    if result:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    print(result)
    return rsp

@app.route("/api/user/login", methods=["POST"])
def login():
    if request.method == 'POST':
        user_id_res = CBSresource.verify_login(request.get_json()['email'], request.get_json()['password'])
        if user_id_res:
            result = {'success':True, 'message':'login successful','userId':user_id_res}
            rsp = Response(json.dumps(result), status=200, content_type="application.json")
        else: 
            result = {'success':False, 'message':'Wrong username or password'}
            rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("Methods not defined", status=404, content_type="text/plain")
    return rsp

@app.route("/api/user/register", methods=["POST"])
def register():
    if request.method == 'POST':
        result = CBSresource.register_user(request.get_json()['email'], request.get_json()['username'], request.get_json()['password'])
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("Methods not defined", status=404, content_type="text/plain")
    return rsp

@app.route("/api/session", methods=["POST"])
def get_available_session():
    result = CBSresource.get_available_session(request.data)
    if result['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    return rsp

@app.route("/api/session/<sessionid>", methods=["GET"])
def get_session_by_key(sessionid):

    result = CBSresource.get_session_by_key(sessionid)
    if result['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    return rsp

@app.route("/api/session/user/<userid>", methods=["GET"])
def get_session_by_user(userid):

    result = CBSresource.get_session_by_user(userid)
    if result['success']:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    return rsp

@app.route("/api/session/<sessionid>/enroll/<userid>", methods=["POST"])
def enroll_session(sessionid, userid):
    print(request.data)
    result = CBSresource.enroll_session(sessionid, userid, with_partner=int(request.data))
    if result['success']:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    return rsp

@app.route("/api/session/<sessionid>/quit/<userid>", methods=["GET"])
def quit_waitlist(sessionid, userid):

    result = CBSresource.quit_waitlist(sessionid, userid)
    if result['success']:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    return rsp
@app.route("/api/user/reset", methods=["POST"])
def reset():
    if request.method == 'POST':
        user_id_res = CBSresource.reset_password(request.get_json()['email'], request.get_json()['old_password'],
                                                 request.get_json()['new_password'])
        if user_id_res:
            result = {'success': True, 'message': 'changing successful'}
            rsp = Response(json.dumps(result), status=200, content_type="application.json")
        else:
            result = {'success': False, 'message': 'Wrong username or password'}
            rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("Methods not defined", status=404, content_type="text/plain")
    return rsp

@app.route("/api/userprofile/<userid>", methods=["GET"])
def show(userid):
    result = CBSresource.show_profile(userid)
    if result['success']:
        rsp = Response(json.dumps(result, default=str), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, default=str), status=404, content_type="application.json")
    return rsp

@app.route("/api/userprofile2/<userid>", methods=["GET"])
def show2(userid):
    result = CBSresource.show_profile2(userid)
    if result['success']:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result), status=404, content_type="application.json")
    return rsp

@app.route("/api/userprofile/edit/<userid>", methods=["POST"])
def edit(userid):
    ## where post id is important
    if request.method == 'POST':
        result = CBSresource.edit_profile(request.get_json()['username'], request.get_json()['sex'],
                                          request.get_json()['birthday'],
                                          request.get_json()['preference'],
                                          request.get_json()['email'],
                                          #  request.get_json()['credits'],
                                          userid)
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response("Methods not defined", status=404, content_type="text/plain")
    return rsp


@app.route("/api/check_partner/<userid>", methods=["GET"])
def check_partner(userid):
    result = CBSresource.show_profile2(userid)
    if result['success']:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result), status=404, content_type="application.json")
    return rsp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=True)

