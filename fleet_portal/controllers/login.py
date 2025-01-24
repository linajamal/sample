from odoo.addons.web.controllers.home import Home as Home
import logging
from odoo import http
from odoo.http import content_disposition, Controller, request, route

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers import portal


_logger = logging.getLogger(__name__)

'''
class CustomAuthSignupHome(Home):

    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect='/portal', *args, **kw):
        response = super(CustomAuthSignupHome, self).web_login(redirect=redirect, *args, **kw)
        _logger.info('redirectttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
        _logger.info(response)
        _logger.info('redirectttttttttttttttttttttttttttttttttttttttttttttttttttttttt 2')
        _logger.info(redirect)
        _logger.info(request.params)
        if not redirect and request.params['login_success']:
            search_user = request.env['res.users'].browse(request.uid)
            domain = [('user_id', '=', search_user.id)]
            if search_user.has_group('base.group_user'):
                return response
            elif search_user.has_group('base.group_portal'):
                _logger.info('******************************************************** 3')
                redirect = '/portal'
            else:
                redirect = '/my'
            _logger.info('YYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY')
            _logger.info(redirect)
            return request.redirect(redirect)
        return response


class CustomerPortal(portal.CustomerPortal):
    """This class inherits controller portal"""
    def _prepare_home_portal_values(self, counters):
        """This function super the method and set count as none
        :param int counters: count of the product
        :param auth: The user must be authenticated and the current
        request will perform using the rights that the user was given.
        :param string type: HTTP Request and JSON Request,utilizing HTTP
        requests via the GET and POST methods. HTTP methods such as GET, POST,
        PUT, DELETE
        :return: values in counters
       """
        values = super()._prepare_home_portal_values(counters)
        if 'f_count' in counters:
            values['f_count'] = None
        return values
'''
class CustomerPortalinherit(CustomerPortal):


    def _prepare_home_portal_values(self, counters):
        """This function super the method and set count as none
        :param int counters: count of the product
        :param auth: The user must be authenticated and the current
        request will perform using the rights that the user was given.
        :param string type: HTTP Request and JSON Request,utilizing HTTP
        requests via the GET and POST methods. HTTP methods such as GET, POST,
        PUT, DELETE
        :return: values in counters
       """
        values = super()._prepare_home_portal_values(counters)
        if 'f_count' in counters:
            values['f_count'] = None
        return values

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })
        _logger.info('redirectttttttttttttttttttttttttttttttttttttttttttttttttttttttt my account')
        _logger.info(values)
        if post and request.httprequest.method == 'POST':
            if not partner.can_edit_vat():
                post['country_id'] = str(partner.country_id.id)

            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self._get_mandatory_fields()}
                values.update({key: post[key] for key in self._get_optional_fields() if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/portal')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'partner_can_edit_vat': partner.can_edit_vat(),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

