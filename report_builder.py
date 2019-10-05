import pandas as pd
from app import db
from models import Websites, ProjectsTitles, Links
import json
import uuid
from flask import send_file, flash, redirect, request
from datetime import datetime, timedelta
from sqlalchemy import or_, any_


class query_db():
    def __init__(self, domains=None, projects=None):
        self.funcs = []
        if domains:
            websites = getattr(Websites, 'id').in_(domains)
            self.funcs.append(websites)
        if projects:
            projects = getattr(ProjectsTitles, 'id').in_(projects)
            self.funcs.append(projects)

    def project_report(self):
        query = db.session.query(ProjectsTitles.name,
                                 Websites.domain,
                                 Links.link,
                                 Links.status,
                                 Links.created)\
            .join(Links, Links.title == ProjectsTitles.id)\
            .join(Websites, Links.domain == Websites.id)\
            .filter(or_(*self.funcs))
        df = pd.read_sql(query.statement, db.session.bind)
        return query_db.df_to_excet_senf_file(df)

    def domain_report(self):
        query = db.session.query(ProjectsTitles.name,
                                 Websites.hosting,
                                 Websites.email,
                                 Websites.domain,
                                 Links.link,
                                 Links.status,
                                 Links.created)\
            .join(Links, Links.title == ProjectsTitles.id)\
            .join(Websites, Links.domain == Websites.id)\
            .filter(or_(*self.funcs))
        df = pd.read_sql(query.statement, db.session.bind)
        return query_db.df_to_excet_senf_file(df)

    def websites_report():
        """Передача параметров не требуется """
        query = db.session.query(Websites).filter(Websites.status == True)
        df = pd.read_sql(query.statement, db.session.bind)
        return query_db.df_to_excet_senf_file(df=df)

    def df_to_excet_senf_file(df=None):
        if df.shape[0] > 0:
            df['created'] = df['created'].astype('datetime64[ns]')
            df['created'] = df['created'].apply(
                lambda x: x + timedelta(hours=3))

            filename = '{}.xlsx'.format(uuid.uuid4().hex)
            file = r'./reports/' + filename + '.xlsx'
            writer = pd.ExcelWriter(
                file, engine='xlsxwriter',
                date_format='DD.MM.YYYY',
                options={'strings_to_urls': False})
            df.to_excel(writer, sheet_name=str(
                datetime.now().date()), index=False)
            writer.save()
            return send_file(file, attachment_filename=filename,
                             cache_timeout=0,
                             as_attachment=True)
        else:
            flash('Нет данных для отчета', 'warning')
            return redirect(request.referrer or '/')
