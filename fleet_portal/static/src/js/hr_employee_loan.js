odoo.define('hr_portal.portal_loan_request', function(require) {
    "use strict";

    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    var _t = core._t;

    publicWidget.registry.loanPortal = publicWidget.Widget.extend({
        selector:'.loan_portal',
        events: {
            'change input#loan_amount , input#installment': '_calMonthlyInstallment',
//            'submit': 'async _onSubmit',

        }, // end of events

        /**
        * @override
        */
        start: function () {
           var self = this;
           return this._super.apply(this, arguments).then(function () {

           });
        }, // end of start


         _calMonthlyInstallment: async function(){
            var self = this;
            var loan_amount = parseFloat(self.$('#loan_amount').val());
            var installment = parseFloat(self.$('#installment').val());
            if (loan_amount && installment) {
                    var amount = loan_amount/installment;
                    self.$('#installment_amount').val(amount);
                  }
        }, //end of _calMonthlyInstallment

    }); // end of loanPortal

}); // end of define