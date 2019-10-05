from app import db
from models import Links, Websites, Users, ProjectsTitles, WorkerProfile
from flask import Flask, abort, request, flash, session, render_template, redirect, send_file, jsonify, url_for, Blueprint
from monitor2 import hosting_cheak
from flask_wtf.csrf import CSRFError, CSRF
import sqlalchemy.exc
from multiprocessing import Process
import re
from user_verify import login_required

blueprint_links = Blueprint('blueprint_links', __name__,
                            template_folder='templates_links')


@login_required(roles=['admin'])
def remove_links():
    remove_type = request.form.get('remove_type', None)
    if request.method == 'POST':
        links = request.form['links'].split('\r\n')
        clear_links = []
        [clear_links.append(x.strip()) if len(
            x) > 0 and x.startswith('http') else None for x in links]
        for link in clear_links:
            link_cheak = Links.query\
                .filter(Links.link == link,
                        Links.title == session['active_project'])\
                .one_or_none()
            if not link_cheak:
                flash(
                    'Ссылка не найдена (в проекте, либо в базе) - <a href="{0}">{0}</a>'.format(link), 'warning')
            else:
                if remove_type == 'update':
                    Links.query.filter(Links.id == link_cheak.id)\
                        .update(dict(status=False))
                    db.session.commit()
                    flash(
                        'Ссылка отмечена, что контент удален - <a href="{0}">{0}</a>'.format(link), 'success')
                if remove_type == 'remove':
                    Links.query.filter(Links.id == link_cheak.id).delete()
                    db.session.commit()
                    flash(
                        'Ссылка удалена - {}'.format(link), 'danger')
    return render_template('remove_links.html')


@login_required(roles=['admin'])
def add_links():
    if request.method == 'GET':
        return render_template('add_links.html')
    if request.method == 'POST':
        if not session['active_project']:
            flash('Не выбран проект для работы', 'danger')
            return render_template('add_links.html')
        links = request.form['links'].split('\r\n')
        clear_links = []
        [clear_links.append(x.strip()) if len(
            x) > 0 and x.startswith('http') else None for x in links]
        cheak_list = []
        for link in clear_links:
            domain = re.sub('http.?://', '',
                            link).replace('www.', '').split('/')[0]
            cheak_domain = Websites.query.filter(
                Websites.domain == domain).one_or_none()
            if not cheak_domain:
                cheak_domain = Websites(domain=domain)
                db.session.add(cheak_domain)
                db.session.commit()
                cheak_list.append(cheak_domain.id)
            try:
                link_cheak = Links.query\
                    .filter(Links.link == link,
                            Links.title == session['active_project'])\
                    .one_or_none()
                if not link_cheak:
                    db.session.add(
                        Links(link=link,
                              title=session['active_project'],
                              domain=cheak_domain.id,
                              user_added=session['user_id']))
                    db.session.commit()
                    flash(
                        'Ссылка добавлена - <a href="{0}">{0}</a>'.format(link), 'success')
                elif link_cheak.status == False:
                    flash(
                        'Ссылка снова активна - <a href="{0}">{0}</a>'.format(link), 'info')
                    Links.query.filter(Links.id == link_cheak.id).update(
                        dict(status=True))
                    db.session.commit()
                else:
                    flash(
                        'Ссылка уже есть - <a href="{0}">{0}</a>'.format(link), 'danger')
            except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
                db.session.rollback()
                flash(
                    'Ссылка уже есть - <a href="{0}">{0}</a>'.format(link), 'danger')
        if cheak_list:
            parsing = Process(target=hosting_cheak, args=(cheak_list,))
            parsing.start()
        return render_template('add_links.html'), 202
