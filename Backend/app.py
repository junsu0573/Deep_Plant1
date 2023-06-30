from flask import Flask, make_response  # Flask Server import
import os  # Port Number assignment
from apscheduler.schedulers.background import (
    BackgroundScheduler,
)  # Background running function
import firebase_connect  # Firebase Connect
import s3_connect  # S3 Connect
import keyId  # Key data in this Backend file
from flask_sqlalchemy import SQLAlchemy  # For implement RDS database in server
import db_config  # For implement RDS database in server
from db_connect import rds_db, Meat, User1, User2, User3  # RDS Connect
import json  # For Using Json files
from flask_login import login_user, logout_user, current_user, LoginManager  # For Login
from flask import Blueprint, request, jsonify  # For web request
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)  # For password hashing
import hashlib  # For password hashing
from datetime import datetime  # 시간 출력용
from flask import abort  # For data non existence
from flask import make_response  # For making response in flask
from werkzeug.exceptions import BadRequest  # For making Error response
from werkzeug.utils import secure_filename  # For checking file name from react page

"""
flask run --host=0.0.0.0 --port=8080
 ~/.pyenv/versions/deep_plant_backend/bin/python app.py
"""
UPDATE_IMAGE_FOLDER_PATH = "./update_images/"


class MyFlaskApp:
    def __init__(self, config):
        self.app = Flask(__name__)
        # 1. RDS Config
        self.config = config
        self.app.config["SQLALCHEMY_DATABASE_URI"] = self._create_sqlalchemy_uri()
        self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

        # Init RDS
        rds_db.init_app(self.app)
        with self.app.app_context():
            rds_db.create_all()  # This will create tables according to the models

        # 2. Firebase Config
        self.firestore_conn = firebase_connect.FireBase_()

        # 3. S3 Database Config
        self.s3_conn = s3_connect.S3Bucket(keyId.s3_folder_name)

        # 4. meat database 요청 Routing
        @self.app.route("/meat", methods=["GET"])  # 1. 전체 meat data 요청
        def get_meat_data():
            id = request.args.get("id")
            if id:
                return _make_response(
                    self._get_specific_meat_data(id), "http://localhost:3000"
                )
            else:
                return _make_response(self._get_meat_data(), "http://localhost:3000")

        @self.app.route("/meat/update", methods=["POST"])  # 3. 특정 육류 데이터 수정(db data만)
        def update_specific_meat_data():
            id = request.args.get("id")
            if id:
                return _make_response(
                    self._update_specific_meat_data(id), "http://localhost:3000"
                )
            else:
                abort(400, description="No id Provided for update data")

        @self.app.route("/meat/upload_image", methods=["POST"])  # 4. 특정 육류 이미지 데이터 수정
        def update_specific_meat_image():
            id = request.args.get("id")
            if id:
                return _make_response(
                    self._update_specific_meat_image(id), "http://localhost:3000"
                )
            else:
                abort(400, description="No id Provided for upload image")

        # 5. user database 요청 Routiong
        @self.app.route("/user", methods=["GET"])  # 1. 특정 유저 id의 유저 정보 요청
        def get_specific_user_data():
            id = request.args.get("id")
            if id:
                return _make_response(
                    self._get_specific_user_data(id), "http://localhost:3000"
                )
            else:
                abort(400, description="No id Provided for Update User information")

        @self.app.route("/user_update", method=["POST"])
        def update_specific_user_data():
            id = request.args.get("id")
            if id:
                return _make_response(
                    self._update_specific_user_data(id), "http://localhost:3000"
                )
            else:
                abort(400, description="No id Provided for Update User information")

    def transfer_data_to_rds(self):
        print("Trasfer DB Data [flask server -> RDS Database]", datetime.now(), "\n")
        """
        Flask server -> RDS
        Firebase에서 새로 저장된 데이터들은 각각 다음의 변수에 저장됩니다.
        self.firestore_conn.temp_user1_data <= user1 database
        self.firestore_conn.temp_user2_data <= user2 database
        self.firestore_conn.temp_user3_data <= user3 database
        self.firestore_conn.temp_meat_data <= meat database
        """
        # 1. Update Meat data to RDS
        meat_data = self.firestore_conn.temp_meat_data
        user1_data = self.firestore_conn.temp_user1_data
        user2_data = self.firestore_conn.temp_user2_data
        user3_data = self.firestore_conn.temp_user3_data

        with self.app.app_context():
            for key, value in meat_data.items():
                try:
                    meat = Meat(
                        id=key,
                        email=value.get("email"),
                        saveTime=value.get("saveTime"),
                        traceNumber=value.get("traceNumber"),
                        species=value.get("species"),
                        l_division=value.get("l_division"),
                        s_division=value.get("s_division"),
                        gradeNm=value.get("gradeNm"),
                        farmAddr=value.get("farmAddr"),
                        butcheryPlaceNm=value.get("butcheryPlaceNm"),
                        butcheryYmd=value.get("butcheryYmd"),
                        deepAging=value.get("deepAging"),
                        fresh=value.get("fresh"),
                        heated=value.get("heated"),
                        tongue=value.get("tongue"),
                        lab_data=value.get("lab_data"),
                    )
                    rds_db.session.merge(meat)
                    print(f"Meat data added: {key} : {value}\n")
                except Exception as e:
                    print(f"Error adding meat data: {e}\n")

            # 2. Update User1 data to RDS

            for key, value in user1_data.items():
                try:
                    user = User1(
                        id=key,
                        meatList=value.get("meatList"),
                        lastLogin=value.get("lastLogin"),
                        name=value.get("name"),
                        company=value.get("company"),
                        position=value.get("position"),
                    )
                    rds_db.session.add(user)

                    print(f"User1 data added: {key} : {value}\n")
                except Exception as e:
                    print(f"Error adding User1 data: {e}\n")

            # 3. Update User2 data to RDS

            for data in user2_data.items():
                try:
                    user = User2(
                        id=key,
                        meatList=data.get("meatList"),
                        lastLogin=data.get("lastLogin"),
                        name=data.get("name"),
                        company=data.get("company"),
                        position=data.get("position"),
                        revisionMeatList=data.get("revisionMeatList"),
                    )
                    rds_db.session.merge(user)

                    print(f"User2 data added: {key} : {value}\n")
                except Exception as e:
                    print(f"Error adding User2 data: {e}\n")

            # 4. Update User3 data to RDS

            for key, value in user3_data.items():
                try:
                    user = User3(
                        id=key,
                        lastLogin=value.get("lastLogin"),
                        name=value.get("name"),
                        company=value.get("company"),
                        position=value.get("position"),
                        pwd=value.get("password"),
                    )
                    rds_db.session.merge(user)

                    print(f"User3 data added: {key} : {value}\n")
                except Exception as e:
                    print(f"Error adding User3 data: {e}\n")

            # 5. Session commit 완료
            rds_db.session.commit()
        self.firestore_conn.temp_meat_data = {}
        self.firestore_conn.temp_user1_data = {}
        self.firestore_conn.temp_user2_data = {}
        self.firestore_conn.temp_user3_data = {}
        print(f"===============================================\n")

    def _get_meat_data(self):  # 전체 meat data 요청
        with self.app.app_context():
            meats = Meat.query.all()
            meat_list = []
            for meat in meats:
                meat_dict = self._to_dict(meat)
                for field in ["deepAging", "fresh", "heated", "tongue", "lab_data"]:
                    if field in meat_dict:
                        meat_dict[field] = json.loads(meat_dict[field])
                # imagePath field
                meat_dict[
                    "imagePath"
                ] = f"https://deep-plant-flask-server.s3.ap-northeast-2.amazonaws.com/meat_image/{meat_dict['id']}"
                meat_list.append(meat_dict)
            return jsonify(meat_list)

    def _get_specific_meat_data(self, id):  # 특정 관리번호 meat data 요청
        with self.app.app_context():
            meat = Meat.query.get(id)
            if meat is None:
                abort(404, description="No meat data found with the given ID")
            else:
                meat_dict = self._to_dict(meat)
                for field in ["deepAging", "fresh", "heated", "tongue", "lab_data"]:
                    if field in meat_dict:
                        meat_dict[field] = json.loads(meat_dict[field])
                # imagePath field
                meat_dict[
                    "imagePath"
                ] = f"https://deep-plant-flask-server.s3.ap-northeast-2.amazonaws.com/{self.s3_conn.folder}/{meat_dict['id']}"
                return jsonify(meat_dict)

    def _get_specific_user_data(self, id):  # 특정 유저 id의 유저 정보 요청
        with self.app.app_context():
            # 1. Fetch
            user1_data = User1.query.filter_by(id=id).first()
            user2_data = User2.query.filter_by(id=id).first()
            user3_data = User3.query.filter_by(id=id).first()

            # 2. Init
            result = {}

            # 3. add
            if user1_data:
                result["user1_data"] = self._to_dict(user1_data)

            if user2_data:
                result["user2_data"] = self._to_dict(user2_data)

            if user3_data:
                result["user3_data"] = self._to_dict(user3_data)

            return jsonify(result)

    def _update_specific_meat_data(self, id):  # 특정 육류 데이터 수정(db data만)
        if not request.json:
            abort(400, description="No data sent for update")

        update_data = request.json

        with self.app.app_context():
            meat = Meat.query.get(id)

            if meat is None:
                abort(404, description="No meat data found with the given ID")

            # Update RDS
            for field, new_value in update_data.items():
                if hasattr(meat, field):
                    setattr(meat, field, new_value)
                else:
                    raise BadRequest(f"Field '{field}' not in Meat")

            rds_db.session.commit()

            return jsonify(self._to_dict(meat))

    def _update_specific_meat_image(self, id):  # 특정 육류 이미지 데이터 수정
        # Axios 라이브러리 post을 이용해 저장한 파일을 첨부했을 경우에 이용되는 API
        # 1. 파일이 없을 경우
        if "file" not in request.files:
            abort(400, description="No file part")

        file = request.files["file"]

        # 2. 파일 확인
        if file.filename == "":
            abort(400, description="No file selected for uploading")

        if file:
            # 1. Flask local server에 저장
            filename = secure_filename(f"{id}.png")
            file.save(os.path.join(UPDATE_IMAGE_FOLDER_PATH, filename))

            # 2. S3에 저장
            s3_file = f"{id}.png"
            self.s3_conn.put_object(
                self.s3_conn.bucket,
                os.path.join(UPDATE_IMAGE_FOLDER_PATH, filename),
                f"{self.s3_conn.folder}/{s3_file}",
            )

        else:
            abort(400, description="Invalid file type, Only PNG files are allowed.")

    def _update_specific_user_data(self, id):
        pass

    def _to_dict(self, obj):  # ditionary 생성 function
        return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

    def _create_sqlalchemy_uri(self):  # uri 생성
        aws_db = self.config["aws_db"]
        return f"postgresql://{aws_db['user']}:{aws_db['password']}@{aws_db['host']}:{aws_db['port']}/{aws_db['database']}"

    def run(self, host="0.0.0.0", port=8080):  # server 구동
        self.app.run(host=host, port=port)


