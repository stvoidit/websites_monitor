from app import app
import view
from blueprint_links import view_links
from blueprint_projects import view_projects
from blueprint_websites import view_websites

URL_LIST = [
    app.add_url_rule('/', view_func=view.index),
    app.add_url_rule('/project_choise', view_func=view.project_choise, methods=['GET', 'POST']),
    app.add_url_rule('/user_profile', view_func=view.user_profile, methods=['GET', 'POST']),

    # blueprint
    app.add_url_rule('/addlink/', view_func=view_links.add_links, methods=['POST', 'GET']),
    app.add_url_rule('/removelink/', view_func=view_links.remove_links, methods=['POST', 'GET']),
    # blueprint
    app.add_url_rule('/project/', view_func=view_projects.project_links, methods=['GET', 'POST']),
    app.add_url_rule('/project/add', view_func=view_projects.add_project, methods=['GET', 'POST']),
    app.add_url_rule('/project/reports', view_func=view_projects.report_templates, methods=['GET']),
    app.add_url_rule('/project/reports/change_template', view_func=view_projects.report_templates_change, methods=['GET', 'POST']),
    
    # blueprint
    app.add_url_rule('/websites/', view_func=view_websites.websites_table, methods=['GET', 'POST']),
    app.add_url_rule('/websites/page/<int:page>', view_func=view_websites.websites_table, methods=['GET']),
    app.add_url_rule('/websites/<int:website_id>', view_func=view_websites.website_configurate, methods=['GET', 'POST']),
    app.add_url_rule('/add_new_website/', view_func=view_websites.add_new_website, methods=['GET', 'POST']),

]
