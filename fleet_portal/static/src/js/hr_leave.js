odoo.define('hr_portal.portal_leave_request', function(require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.leavePortal = publicWidget.Widget.extend({
        selector:'.leave_portal',
        events: {
            'change select#holiday_status_id': '_onChangeLeaveType',
            'change input#date_from , input#date_to': '_onChangeDate',
            'submit': 'async _onSubmit',

        }, // end of events

        /**
        * @override
        */
        start: function () {
           var self = this;
           $("select").select2();
           return this._super.apply(this, arguments).then(function () {

           });
        }, // end of start

        _onChangeLeaveType: function(){
             var self = this;
             var holiday_status_id = $('#holiday_status_id').val();
             self._getBalance(holiday_status_id);
        }, //end of _onChangeLeaveType

         _onChangeDate: async function(){
            var self = this;
            var date_from = $('#date_from').val();
            var date_to = $('#date_to').val();
            var holiday_status_id =$('#holiday_status_id').val();
            if (date_from && date_to) {
                  self._date_validation(date_from,date_to);
                  }
            self._getDuration(date_from,date_to,holiday_status_id);
        }, //end of _onChangeDate
        _date_validation: async function(date_from, date_to){
               if ((Date.parse(date_from) > Date.parse(date_to))) {
                    var error = "End date should be greater than Start date";
                        $('.form-error').remove();
                 $('#error_div').append($('<p/>', {
                     class: 'alert alert-danger form-error',
                     text: _t("Error: "+ error ),
                 }));
                 $('#submit_leave').attr('disabled','disabled');
                }else{
                  $('#submit_leave').removeAttr('disabled');
                  $('.form-error').remove();
                }
        },

           _getDuration: async function (date_from, date_to, holiday_status_id) {
            var self = this;
            await this._rpc({
                    route: '/get_leave_duration',
                    params: {
                        date_from: date_from,
                        date_to: date_to,
                        holiday_status_id: holiday_status_id,
                    }}).then(function (data) {
                        // alert(data);
                        if (data) {
                        self.$('#duration').val(data);
                    }
                }); // end of then
        }, // end of _getDuration

         _getBalance: async function (holiday_status_id) {
            var self = this;
            await this._rpc({
                    route: '/get_leave_balance',
                    params: {
                        holiday_status_id: holiday_status_id,
                    }}).then(function (data) {
                        if (data) {
                        self.$('#current_balance').val(data);
                    }
                }); // end of then
        }, // end of _getDuration

         _form_data_validate: async function(ev){
            var self  = this;
            var error  = '';
            return error
         },
         _onSubmit: async function(ev) {
             ev.stopPropagation();
             ev.preventDefault();
             var error = await this._form_data_validate();
             var form = this.el;
             console.log(form);
             if (!error){
//                 form.submit();
                 HTMLFormElement.prototype.submit.call(form);
             } else {
                 $('.form-error').remove();
                 $('#error_div').append($('<p/>', {
                     class: 'alert alert-danger form-error',
                     text: _t("Error: "+ error ),
                 }));
             }
         }, // end of _onSubmit

//                }); // end of then

    }); // end of leavePortal

}); // end of define