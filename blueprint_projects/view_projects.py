from user_verify import login_required
from app import db
from models import Links, Websites, Users, ProjectsTitles, WorkerProfile
from flask import Flask, abort, request, flash, session, render_template, redirect, send_file, jsonify, url_for, Blueprint
from flask_wtf.csrf import CSRFError, CSRF
import sqlalchemy.exc
import re


blueprint_projects = Blueprint('blueprint_projects', __name__,
                               template_folder='templates_projects')


@login_required(roles=['admin'])
def project_links():
    active_title = ProjectsTitles.query\
        .filter(ProjectsTitles.id == session['active_project'])\
        .one_or_none()
    project_links_data = db.session.query(Links, Websites, ProjectsTitles)\
        .join(Websites, Websites.id == Links.domain)\
        .join(ProjectsTitles, ProjectsTitles.id == Links.title)\
        .filter(Links.status == True,
                ProjectsTitles.status == True,
                ProjectsTitles.id == session['active_project']).all()
    removed_links = db.session.query(Links, Websites, ProjectsTitles)\
        .join(Websites, Websites.id == Links.domain)\
        .join(ProjectsTitles, ProjectsTitles.id == Links.title)\
        .filter(Links.status == False,
                ProjectsTitles.status == True,
                ProjectsTitles.id == session['active_project']).all()
    if request.method == 'POST':
        del_project = request.form.get('del_project', None)
        if del_project:
            ProjectsTitles.query\
                .filter(ProjectsTitles.id == session['active_project']).delete()
            Users.query.filter(Users.id == session['user_id'])\
                .update(dict(active_title=None))
            session['active_project'] = None
            db.session.commit()
            active_title = None
    return render_template('project.html',
                           project_data=project_links_data,
                           active_title=active_title,
                           removed_links=removed_links)


@login_required(roles=['admin'])
def add_project():
    if request.method == 'POST':
        title_name = request.form.get('project_name').strip()
        db.session.add(ProjectsTitles(name=title_name))
        db.session.commit()
        flash('Проект добавлен', 'success')
        return render_template('add_project.html'), 201
    if request.method == 'GET':
        return render_template('add_project.html')


@login_required(roles=['admin'])
def report_templates_change():
    templ = ProjectsTitles.query\
        .filter_by(id=session['active_project'])\
        .first_or_404()
    if request.method == 'POST':
        text_notice = request.form.get('change_notice', None)
        title_notice = request.form.get('title_mail', None)
        if len(text_notice) == 0:
            text_notice = None
        if len(title_notice) == 0:
            title_notice = None
        ProjectsTitles.query.filter_by(id=templ.id)\
            .update(dict(reports_template=text_notice,
                         title_notice=title_notice))
        db.session.commit()
    return render_template('change_template.html',
                           text_notice=templ.reports_template,
                           title_notice=templ.title_notice)


@login_required(roles=['admin'])
def report_templates():
    active_title = ProjectsTitles.query\
        .filter_by(id=session['active_project'])\
        .first_or_404()
    if active_title.reports_template:
        mail = format(active_title.reports_template)
        title_n = format(active_title.title_notice)
        l = db.session.query(Websites, Links)\
            .join(Links, Links.domain == Websites.id)\
            .filter(Links.status == True,
                    Links.title == session['active_project']).all()
        w_l = {}
        for data in l:
            dom = data.Websites.domain
            try:
                dom_links = w_l[dom]['links']
                dom_links.append(data.Links.link)
                w_l[dom]['links'] = dom_links
            except KeyError:
                w_l[dom] = {
                    'links': [data.Links.link],
                    'mails': data.Websites.email,
                    'website_id': data.Websites.id,
                    'titlenotice': active_title.title_notice,
                }

            rep_mails = []
            for k in w_l:
                ind = {}
                links = '\n'.join(w_l[k]['links'])
                t_notice = title_n.format(website=k, project=active_title.name)
                text_m = mail.format(website=k, links=links,
                                     project=active_title.name)
                ind[k] = {
                    'notice_text': text_m,
                    'mails': w_l[k]['mails'],
                    'website_id': w_l[k]['website_id'],
                    'titlenotice': t_notice
                }
                rep_mails.append(ind)
    else:
        rep_mails = None
    return render_template('reports_template.html',
                           active_title=active_title,
                           reports=rep_mails)
