# -*- coding: utf-8 -*-

import base64
from odoo.http import content_disposition, Controller, request, route
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import calendar as cal
from odoo.exceptions import AccessError, MissingError, ValidationError
import pytz
from datetime import datetime
from dateutil.relativedelta import relativedelta
from babel.dates import format_datetime
from odoo.tools.misc import get_lang
from operator import itemgetter
from odoo.osv.expression import OR
from odoo.tools import groupby as groupbyelem
#from odoo.addons.http_routing.models.ir_http import slug
from odoo import http, _
import logging 
from odoo import fields
import urllib

import binascii

from odoo.fields import Command

_logger = logging.getLogger(__name__)



class ESSPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(ESSPortal, self)._prepare_portal_layout_values()
        return values

    def _get_appointment_slots(self, timezone, employee=None):
        """ Fetch available slots to book an appointment
            :param timezone: timezone string e.g.: 'Europe/Brussels' or 'Etc/GMT+1'
            :param employee: if set will only check available slots for this employee
            :returns: list of dicts (1 per month) containing available slots per day per week.
                      complex structure used to simplify rendering of template
        """
        requested_tz = pytz.timezone(timezone)
        last_day = requested_tz.fromutc(datetime.utcnow() + relativedelta(days=8))

        # Compute available slots (ordered)
        slots = []
        # Compute calendar rendering and inject available slots
        today = requested_tz.fromutc(datetime.utcnow())
        start = today
        month_dates_calendar = cal.Calendar(0).monthdatescalendar
        months = []
        while (start.year, start.month) <= (last_day.year, last_day.month):
            dates = month_dates_calendar(start.year, start.month)
            for week_index, week in enumerate(dates):
                for day_index, day in enumerate(week):
                    mute_cls = weekend_cls = today_cls = None
                    today_slots = []
                    if day.weekday() in (cal.SUNDAY, cal.SATURDAY):
                        weekend_cls = 'o_weekend'
                    if day == today.date() and day.month == today.month:
                        today_cls = 'o_today'
                    if day.month != start.month:
                        mute_cls = 'text-muted o_mute_day'
                    else:
                        # slots are ordered, so check all unprocessed slots from until > day
                        while slots and (slots[0][timezone][0].date() <= day):
                            if (slots[0][timezone][0].date() == day) and ('employee_id' in slots[0]):
                                today_slots.append({
                                    'employee_id': slots[0]['employee_id'].id,
                                    'datetime': slots[0][timezone][0].strftime('%Y-%m-%d %H:%M:%S'),
                                    'hours': slots[0][timezone][0].strftime('%H:%M')
                                })
                            slots.pop(0)
                    dates[week_index][day_index] = {
                        'day': day,
                        'slots': today_slots,
                        'mute_cls': mute_cls,
                        'weekend_cls': weekend_cls,
                        'today_cls': today_cls
                    }

            months.append({
                'month': format_datetime(start, 'MMMM Y', locale=get_lang(request.env).code),
                'weeks': dates
            })
            start = start + relativedelta(months=1)
        return months
    @route(['/portal'], type='http', auth='user', website=True)
    def dashboard(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        tameed_locations =[]
        #employee = request.env['hr.employee'].sudo().search([('user_id', '=', request.env.user.id)], limit=1)
        partner = request.env.user.partner_id
        fleets = request.env['fleet.vehicle'].search([
            ])
        ''' 
        if tameeds.line_ids and tameeds.line_ids.location_id:
            tameed_locations= tameeds.line_ids.mapped('location_id')
        fleet_locations = request.env['fleet.location'].search([])
        _logger.info('USerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr locations')
        _logger.info(fleet_locations)

        eq_count_wait_approve = request.env['equipment.count'].sudo().search([('state','=','send_to_contractor')])
        eq_count_today = request.env['equipment.count.location'].sudo().search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'equipment_count_id.tameed_customer_manager_id','=',request.env.user.partner_id.id
            ),('count_date', '>=', datetime.combine(fields.Date.today(), datetime.min.time())),
                               ('count_date', '<=', datetime.combine(fields.Date.today(), datetime.max.time()))])
        eq_count_install_today = request.env['equipment.count.location'].sudo().search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'equipment_count_id.tameed_customer_manager_id','=',request.env.user.partner_id.id
            ),('installation_date', '>=', datetime.combine(fields.Date.today(), datetime.min.time())),
                               ('installation_date', '<=', datetime.combine(fields.Date.today(), datetime.max.time()))])

        fleet_requests = request.env['fleet.vehicle'].search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'is_installation','=',False
            )])
        mr_wait_approve = request.env['fleet.vehicle'].search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'is_installation','=',False
            ),('state','=','contractor_approval')])
        mr_today = request.env['fleet.vehicle'].search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'is_installation','=',False
            ),('state','=','accepted'), ('visit_from_date', '>=', datetime.combine(fields.Date.today(), datetime.min.time())),
                               ('visit_from_date', '<=', datetime.combine(fields.Date.today(), datetime.max.time()))])
        _logger.info('Max time today MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
        _logger.info(datetime.combine(fields.Date.today(), datetime.max.time()))
        _logger.info(mr_today)
        installation_requests = request.env['fleet.vehicle'].search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'is_installation','=',True
            )])

        installs_wait_approve = request.env['fleet.vehicle'].search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'is_installation','=',True
            ), ('state','=','contractor_approval')])
        installs_today = request.env['fleet.vehicle'].search([(
            # stopped domain to get all request and only depends on record rules
            #'location_id', 'in',  tameed_locations
            'is_installation','=',True
            ), ('state','=','accepted'),('visit_from_date', '>=', datetime.combine(fields.Date.today(), datetime.min.time())),
                               ('visit_from_date', '<=', datetime.combine(fields.Date.today(), datetime.max.time()))])
        punishments = request.env['fleet.punishment'].search([])

        #loan_ids = request.env['hr.loan'].sudo().search([('employee_id', '=', employee.id), ('state', '=', 'approve')])
        #loans = sum(loan.total_amount for loan in loan_ids)
        user_type = 'internal' if request.env.user.has_group('base.group_user') else 'portal'
        #business_trip = request.env['business.trip'].sudo().search([('employee_id', '=', employee.id),
        #                                                            ('state', '=', 'approved')])
        #business_trip_amount = sum(business_trip.mapped('payment_amount'))
        timezon = request.session['context']['tz'] or request.session['timezone']
        #slots = self._get_appointment_slots(timezon,partner)
        _logger.info('USerrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrorrr partner')
        _logger.info(request.env.user)
        _logger.info(request.env.user.lang)
        '''
        qcontext = {
            'error': {},
            'error_message': [],
            'partner': partner,
            'portal': True,
            'page_name': 'portal_home',
            'user':request.env.user,
            #'employee': employee,
            'fleet_counts': len(fleets.mapped('id')),
            'fleets':fleets,
            #'mr_today':mr_today,
            #'installation_counts': len(installation_requests.mapped('id')),
            #'installs_wait_approve':installs_wait_approve.ids,
            #'installs_today':installs_today,
            #'tameeds_count': len(tameeds.mapped('id')),
            #'locations_count': len(tameed_locations),
            #'punishments_count': len(punishments.mapped('id')),
            #'requests': fleet_requests,
            #'installations':installation_requests,
            #'user_type': user_type,
            #'tameeds': tameeds,
            #'eq_count_wait_approve':len(eq_count_wait_approve.mapped('id')),
            #'eq_count_today':eq_count_today,
            #'eq_count_install_today':eq_count_install_today,
        }
        qcontext.update(values)
        _logger.info('partnererrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr partner')
        _logger.info(qcontext)
        response = request.render("fleet_portal.fleet_portal_home_home", qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @route(['/portal/partner/profile'], type='http', auth='user', website=True)
    def user_profile(self):
        values = {'partner':  request.env.user.partner_id,
                  'edit_mode': 1,
                  'page_name': 'profile',
                  'portal': True,
                  }

        response = request.render("fleet_portal.partner_profile_template", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response




class MaintancesData(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'fleet_count' in counters:
            domain, fleet_count = [], 0
            employee_id = self.get_employeess()
            fleet_count = request.env['fleet.vehicle'].sudo().search_count(domain)
            if not request.env.user._is_admin():
                #domain += [('location_id.customer_manager_id', '=', request.env.user.id)]
                # domain += [('owner_user_id', '=', request.env.user.id)]
                fleet_count = request.env['fleet.vehicle'].sudo().search_count(domain)
            if fleet_count < 1:
                fleet_count = 1
            values['fleet_count'] = fleet_count
        
        if 'm_count' in counters:
            fleet_count = request.env['fleet.vehicle'].sudo().search_count([])
            if not request.env.user._is_admin():
                domain=[]
                #domain += [('location_id.customer_manager_id', '=', request.env.user.id)]
                # domain += [('owner_user_id', '=', request.env.user.id)]
                fleet_count = request.env['fleet.vehicle'].sudo().search_count(domain)
            if fleet_count < 1:
                fleet_count = 1
            values['m_count'] = fleet_count
        
        return values

    @http.route(['/get/fleets', '/get/fleets/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_fleets(self, page=1, access_token=None, search=None, search_in='all', sortby=None, groupby='none',
                             **kw):
        values = self._prepare_portal_layout_values()
        fleet_obj = request.env['fleet.vehicle']
        domain, fleet_count, fleet_ids = [], 0, None
        fleets = request.env['fleet.vehicle'].sudo().search([])
        #if not request.env.user._is_admin():
            # domain += [('owner_user_id', '=', request.env.user.id)]
            #domain += [('location_id.customer_manager_id', '=', request.env.user.id)]

        searchbar_sortings = {
            'model': {'label': _('Model'), 'order': 'model_id asc'},
            'id': {'label': _('Newest'), 'order': 'id desc'},
            'state_id': {'label': _('Status'), 'order': 'state_id desc'},
        }
        
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'equipment_id': {'input': 'equipment_id', 'label': _('Search by Equipment')},
            'owner_user_id': {'input': 'owner_user_id', 'label': _('Search by Owner')},
            'schedule_date': {'input': 'schedule_date', 'label': _('Search by Date')},
            'name': {'input': 'name', 'label': _('Search By name')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state_id': {'input': 'state_id', 'label': _('Status')},
        }

        if not sortby:
            sortby = 'id'
        order = searchbar_sortings[sortby]['order']

        # count for pager
        #if employee_id:
        fleet_count = fleet_obj.search_count(domain)

        # search
        if search and search_in:
            _logger.info('IIIIIIIIIIIIIIIIIIIII ids 1 IIIIIIIIIIIIIIIIIIIIIIIIIIIII')
            _logger.info(search)
            _logger.info(search_in)
            search_domain = []
            '''
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            if search_in in ('equipment_id', 'all'):
                search_domain = OR([search_domain, [('equipment_id', 'ilike', search)]])
            if search_in in ('owner_user_id', 'all'):
                search_domain = OR([search_domain, [('owner_user_id', 'ilike', search)]])
            if search_in in ('schedule_date', 'all'):
                search_domain = OR([search_domain, [('schedule_date', 'like', search)]])
            if search_in in ('installs_wait_approve', 'all'):
                search_domain = OR([search_domain, [('is_installation','=',True
            ), ('state','=','contractor_approval')]])
            if search_in in ('requests_wait_approve', 'all'):
                _logger.info('BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB')
                search_domain = OR([search_domain, [('is_installation','=',False
            ), ('state','=','contractor_approval')]])
            domain += search_domain
        _logger.info('MMMMMMMMMMMMMMFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF')
        _logger.info(domain)
        '''
        pager = portal_pager(
            url="/get/fleets",
            total=fleet_count,
            page=page,
            url_args={'search_in': search_in, 'search': search},
            step=12
        )

        grouped_fleet = []
        # content according to pager and archive selected
        #if employee_id:
        fleet_ids = fleet_obj.search(domain, order=order, limit=12, offset=pager['offset'])
        #request.session['my_expense_history'] = fleet_ids.ids[:100]
        grouped_fleet = [fleet_ids]
        if groupby == 'stage_id':
            grouped_fleet = [fleet_obj.concat(*g) for k, g in
                                    groupbyelem(fleet_ids, itemgetter('state'))]
        _logger.info(fleet_ids)
        _logger.info(fleet_ids)

        values = {}
        values.update({
            'fleet_ids': fleets,
            'page_name': 'fleet',
            'fleet_count': fleet_count,
            'pager': pager,
            'portal':True,
            'default_url': '/get/fleet',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'user': request.env.user,
            'partner': request.env.user.partner_id,
            'search_in': search_in,
            'groupby': groupby,
            'grouped_fleet': grouped_fleet,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby
        })
        return request.render("fleet_portal.portal_fleets", values)

    def get_employeess(self):
        return request.env['fleet.vehicle'].sudo().search([])
    

    @http.route(['/get/maintenances', '/get/maintenances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_maintances(self, page=1, access_token=None, search=None, search_in='all', sortby=None, groupby='none',
                             **kw):
        values = self._prepare_portal_layout_values()
        fleet_services_obj = request.env['fleet.vehicle.log.services']
        domain, fleet_service_count, fleet_ids = [], 0, None
        fleet_servs = request.env['fleet.vehicle.log.services'].sudo().search([])
        

        searchbar_sortings = {
            'model': {'label': _('Model'), 'order': 'model_id asc'},
            'id': {'label': _('Newest'), 'order': 'id desc'},
            'state_id': {'label': _('Status'), 'order': 'state_id desc'},
        }
        
        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'vehicle_id': {'input': 'vehicle_id', 'label': _('Search by Vehicle')},
            #'owner_user_id': {'input': 'owner_user_id', 'label': _('Search by Owner')},
            'date': {'input': 'date', 'label': _('Search by Date')},
            'name': {'input': 'maintenance_id', 'label': _('Search By name')},
        }
        
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'state': {'input': 'custom_state', 'label': _('Status')},
        }

        if not sortby:
            sortby = 'id'
        order = searchbar_sortings[sortby]['order']

        # count for pager
        #if employee_id:
        fleet_service_count = fleet_services_obj.search_count(domain)
        # search
        if search and search_in:
            _logger.info('IIIIIIIIIIIIIIIIIIIII ids 1 IIIIIIIIIIIIIIIIIIIIIIIIIIIII')
            _logger.info(search)
            _logger.info(search_in)
            search_domain = []
            
        pager = portal_pager(
            url="/get/maintenances",
            total=fleet_service_count,
            page=page,
            url_args={'search_in': search_in, 'search': search},
            step=12
        )

        grouped_fleet_ser = []
        # content according to pager and archive selected
        #if employee_id:
        fleet_serv_ids = fleet_services_obj.search(domain, order=order, limit=12, offset=pager['offset'])
        #request.session['my_expense_history'] = fleet_ids.ids[:100]
        grouped_fleet_ser = [fleet_serv_ids]
        if groupby == 'state':
            grouped_fleet_ser = [fleet_services_obj.concat(*g) for k, g in
                                    groupbyelem(fleet_ids, itemgetter('state'))]
        _logger.info(fleet_serv_ids)
        _logger.info(fleet_serv_ids)

        values = {}
        values.update({
            'maintenance_ids': fleet_serv_ids,
            'page_name': 'fleet_ser',
            'fleet_count': fleet_service_count,
            'pager': pager,
            'portal':True,
            'default_url': '/get/maintenances',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'user': request.env.user,
            'partner': request.env.user.partner_id,
            'search_in': search_in,
            'groupby': groupby,
            'grouped_fleet': grouped_fleet_ser,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby
        })
        return request.render("fleet_portal.portal_maintenances", values)

    '''

    @route(['/update/fleet'], type='http', auth='public', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            #if not partner.can_edit_vat():
            #    post['country_id'] = str(partner.country_id.id)

            #error, error_message = self.details_form_validate(post)
            #values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                #values = {key: post[key] for key in self._get_mandatory_fields()}
                values.update({key: post[key] for key in self._get_optional_fields() if key in post})
                #for field in set(['country_id', 'state_id']) & set(values.keys()):
                #    try:
                #        values[field] = int(values[field])
                #    except:
                #        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                self.on_account_update(values, partner)
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')


        values.update({
            'partner': partner,
            #'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response

    '''
    

    # @http.route(['/student/form/update'], auth="user", website=True)
    # def Student_Update(self, **kw):
    #     if kw.get('record'):
    #         rec = kw.get('record')
    #         rec_id = http.request.env['fleet.vehicle'].sudo().search([('id', '=', rec)])
    #
    #         rec_id.write({
    #             'state': 'in_progress',
    #         })
    #
    #         return request.redirect("/fleet/%s" % (slug(rec_id)))

    '''

    def _add_attachments(self, rec_id=False):
        attachments = []
        _logger.info('KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK')
        _logger.info(request.params)
        if 'document' in request.params:

            #attached_files = request.httprequest.files.getlist('document')
            _logger.info(base64.b64encode(request.params['document']))
            _logger.info(attached_files)
            _logger.info('MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
            for attachment in attached_f/iles:
                attached_file = attachment.read()
                attachment = request.env['ir.attachment'].sudo().create({
                    'name': attachment.filename,
                    'res_model': 'fleet.vehicle',
                    'type': 'binary',
                    'datas': base64.encodestring(attached_file),
                    })
                attachments.append(attachment.id)
                _logger.info('LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL')
                _logger.info(attachments)
        return attachments

    
        

    @http.route('/fleet/form/update/<model("fleet.vehicle"):fleet>', auth="public", website=True)
    def fleet_Update(self, fleet,**kw):
        if kw.get('record'):
            #if kw.get('license_plate'):
            #    ddd = kw.get('license_plate').split('T')
            #    formated_date = ddd[0] + " " + ddd[1] + ':00'
            #else:
            #    formated_date = False
            rec = kw.get('record')
            rec_id = http.request.env['fleet.vehicle'].sudo().search([('id', '=', fleet.id)])
            #if kw.get('equipment_id'):
            #    e_id = kw.get('equipment_id')
            #else:
            #    e_id = False
            values={
                #'name': kw.get('name'),
                'license_plate': kw.get('license_plate'),
                #'equipment_id': int(e_id),
                #'owner_user_id': request.env.user.id,
                #'schedule_date': formated_date,

            }


            rec_id.sudo().write(values)

            return request.redirect("/request/%s" % request.env['ir.http']._slug(fleet))
            #return request.redirect('/get/fleets')
    '''

    @http.route(['/request/<model("fleet.vehicle"):record_id>'], type='http', auth="user", website=True)
    def form_view_edit(self, record_id, **post):
        # Fetch the record by its ID
        _logger.info('***************************************************************************************')
        _logger.info(record_id)
        _logger.info(post)
        record = request.env['fleet.vehicle'].sudo().browse(record_id)
        
        # Ensure the record exists
        if not record_id.exists():
            return request.redirect('/get/fleets')
        
        # Check if the logged-in user has access to this record (Optional: Add security logic)
        #if record.partner_id != request.env.user.partner_id:
        #    return request.redirect('/get/fleets')
        # If POST data is sent, process the form to update the record
        if post:
            #if post.get('add_attachment', False):
            #    file = post['add_attachment']
            #    self._create_and_upload_attach(record_id, file, file.filename)
            _logger.info({
                'name': post.get('license_plate'),
                'vehicle_serial_number': post.get('serial_no'),
                'vehicle_plate_word' : post.get('Plate_words'),
                'customer_signature': post.get('customer_signature'),
                'plate_image': post.get('image'),
                'plate_image_url' : post.get('url'),
                'barcode': post.get('barcode_id'),})
            # Update record based on form data
            record_id.sudo().write({
               'name': post.get('license_plate'),
                'vehicle_serial_number': post.get('serial_no'),
                'vehicle_plate_word' : post.get('Plate_words'),
                'customer_signature': post.get('customer_signature'),
                'plate_image': post.get('image'),
                'plate_image_url' : post.get('url'),
                'barcode': post.get('barcode_id'),})
            # Redirect to avoid resubmitting the form when refreshing
            return request.redirect('/request/%s' % record_id)
        
        # If it's a GET request, just render the form to view/edit the record
        values = {
            'fleet': record_id,
        }
        return request.render('fleet_portal.fleet_details_template', values)
    
    @http.route(['/request/service/<model("fleet.vehicle.log.services"):record_id>'], type='http', auth="user", website=True)
    def service_view_edit(self, record_id, **post):
        _logger.info('***************************************************************************************')
        _logger.info(record_id)
        _logger.info(post)
        
        if not record_id.exists():
            return request.redirect('/get/maintenances')
        
        # Check if the logged-in user has access to this record (Optional: Add security logic)
        #if record.partner_id != request.env.user.partner_id:
        #    return request.redirect('/get/fleets')
        # If POST data is sent, process the form to update the record
        if post:
            if post.get('request_status')=='technical_no_device_change':
                values={
                'request_status': post.get('request_status'),
                'vehicle_serial_number':post.get('vehicle_serial_number'),
                }
            elif post.get('request_status')=='technical_device_change':
                values= {
                'request_status': post.get('request_status'),
                'vehicle_serial_number':post.get('vehicle_serial_number'),
                'device_warranty_status': post.get('device_warranty_status'),
                'device_warranty_expiration_date': post.get('device_warranty_expiration_date'),
                'barcode':post.get('barcode'),
                }
            elif post.get('request_status')=='technical_sim_change':
                values= {
                'request_status': post.get('request_status'),
                'vehicle_serial_number':post.get('vehicle_serial_number'),
                'new_sim_code': post.get('new_sim_code'),
                'new_sim_serial_no': post.get('new_sim_serial_no'),
                }
            _logger.info(
                values)
            # Update record based on form data
            record_id.sudo().write(values)
            #record_id.sudo().action_submit()
            # Redirect to avoid resubmitting the form when refreshing
            return request.redirect('/request/service/%s' % record_id.id)
        
        # If it's a GET request, just render the form to view/edit the record
        values = {
            'service': record_id,
        }
        return request.render('fleet_portal.fleet_service_template', values)
    
    def _create_and_upload_attach(self, res_id, file, filename):
        attach= request.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file.read()),
            'res_model': 'fleet.vehicle',
            'res_id': res_id
        })
        _logger.info('NJNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
        _logger.info(request.env['ir.attachment'].sudo().create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(file.read()),
            'res_model': 'fleet.vehicle',
            'res_id': res_id
        }))
        return attach


    @http.route('/upload/vehicle/attachment/<model("fleet.vehicle"):fleet>', type='http', auth='public', website=True)
    def upload_attachment(self, fleet,**kw):
        #fleet = int(kw['fleet'])
        _logger.info('NJNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
        _logger.info(kw)
        if kw.get('add_attachment', False):
            file = kw['add_attachment']
            attach=self._create_and_upload_attach(fleet, file, file.filename)
            #fleet_id = request.env['fleet.vehicle'].sudo().search([('id','=',fleet)])
            if fleet and attach:
                fleet.write({'plate_image_attachment':[(4,attach)]})
                _logger.info('NJNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
                _logger.info(attach)
        return request.redirect('/request/%s' % fleet)
    
    @http.route(['/request/<int:fleet_id>/accept'], type='json', auth="public", website=True)
    def portal_quote_accept(self, fleet_id,
                             access_token=None, name=None, signature=None):
        # get from query string if not on json param
        #access_token = access_token or request.httprequest.args.get('access_token')
        #try:
        #    order_sudo = self._document_check_access('fleet.vehicle', fleet_id, access_token=access_token)
        #except (AccessError, MissingError):
        #    return {'error': _('Invalid order.')}

        #if not signature:
        #    return {'error': _('Signature is missing.')}
        fleet_id = request.env['fleet.vehicle'].sudo().search([('id','=',fleet_id)])
        try:
            _logger.info('KKKKKKKKKKKKKKKKKKKKKKKKKKKKLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL')
            _logger.info(signature)
            fleet_id.write({
                'customer_signature': signature,
            })
            request.env.cr.commit()
        except (TypeError, binascii.Error) as e:
            return {'error': _('Invalid signature data.')}

        return {
            'force_refresh': True,
            'redirect_url':'/request/%s' % fleet_id,
        }

'''
@http.route('/request/<model("fleet.vehicle"):fleet>/', auth='public', website=True)
    def work(self, fleet):
    
        return request.render('fleet_portal.fleet_details_template', {
            'fleet': fleet,
            #'formated_date': formated_date,
            #'formated_duration': formated_duration,
            'user': request.env.user,
            'partner': request.env.user.partner_id,
            #'spare_lines': request.env['spare.line'].sudo().search([('fleet_id','=',work.id)]),
            'portal':True,
            'error': {},
            'error_message': [],
        })
'''