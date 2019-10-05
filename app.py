from flask import Flask
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import babel
import os
from config import Database


app = Flask(__name__)
app.config['SECRET_KEY'] = 'my\nsecret\nkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['CSRF_ENABLED'] = True
app.config['UPLOAD_FOLDER'] = os.path.join(__file__, 'upload_files')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql+psycopg2://{Database.login}:{Database.password}@{Database.host}:{Database.port}/app"


db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('dbmig', MigrateCommand)

try:
    from models import Users, Websites, ProjectsTitles, Links, WorkerProfile
    admin = Admin(app, name='Админка', url='/xxx_admin_xxx/',
                  template_mode='bootstrap3')
    admin.add_view(ModelView(Users, db.session, name='Пользователи'))
    admin.add_view(ModelView(WorkerProfile, db.session,
                             name='Настройки профиля'))
    admin.add_view(ModelView(Websites, db.session, name='Сайты'))
    admin.add_view(ModelView(ProjectsTitles, db.session, name='Проекты'))
    admin.add_view(ModelView(Links, db.session, name='Ссылки'))
except (NameError, ImportError):
    pass


def format_datetime(value, format='medium'):
    """ Формат дат для Jinja """
    if format == 'full':
        format = "EEEE, d MMMM y 'в' HH:mm"
    elif format == 'medium':
        format = "dd.MM.y HH:mm"
    return babel.dates.format_datetime(value, format)


app.jinja_env.filters['datetime'] = format_datetime
