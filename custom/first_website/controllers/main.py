# -*- coding: utf-8 -*-
import json
import logging

import werkzeug
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class Home(http.Controller):

    @http.route('/first_website', type='http', auth="user")
    def first_website(self, **kw):
        if not request.session.uid:
            return werkzeug.utils.redirect('/web/login', 303)
        if kw.get('redirect'):
            return werkzeug.utils.redirect(kw.get('redirect'), 303)

        info = request.env['ir.http'].session_info()
        if 'web_tours' in info:
            del info['web_tours']
        company = request.env['res.company'].browse([info['company_id']])
        info.update(dict(
            company_name=company.name,
            currency_id=company.currency_id.id,
        ))
        context = {
            'session_info': json.dumps(info)
        }
        return request.render('first_website.index', qcontext=context)