def _make_response(data, url):  # For making response
    response = make_response(data)
    response.headers["Access-Control-Allow-Origin"] = url
    return response


# Init RDS
myApp = MyFlaskApp(db_config.config)

# 1. Login/Register Routing
login_manager = LoginManager()
login_manager.init_app(myApp.app)


@login_manager.user_loader
def load_user(user_id):
    return User3.query.get(user_id)


@myApp.app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    hashed_password = hashlib.sha256(
        data["password"].encode()
    ).hexdigest()  # hash 화 후 저장
    user = User3(
        id=data["id"],
        name=data["name"],
        company=data["company"],
        position=data["position"],
        pwd=hashed_password,
    )
    rds_db.session.add(user)
    rds_db.session.commit()
    return jsonify({"message": "Registered successfully"}), 201


@myApp.app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User3.query.filter_by(id=data["id"]).first()
    if user and user.pwd == hashlib.sha256(data["password"].encode()).hexdigest():
        login_user(user)
        return jsonify({"message": "Logged in successfully"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@myApp.app.route("/logout", methods=["GET"])
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


# 3. user(1,2,3) database 요청 Routing


# Server 구동
if __name__ == "__main__":
    # 1. Background Fetch Data (FireStore -> Flask Server) , 30sec 주기
    scheduler = BackgroundScheduler(daemon=True, timezone="Asia/Seoul")
    scheduler.add_job(
        myApp.firestore_conn.transferDbData, "interval", minutes=0.5
    )  # 주기적 데이터 전송 firebase -> flask server

    # 2. Send data to S3 storage (Flask server(images folder) -> S3), 30sec
    scheduler.add_job(
        myApp.s3_conn.transferImageData, "interval", minutes=0.6
    )  # 주기적 이미지 데이터 전송 flask server -> S3

    # 3. Send data to RDS (FireStore -> RDS), 30sec
    scheduler.add_job(
        myApp.transfer_data_to_rds, "interval", minutes=0.7
    )  # 주기적 Json Data 전송 flask server -> RDS
    scheduler.start()

    # 3. Flask 서버 실행

    myApp.run()
