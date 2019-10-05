from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from app import db, app
from datetime import datetime as dt
import hashlib
import jwt


class Users(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=True)
    role = db.Column(db.String(50), unique=False, nullable=False, default=None)
    status = db.Column(db.Boolean(), default=True)
    active_title = db.Column(db.Integer, db.ForeignKey(
        'projects_titles.id', ondelete="Set null", onupdate='Cascade'), nullable=True)

    def __init__(self, *args, **kwargs):
        super(Users, self).__init__(*args, **kwargs)
        self.create_password()

    def create_password(self):
        self.password = Users.password_generate(self.password)

    def password_generate(self):
        user_entered_password = str(self)
        db_password = user_entered_password + app.secret_key
        h = hashlib.md5(db_password.encode())
        return h.hexdigest()

    def __repr__(self):
        return '{}'.format(self.username)


class WorkerProfile(db.Model):
    __tablename__ = 'worker_profile'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        Users.id), unique=True, nullable=False)
    work_email = db.Column(db.String(100), unique=True, nullable=False)
    work_password_email = db.Column(
        db.String(), unique=False, nullable=False)
    smtp_server = db.Column(
        db.String(), unique=False, nullable=False)
    smtp_port = db.Column(
        db.Integer(), unique=False, nullable=False)
    can_send = db.Column(db.Boolean(), default=True)

    origin_user = relationship(Users)

    def __init__(self, *args, **kwargs):
        super(WorkerProfile, self).__init__(*args, **kwargs)
        self.create_password()

    def create_password(self):
        self.work_password_email = WorkerProfile.password_generate(
            self.work_password_email)

    def password_generate(self):
        user_entered_password = str(self)
        db_password = jwt.encode(
            {'password': user_entered_password}, app.secret_key, algorithm='HS256').decode()
        return db_password


class ProjectsTitles(db.Model):
    __tablename__ = 'projects_titles'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    status = db.Column(db.Boolean(), default=True)
    created = db.Column(db.DateTime(timezone=True), nullable=False,
                        server_default=func.now())
    title_notice = db.Column(db.String())
    reports_template = db.Column(db.String())

    active_project = relationship(Users, backref=backref('projects_titles'))

    def __repr__(self):
        return '{}'.format(self.name)


class Websites(db.Model):
    __tablename__ = 'websites'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True,
                   nullable=False, autoincrement=True)
    domain = db.Column(db.String(100), nullable=False, unique=True)
    hosting = db.Column(db.String(250), nullable=True)
    ip = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean(), default=True)
    created = db.Column(db.DateTime(timezone=True), nullable=False,
                        server_default=func.now())

    def __repr__(self):
        return '{}'.format(self.domain)


class Links(db.Model):
    __tablename__ = 'links'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    domain = db.Column(db.Integer, db.ForeignKey(
        Websites.id, ondelete='Cascade', onupdate='Cascade'), nullable=False)
    title = db.Column(db.Integer(), db.ForeignKey(
        ProjectsTitles.id, ondelete='Cascade', onupdate='Cascade'))
    link = db.Column(db.String(), nullable=True, unique=False)
    created = db.Column(db.DateTime(timezone=True), nullable=False,
                        server_default=func.now())
    last_modified = db.Column(
        db.DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    status = db.Column(db.Boolean(), default=True)
    send_notice = db.Column(db.Boolean(), nullable=True,
                            default=False, server_default='false')
    report_count = db.Column(db.Integer, nullable=True,
                             server_default='0', default=0)
    user_added = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=True)

    origin_host = relationship(Websites)
    project = relationship(ProjectsTitles)
    adduser = relationship(Users)

    def __repr__(self):
        return '{} {} {}'.format(self.origin_host, self.project, self.link)


if __name__ == "__main__":
    # db.create_all()
    admin = Users(
        username="Admin",
        password="Admin",
        role="admin"
    )
    db.session.add(admin)
    db.session.commit()
