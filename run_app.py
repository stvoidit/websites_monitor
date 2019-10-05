# -*- coding: utf-8 -*-
from app import app
import view
from flask_wtf.csrf import CSRFProtect
import urls


""" Blueprints """
from blueprint_links import view_links
from blueprint_projects import view_projects
from blueprint_websites import view_websites


app.register_blueprint(view_links.blueprint_links)
app.register_blueprint(view_projects.blueprint_projects)
app.register_blueprint(view_websites.blueprint_websites)

[url for url in urls.URL_LIST]

csrf = CSRFProtect()
csrf.init_app(app)
if __name__ == '__main__':
    """ gunicorn -c gunicorn_config.py ren_run:app & """
    app.run(debug=True, port=5050)
