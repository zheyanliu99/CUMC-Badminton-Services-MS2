from flask import Flask, Response, request
from datetime import datetime
import json
from cbs_resource import CBSresource
from flask_cors import CORS

# Create the Flask application object.
app = Flask(__name__,
            static_url_path='/',
            static_folder='static/class-ui/',
            template_folder='web/templates')

# CORS(app)
cors = CORS(app, resources={r'/api/*':{'origins':'*'}})


@app.route("/api/students/<uni>", methods=["GET"])
def get_student_by_uni(uni):

    result = CBSresource.get_user_by_key(uni)

    if result:
        rsp = Response(json.dumps(result), status=200, content_type="application.json")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5011, debug=True)

