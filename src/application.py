from flask import Flask, Response, request, redirect, url_for, make_response
from datetime import datetime
import json
from cbs_resource import CBSresource
from flask_cors import CORS
from utils import DTEncoder
from oauthlib.oauth2 import WebApplicationClient
import os
import requests
from sns_new_trial import SNS

# Create the Flask application object.
app = Flask(__name__,
            static_url_path='/',
            static_folder='static/class-ui/',
            template_folder='web/templates')

# CORS(app)
cors = CORS(app, resources={r'/api/*':{'origins':'*'}})

# Google OAuth
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.before_request
def before_decorator():
    print('Before request I should do...')
    # Verify it is an admin or a user
    print(request.form)
    print(request.values)
    print(request.url)
    print(request.url_rule)
    print(request.data)
    if str(request.url_rule)[:11] == "/api/admin/":
        if not CBSresource.if_admin(int(request.data)):
            raise NameError('You are not an admin')

@app.after_request
def after_decorator(rsp):
    print('After request I should do...')
    print(rsp.data)
    return rsp

@app.route("/api/user/<id>", methods=["GET"])
def get_user_by_id(id):

    result = CBSresource.get_user_by_key(id)

    if result:
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response("NOT FOUND", status=404, content_type="text/plain")

    print(result)
    return rsp

@app.route("/api/login", methods=["GET"])
def login():
    print('login 1')
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    print(authorization_endpoint)

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    print(request_uri)
    print(request.base_url + "/callback")
    rsp = Response(json.dumps({'request_uri' : request_uri}, cls=DTEncoder), status=200, content_type="application.json")
    return rsp

@app.route("/api/login/callback", methods=["GET", "POST"])
def callback():
    # Get authorization code Google sent back to you
    print('Begin callback')
    code = request.args.get("code")
    print('callback 1')
    print(code)
    print(request.url)
    print(request.base_url)

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    print(token_endpoint)
    print('callback 2')
    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    print(token_url)
    print('callback 3')
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    print('callback 4')
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    print(userinfo_endpoint)
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    
    CBSresource.process_google_login(userinfo_response.json())
    rsp = Response(json.dumps(userinfo_response.json(), cls=DTEncoder), status=200, content_type="application.json")
    # Send user back to homepage
    # return Response(status = 204)
    response = make_response(redirect(os.environ.get("WEB_APP_URL")))
    response.set_cookie('cookie_msg_demo', 'gggg8888')

    return response


@app.route("/api/googlelogin", methods=["POST"])
def google_login():
    response = CBSresource.process_google_login(request.get_json())
    ## login set sns
    result = CBSresource.show_profile_by_email(request.json["email"], 1)
    email = result["data"][0]['email']
    id = result["data"][0]['userid']
    print(email)
    print(id)
    content = "You received a partner invitation, please check it on our web: "
    Topic_ARN = f'{os.environ.get("Topic_ARN")}{id}'
    created = False;
    for each in SNS.list_topics(SNS.sns_client, SNS.logger)['Topics']:
        if (Topic_ARN == each['TopicArn']):
            created = True

    if created == False:
        topic_mame = SNS.create_topic(SNS.sns_client, SNS.logger, str(id))
        response_2 = SNS.subscribe(SNS.sns_client, SNS.logger, Topic_ARN, "email", email)

    else:
        print(1)


    return response

@app.route("/api/setcookie", methods=["GET"])
def set_cookie():
    response = make_response(redirect("https://www.google.com"))
    response.set_cookie('COOKIE_MSG_DEMO', 'gggg8888')
    return response

@app.route("/api/setheader", methods=["GET"])
def set_header():
    response = Response()
    # response.headers["Deomo_header"] = "gggg7777"
    response.set_cookie('COOKIE_MSG_DEMO', 'gggg8888')
    return response

@app.route("/api/login/mostrecent", methods=["GET"])
def most_recent_user():
    if request.method == 'GET':
        result = CBSresource.get_most_recent_login()
        rsp = Response(json.dumps(result, cls=DTEncoder), status=200, content_type="application.json")
    else:
        rsp = Response("Methods not defined", status=404, content_type="text/plain")
    return rsp

@app.route("/api/searchprofile", methods=["POST"])
def show_search():
    result = CBSresource.show_profile_by_email(request.get_json()['email'], request.get_json()['number'])
    if result['success']:
        rsp = Response(json.dumps(result, default=str), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, default=str), status=404, content_type="application.json")
    return rsp

@app.route("/api/searchprofile2", methods=["POST"])
def show_search_2():
    result = CBSresource.show_profile_by_email_2(request.get_json()['email'])
    if result['success']:
        rsp = Response(json.dumps(result, default=str), status=200, content_type="application.json")
    else:
        rsp = Response(json.dumps(result, default=str), status=404, content_type="application.json")
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

@app.route("/api/session/approved/user/<userid>", methods=["GET"])
def get_approved_session_by_user(userid):

    result = CBSresource.get_approved_session_by_user(userid)
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

@app.route("/api/admin/session/approve/<sessionid>", methods=["POST"])
def waitlist_approve(sessionid):

    result = CBSresource.waitlist_approve(sessionid)
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

@app.route("/api/userprofile3/<userid>", methods=["GET"])
def show3(userid):
    result = CBSresource.show_profile3(userid)
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
                                          #  request.get_json()['email'],
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

