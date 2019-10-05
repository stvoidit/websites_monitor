from app import app, db
from models import Links, Websites, Users, ProjectsTitles, WorkerProfile
from flask import Flask, abort, request, flash, session, render_template, redirect, send_file, jsonify, url_for
from sqlalchemy.sql import func, or_, any_, case
import sqlalchemy.exc
from multiprocessing import Process
from report_builder import query_db
from flask_wtf.csrf import CSRFError, CSRF
import json
import csv
import re
from user_verify import login_required
import werkzeug
import os


@app.route("/calendar", methods=['GET', 'POST'])
@login_required(roles=['admin'])
def calendar():
    return render_template('calendar.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@login_required(roles=['admin'])
def index():
    table_stat = db.session.query(
        ProjectsTitles.name.label('Title'),
        func.sum(case([(Links.status == True, 1)], else_=0)).label(
            'Active'),
        func.sum(case([(Links.status == False, 1)], else_=0)).label('Remove'))\
        .join(Links, Links.title == ProjectsTitles.id, isouter=True)\
        .group_by(ProjectsTitles)\
        .order_by(ProjectsTitles.id).all()
    return render_template('index_stat.html', table_stat=table_stat)


@login_required(roles=['admin'])
@app.errorhandler(CSRFError)
def project_choise():
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    fb = create_engine(db.get_engine().url)
    Session = sessionmaker(bind=fb)
    s = Session()
    if request.method == 'GET':
        all_title = s.query(ProjectsTitles)\
            .filter(ProjectsTitles.status == True)\
            .order_by(ProjectsTitles.name).all()
        all_js = {x.name: x.id for x in all_title}
        return jsonify(all_js)
    if request.method == 'POST':
        title_id = request.form.get('choise_title', None)
        session['active_project'] = title_id
        s.query(Users).filter(Users.id == session['user_id']).update(
            dict(active_title=title_id))
        s.commit()
    return redirect(request.referrer)


@app.route('/remove_ajax', methods=['POST', 'GET'])
@login_required(roles=['admin'])
def remove_ajax():
    if request.method == 'POST':
        link_id = request.get_json()['link_id']
        Links.query.filter(Links.id == link_id)\
            .update(dict(status=False))
        db.session.commit()
    return jsonify({'status': 'ok'})


@app.route('/login', methods=['POST', 'GET'])
@app.errorhandler(CSRFError)
def login():
    if request.method == "POST":
        login = request.form['username']
        password = request.form['password']
        password = Users.password_generate(password)
        user_cheak = db.session.query(Users)\
            .filter(Users.username == login,
                    Users.password == password,
                    Users.status == True)\
            .one_or_none()
        if not user_cheak:
            flash('Неправильный логин или пароль')
            return redirect('/login')
        session['logged_in'] = True
        session['username'] = login
        session['user_id'] = user_cheak.id
        session['role'] = user_cheak.role
        session['active_project'] = user_cheak.active_title
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('login_screen.html')


@app.route('/logout')
@login_required(roles=['admin'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@login_required(roles=['admin'])
def user_profile():
    user_profile = WorkerProfile.query\
        .filter_by(user_id=session['user_id'])\
        .one_or_none()
    user = Users.query\
        .filter_by(id=session['user_id'])\
        .first_or_404()
    if request.method == 'POST':
        if request.form.get('change_profile', None):
            u_email = request.form.get('user_email', None)
            u_password = request.form.get('user_password', None)
            if len(u_password) < 5:
                flash(
                    '<p class="text-center">Слишком короткий пароль<br>Минимум 5 символов</p>', 'danger')
                return render_template('user_profile.html', user_profile=user_profile, user=user)
            u_password = Users.password_generate(u_password)
            Users.query.filter_by(id=user.id).update(
                dict(email=u_email, password=u_password))
            db.session.commit()
            flash(
                '<p class="text-center">Данные успешно обновлены</p>', 'success')

        else:
            w_email = request.form.get('worker_email', None).strip()
            w_passwrod = request.form.get('worker_password', None).strip()
            u_smtp_server = request.form.get('smtp_server', None).strip()
            u_smtp_port = int(request.form.get('smtp_port').strip())
            if user_profile:
                w_passwrod = WorkerProfile.password_generate(w_passwrod)
                try:
                    WorkerProfile.query\
                        .filter_by(id=user_profile.id)\
                        .update(dict(work_email=w_email,
                                     work_password_email=w_passwrod,
                                     smtp_server=u_smtp_server,
                                     smtp_port=u_smtp_port))
                    db.session.commit()
                    flash(
                        '<p class="text-center">Данные успешно обновлены</p>', 'success')
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()
                    flash(
                        '<p class="text-center">Должны быть заполнены все поля</p>', 'danger')
            else:
                wu = WorkerProfile(
                    user_id=session['user_id'],
                    work_email=w_email,
                    work_password_email=w_passwrod,
                    smtp_server=u_smtp_server,
                    smtp_port=u_smtp_port)
                db.session.add(wu)
                try:
                    db.session.commit()
                    flash(
                        '<p class="text-center">Данные успешно обновлены</p>', 'success')
                except sqlalchemy.exc.IntegrityError:
                    db.session.rollback()
                    flash(
                        '<p class="text-center">Должны быть заполнены все поля</p>', 'danger')
    return render_template('user_profile.html',
                           user_profile=user_profile,
                           user=user)


@app.route('/get_report')
@login_required(roles=['admin'])
def get_report():
    if url_for('project_links') in request.referrer:
        return query_db(projects=[session['active_project']])\
            .project_report()

    if request.args.get('website'):
        if url_for('website_configurate', website_id=request.args.get('website')) in request.referrer:
            website_id = request.args.get('website')
            return query_db(domains=[website_id])\
                .domain_report()

    if url_for('websites_table') in request.referrer:
        return query_db.websites_report()
