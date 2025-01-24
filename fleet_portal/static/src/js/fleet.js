/** @odoo-module **/

import publicWidget from '@web/legacy/js/public/public_widget';
import { rpc } from "@web/core/network/rpc";

publicWidget.registry.form = publicWidget.Widget.extend({
    selector: '.add_attachments',
    events: {
        'click #chooseFile': 'chooseFile',
        'change .add_attachment': 'onchange_attachment',
    },
    async onchange_attachment(e) {
          var self = this;
          var targetID = e.target.id;
          var attachment = e.target.files[0];
          if(attachment){
               $('input[type="submit"]').click()
          }
    },
    chooseFile: function(){
        $('input[name="add_attachment"]').click()
    }
});