odoo.define('first_website.chrome', function (require) {
"use strict";

var chrome = require('vx_web_ui.chrome');
var gui = require('vx_web_ui.gui');
var models = require('first_website.models');
var core = require('web.core');
var _t = core._t;
var qweb = core.qweb;

var Chrome = chrome.Chrome.extend({
    init: function() {
        var self = this;
        this.module_name = odoo.session_info.module_name?odoo.session_info.module_name:_t('FistWebsite');
        document.title = this.module_name;
        this.module_code = odoo.session_info.module_code?odoo.session_info.module_code:'first_website';
        this._super(arguments[0],{});

        this.model = new models.EcomPickingModel(this.getSession(), {chrome:this});
        this.gui = new gui.Gui({model: this.model, chrome: this});
        this.gui.set_barcode_product_screen('first_website_main_screen');
        this.gui.set_startup_screen('first_website_main_screen');
        this.model.gui = this.gui;

        this.model.ready.done(function(){
            self.build_chrome();
            self.build_widgets();
            self.disable_rubberbanding();
            self.disable_backpace_back();
            self.ready.resolve();
            self.loading_hide();
            self.replace_crashmanager();
            self.model.db.set_order_type(self.module_code);
            self.$('#module_main').html(qweb.render('module_main_order_selection_tmpl'));
//            self.$('#order_selection').click(function () {
//                var list = [];
//                for (var i = 0; i < self.model.db.requests.length; i++) {
//                    var request = self.model.db.requests[i];
//                    list.push({
//                        'label': request['name'],
//                        'item': request['id']
//                    });
//                }
//                self.gui.show_popup('selection', {
//                    title: _t('Order selection'),
//                    list: list,
//                    button: 2, //BT_OK | BT_CANCEL
//                    confirm: function (item) {
//                        var data = {
//                                qty:0,
//                                picking_time:self.get_current_UTCtime(),
//                                note:item,
//                            };
//                        self.model.db.add_product_to_requestline(chosenRequestline,data);
//                        self.render_list();
//                    }
//                });
//            });
        }).fail(function(err){   // error when loading models data from the backend
            self.loading_error(err);
        });
    },
    onResize: function(){
        this._super.apply(this, arguments);
        var $win = $(window), width = $win.width();
        this.$('#detail_section .form-group').toggleClass('half-box', width >= 720);
    }
});

return {
    Chrome: Chrome
};
});