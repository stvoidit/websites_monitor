from user_verify import login_required
from app import db
from models import Links, Websites, Users, ProjectsTitles, WorkerProfile
from flask import Flask, abort, request, flash, session, render_template, redirect, send_file, jsonify, url_for, Blueprint
from flask_wtf.csrf import CSRFError, CSRF
import sqlalchemy.exc
import re
from sqlalchemy.sql import func, or_, any_, case
from monitor2 import hosting_cheak


blueprint_websites = Blueprint('blueprint_websites', __name__,
                               template_folder='templates_websites')


@login_required(roles=['admin'])
def websites_table(page=1):
    websites_data = db.session.query(Websites, func.count(Links.id))\
        .join(Links, Links.domain == Websites.id, isouter=True)\
        .group_by(Websites).order_by(Websites.created.asc())\
        .paginate(page, 50, True)
    if request.method == 'POST':
        search_website = request.form.get('search').strip().lower()
        if re.search(r'\w+', search_website):
            search_char = '%{}%'.format(search_website)
            WS = func.lower(getattr(Websites, 'domain')).like(search_char)
            HS = func.lower(getattr(Websites, 'hosting')).like(search_char)
            EM = func.lower(getattr(Websites, 'email')).like(search_char)
            IP = func.lower(getattr(Websites, 'ip')).like(search_char)
            search_params = [WS, HS, EM, IP]

            websites_data = db.session.query(Websites, func.count(Links.id))\
                .join(Links, Links.domain == Websites.id, isouter=True)\
                .filter(or_(*search_params))\
                .group_by(Websites)\
                .order_by(Websites.created.asc())\
                .paginate(page, 50, True)
        else:
            flash('Введены только пробелы', 'danger')
    return render_template('websites.html', websites_data=websites_data)


@login_required(roles=['admin'])
def website_configurate(website_id):
    website = db.session.query(Websites).filter(
        Websites.id == website_id).first_or_404()
    if request.method == 'POST':
        if request.form.get('recheak', None):
            hosting_cheak([website.id])
            flash('Данные сайта обновлены', 'info')
        else:
            host = request.form.get('hosting', None)
            ip_ = request.form.get('ip', None)
            email = request.form.get('email', None)
            active = request.form.get('active', None)
            if active:
                active = True
            else:
                active = False
            Websites.query.filter(Websites.id == website_id).update(
                dict(hosting=host, ip=ip_, email=email, status=active))
            db.session.commit()
            flash('Изменения сохранены', 'success')
            website = db.session.query(Websites).filter(
                Websites.id == website_id).first_or_404()
    return render_template('websites_config.html', website=website)


@login_required(roles=['admin'])
def add_new_website():
    if request.method == 'POST':
        form_data = request.form
        domain = form_data.get('website').strip()
        domain = re.sub('http.?://', '',
                        domain).replace('www.', '').split('/')[0]
        host = form_data.get('host').strip()
        site_ip = form_data.get('ip').strip()
        email = form_data.get('email').strip()

        add_website = Websites(
            domain=domain, hosting=host, ip=site_ip, email=email)
        try:
            db.session.add(add_website)
            db.session.commit()
            flash('Новый сайт - <b>{}</b> - успешно добавлен'.format(domain), 'success')
        except (sqlalchemy.exc.IntegrityError, sqlalchemy.exc.InvalidRequestError):
            db.session.rollback()
            flash('Сайт <b>{}</b> уже есть в списке'.format(domain), 'danger')
    return render_template('add_new_website.html')
