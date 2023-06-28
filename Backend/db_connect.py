from flask_sqlalchemy import SQLAlchemy

rds_db = SQLAlchemy()


class Meat(rds_db.Model):
    id = rds_db.Column(rds_db.String, primary_key=True) 
    email = rds_db.Column(rds_db.String, nullable=False) 
    saveTime = rds_db.Column(rds_db.String, nullable=False) 
    traceNumber = rds_db.Column(rds_db.String, nullable=False) 
    species = rds_db.Column(rds_db.String, nullable=False)
    l_division = rds_db.Column(rds_db.String, nullable=False)
    s_division = rds_db.Column(rds_db.String, nullable=False)
    gradeNm = rds_db.Column(rds_db.String, nullable=False)
    farmAddr = rds_db.Column(rds_db.String, nullable=False)
    butcheryPlaceNm = rds_db.Column(rds_db.String, nullable=False)
    butcheryYmd = rds_db.Column(rds_db.String, nullable=False)
    deepAging = rds_db.Column(rds_db.String, nullable=True)  # as JSON string
    fresh = rds_db.Column(rds_db.String, nullable=True)  # as JSON string
    heated = rds_db.Column(rds_db.String, nullable=True)  # as JSON string
    tongue = rds_db.Column(rds_db.String, nullable=True)  # as JSON string
    lab_data = rds_db.Column(rds_db.String, nullable=True)  # as JSON string


class User1(rds_db.Model):
    id = rds_db.Column(rds_db.String, primary_key=True)
    meatList = rds_db.Column(rds_db.String)
    lastLogin = rds_db.Column(rds_db.String)
    name = rds_db.Column(rds_db.String)
    company = rds_db.Column(rds_db.String)
    position = rds_db.Column(rds_db.String)


class User2(rds_db.Model):
    id = rds_db.Column(rds_db.String, primary_key=True)
    meatList = rds_db.Column(rds_db.String)
    lastLogin = rds_db.Column(rds_db.String)
    name = rds_db.Column(rds_db.String)
    company = rds_db.Column(rds_db.String)
    position = rds_db.Column(rds_db.String)
    revisionMeatList = rds_db.Column(rds_db.String)


class User3(rds_db.Model):
    id = rds_db.Column(rds_db.String, primary_key=True)
    lastLogin = rds_db.Column(rds_db.String)
    name = rds_db.Column(rds_db.String)
    company = rds_db.Column(rds_db.String)
    position = rds_db.Column(rds_db.String)
    pwd = rds_db.Column(rds_db.String) # 암호화 완료
