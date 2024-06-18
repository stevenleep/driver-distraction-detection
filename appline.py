from flask import Flask, render_template, request, Response, jsonify
import os
import model
import id
import shutil
from http_response import ResponseObject
from database import OutcomeDatabase, UserDatabase
import global_label
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token
)

app = Flask(__name__, static_folder="static", template_folder="templates")

app.config["UPLOAD_FOLDER"] = "uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

app.config.setdefault("JWT_SECRET_KEY", "super")
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False # token never expires
jwt = JWTManager(app)

outcome_db = OutcomeDatabase()
user_db = UserDatabase()


@app.route("/")
@app.route("/index.html")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/signin.html")
@app.route("/signin")
def siginin():
    return render_template("signin.html")


@app.route("/app")
@app.route("/app.html")
def applications():
    return render_template("app.html")


# /upload endpoint to upload a file and save it to the server folder based on the file type
# multipart/form-data post request
@app.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    file = request.files.get("file")
    type = request.form.get("type")

    if not file or not type:
        return ResponseObject.bad_request(
            message="No file was uploaded in the request or the file format is incorrect."
        )

    # calculate the md5 hash of the file
    # this will be used as the file id to save the file in the server folder
    # and to retrieve the file later
    md5 = id.calc_file_hash(file)

    # folder path: uploads/<file_type>/<md5>
    root_upload_folder = app.config.get("UPLOAD_FOLDER")
    save_folder = os.path.join(root_upload_folder, type, md5)

    query_old_result = outcome_db.get(md5)
    if query_old_result:
        return ResponseObject.success(
            message="File already exists", data=query_old_result
        )

    # file_path: uploads/<file_type>/<md5>/<file_name>
    os.makedirs(save_folder, exist_ok=True)
    file_path = os.path.join(save_folder, file.filename)

    try:
        file.save(file_path)
        new_inserted_result = outcome_db.insert(
            filename=file.filename,
            path=file_path,
            type=type,
            md5=md5,
            save_path=save_folder,
        )
        return ResponseObject.success(data=new_inserted_result)
    except Exception:
        return ResponseObject.error()


@app.route("/query/<id>", methods=["GET"])
@jwt_required()
def query(id: str):
    return ResponseObject.success(data=outcome_db.get(id))


@app.route("/query_all", methods=["GET"])
@jwt_required()
def query_all():
    type = request.args.get("type") or None
    status = request.args.get("status") or None
    if type or status:
        return ResponseObject.success(data=outcome_db.get_all_with_type(type, status))
    return ResponseObject.success(data=outcome_db.get_all())


@app.route("/delete/<id>", methods=["DELETE"])
@jwt_required()
def delete(id: str):
    query_result = outcome_db.get(id)
    file_folder_path = query_result["save_path"]
    if os.path.exists(file_folder_path):
        try:
            shutil.rmtree(file_folder_path)
            outcome_db.delete(id)
            return ResponseObject.success(
                message="File with ID " + id + " has been deleted successfully"
            )
        except Exception:
            return ResponseObject.error(
                message="An error occurred while deleting the file"
            )
    else:
        return ResponseObject.bad_request(
            message="File with ID" + id + "does not exist"
        )


# /feed/<filetype>/<id> endpoint to stream the video file
# the video file is read frame by frame and sent to the client
# the client will display the video frame by frame in the browser
@app.route("/feed/<filetype>/<id>", methods=["GET"])
def video_feed(filetype, id):
    if not id or not filetype:
        return jsonify(
            ResponseObject.bad_request(message="Expected id and type do not exist")
        )

    query_result = outcome_db.get(id)
    if not query_result:
        return ResponseObject.bad_request(message="Expected id is error")

    file_folder_path = os.path.join(query_result["save_path"])
    if not os.path.exists(file_folder_path):
        return ResponseObject.bad_request(
            message="File with ID" + id + "does not exist"
        )

    files = os.listdir(file_folder_path)
    if not files:
        return ResponseObject.bad_request(
            message="No files found in the folder with ID" + id
        )

    target_file = files[0]
    file_path = os.path.join(file_folder_path, target_file)
    return Response(
        model.process_video(video_path=file_path),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/real_time_feed")
def real_time_feed():
    return Response(
        model.generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/current_label")
def current_label():
    return jsonify(label=global_label.getValue())


@app.route("/user/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return ResponseObject.bad_request(
            message="Username and password are required to login"
        )
    user = user_db.get(username=username)
    if not user:
        return ResponseObject.bad_request(message="User does not exist")
    if user["password"] != id.sha256(password):
        return ResponseObject.bad_request(message="Invalid password")
    access_token = create_access_token(identity=username)
    return ResponseObject.success(
        data={"access_token": "Bearer " + access_token, "username": username, "userId": user["id"]}
    )


@app.route("/user/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if not username or not password:
        return ResponseObject.bad_request(
            message="Username and password are required to register"
        )
    user = user_db.get(username=username)
    if user:
        return ResponseObject.bad_request(
            message="User with the username already exists"
        )
    password = id.sha256(password)
    user = user_db.insert(username=username, password=password)
    return ResponseObject.success(
        message="User registered successfully",
        data={"username": username, "userId": user["id"]},
    )


if __name__ == "__main__":
    app.run()
