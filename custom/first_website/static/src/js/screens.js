odoo.define('first_website.screens', function (require) {
"use strict";

var screens = require('vx_web_ui.screens');
var gui = require('vx_web_ui.gui');
var core = require('web.core');
var rpc = require('web.rpc');

var qweb = core.qweb;
var _t = core._t;

var MainScreenWidget = screens.ScreenWidget.extend({
    template: 'main_screen_first_website_tmpl',
    current_product: null,
    current_request:null,
    lock: false,

    onClickEnableCompression: function(){
      var self = this;
      if (!self.model.db.compress_local_storage) {
        self.gui.show_popup('general', {
          title: _t('Confirm'),
          html: _t('Do you want to enable compression?'),
          button: 3, //BT_OK | BT_CANCEL
          buttonText: {ok: _t('Yes')},
          confirm: function () {
            self.$('#enable-compression').hide();
            self.$('#disable-compression').show();
            self.model.db.set_local_storage_compression(true);
          }
        });
      }
    },
    onClickDisableCompression: function(){
      var self = this;
      if (self.model.db.compress_local_storage) {
        self.gui.show_popup('general', {
          title: _t('Warning'),
          html: _t('Disabling compression may causes exceeding storage limit error.' +
            '<br>Do you want to disabling compression?'),
          button: 3, //BT_OK | BT_CANCEL
          buttonText: {ok: _t('Yes')},
          confirm: function () {
            self.$('#enable-compression').show();
            self.$('#disable-compression').hide();
            self.model.db.set_local_storage_compression(false)
          }
        });
      }
    },
    onClickShowStorageInfo: function(){
      var self = this;
      self.gui.show_popup('general', {
        title: _t('Storage Info'),
        html: _t('You are using <b>' + self.model.db.getLocalStorageSize() + 'MB</b> of local storage.' +
                 '<br>Storage UTF-16 encoding ' + ($.browser.webkit ? '<b>is supported</b>.' : '<b>is not supported</b>.') +
                 '<br>Service Worker ' + ('serviceWorker' in navigator ? '<b>is available</b>.' : '<b>is not available</b>.')),
        button: 3, //BT_OK | BT_CANCEL
        buttonText: {ok: _t('Yes')},
        confirm: function () {
        }
      });
    },
    start: function(){
        var self = this, db = self.model.db;
        self.$('input[name="expired_minute"]').on('change', function () {
            self.model.stock_expire = $(this).val();
        });
        self.$('#submit_list').click(function () {
            var warning_message = "";
            if(self.current_request){
                var requestlines = self.model.db.get_requestline_by_request_id(self.current_request);
                var not_stocktaking_count=0,i;
                for (i in requestlines){
                    if(!requestlines[i].is_picked){
                        warning_message += "<div class='text-danger'>- Item has not been picked: [" + requestlines[i].product_code + '] ' + requestlines[i].product_name + "</div>";
                    } else {
                        if (requestlines[i].product_qty == 0 && requestlines[i].replacement_details && !requestlines[i].replacement_data){
                            warning_message += "<div class='text-danger'>- Replacement is available for: [" + requestlines[i].product_code + '] ' + requestlines[i].product_name + "</div>";
                        }
                    }
                }

                if (warning_message != ''){
                    warning_message = "<div class='warning-box'>" + warning_message + "</div>";
                }
            }


            self.gui.show_popup('textinput', {
                title: _t('Confirm Submit'),
                html: warning_message + 'Please enter <span style="color: red;">your name*</span> to submit?',
                button: 3, //BT_OK | BT_CANCEL
                buttonText: {ok: _t('Confirm')},
                confirm: function(value){
                    if (!value){
                        self.gui.close_popup();
                        self.gui.show_popup('error', {
                            'title': 'Input Error',
                            'body': 'Your name is required',
                        });
                        return;
                    }

                    db.set_picking_user(value);
                    self.submit_list();
                }
            })
        });
        self.$('#real_qty').on('keypress',function(){
            setTimeout(function(){
                var real_qty=parseInt(self.$('#real_qty').val());
                var storage_qty=parseInt(self.$('#storage_qty').val());
                var product = self.current_product;
                if (real_qty >= 0 && storage_qty >= 0 && product){
                    var pack_size=product.pack_size;
                    self.$('#total_qty').text(storage_qty * pack_size + real_qty);
                } else {
                    self.$('#total_qty').text('0');
                }
            },70);
        })
        self.$('#reload_history').click(function () {
            var loaded=self.reload_history();
            loaded.then(function(){
                self.render_history_list();
            });
        });

        self.$('#stock_product_info_btn').click(function () {
            if (self.current_product) {
                self.onClickStockProductInfo(self.current_product, {
                    clear_detail: true,
                    popup: true
                });
            }
            self.$('#real_qty').blur();
        });

        self.$('#clear-button').click(function(){
            self.$('#query').val('').focus();
        });
        self.$('#find-button').click(function(){
            var query = self.$('#query').val();
            self.current_code = query;
            if (query.length < 3) return;
            var loaded = self.model.find_product(query);
            self.gui.show_popup('loading', {body: _t('Finding ')+query, cancel: function(){
                loaded.reject();
            }});
            loaded.then(function(){
                self.gui.close_popup();
                self.set_picking_product(0);
            }, function (err, reason) {
                self.chrome.loading_error(err, reason);
            });
            self.$('#query').blur();
        });
        self.$('#load-now').click(function(){
            self.model.load_all();
        });
        self.$('#deselect-request').on('click',function(ev){
            self.deselect_request(ev);
        });
        self.$('#reload-request').click(function(){
            var loaded=self.reload_request();
            loaded.then(function(){
                self.current_request=null;
                self.render_request_list();
                self.render_list();
                self.clear_current_product_info();
            });
        });
        self.$('#clear-cache').click(function(){
            var ids = self.model.db.clear_cache(), loaded=self.reload_request();
            self.model.wait_product_id = ids.concat(self.model.wait_product_id);
            //self.set_active_product(0);
            self.current_request=null;
            self.clear_current_product_info();
            if(self.chrome.module_code == 'eyepos_over_stock'
                || self.chrome.module_code == 'eyepos_under_stock'
                || self.chrome.module_code == 'eyepos_empty_shelve'){
                self.$('#tab_detail').click();
            } else {
                self.$('#tab_request_list').click();
            }
            loaded.then(function(){
                self.render_request_list();
                self.render_list();
            });
            self.update_waiting_count(self.model.get_waiting_count());
        });
        self.$('#qty_available_btn').click(function(){
            var product = self.model.get_product();
            if (!product) return;
            var loaded = self.model.find_product(parseInt(product.id), true);
            self.gui.show_popup('loading', {body: _t('Reloading product ')+product.code, cancel: function(){
                loaded.reject();
            }});
            loaded.then(function(){
                self.gui.close_popup();
                self.set_picking_product(0);
            }, function (err, reason) {
                self.chrome.loading_error(err, reason);
            });
        });
        self.$('#btn_calculator').click(function(){
            self.calculating_unit();
        });
        self.$('#btn_storage_calculator').click(function(){
            self.calculating_storage_unit();
        });
        self.$('#enable-compression').click(function () {
            self.onClickEnableCompression();
        });
        self.$('#disable-compression').click(function () {
            self.onClickDisableCompression();
        });
        if (self.model.db.compress_local_storage) {
            self.$('#enable-compression').hide();
        } else {
            self.$('#disable-compression').hide();
        }
        self.$('#show-storage-info').click(function () {
            self.onClickShowStorageInfo();
        });
        self.$('#reload-now').click(function () {
            self.onClickReloadApp();
        });
        self.render_request_list();
        self.render_list();
        self.update_waiting_count(self.model.get_waiting_count());

        var loaded=self.reload_history();
        loaded.then(function(){
            self.render_history_list();
        });

        return self._super();
    },
    onClickStockProductInfo: function (current_product, options) {
      var self = this;
      var product = self.current_product;
      if (!product || product.id < 0) return;
      var loaded;
      self.gui.show_popup('loading', {body: _t('Finding ')+product.code, cancel: function(){
            loaded.reject();
        }});
      loaded = rpc.query({
            model: 'product.product',
            method: 'search_stock_by_query',
            args: [product.id],
        }, self.rpc_config).then(function(result){
            if (result){
                self.gui.close_popup();
                if (result.grn_note){
                    result.grn_note = JSON.parse(result.grn_note);
                }
                if (!!options && options.popup){
                    self.gui.close_popup();
                    self.gui.show_popup('general', {
                        title: "[" + result.product_code + "]" + result.product_id[1],
                        html: qweb.render('popup_stock_product_info_ecompk_tmpl', {'stock_info': result}),
                        button: 1, //BT_OK | BT_CANCEL

                      }, function (err, reason) {
                        self.chrome.loading_error(err, reason);
                      });
                      return;
                }



                self.$('#stock_info_form').html(qweb.render('popup_stock_product_info_ecompk_tmpl',
                    {'stock_info': result,
                    'planogram_url': 'https://cz-epos.longdan.co.uk:18170/longdan_planogram/product_place?store_code=' + self.chrome.current_store_code + '&product_code=' + result.product_code + '&application=' + self.chrome.module_code + '&mini_iframe=True',
                    'product_image_url': 'https://cz-epos.longdan.co.uk:18170/longdan_image/product_image?product_code=' + result.product_code}));
                if (result.final_remain_qty > 5 && self.chrome.module_code == 'eyepos_empty_shelve'){
                    self.gui.show_popup('general', {
                        title: _t('Becareful with empty shelves list'),
                        html: _t('<b>Maybe</b> we have stock (<b>>=') + result.final_remain_qty + _t(' unit(s)</b>) at shop. Please <b>check stock to fill</b> the shelve. Just add to empty shelve list if this product can not be filled.</br>Thank you for your checking!'),
                        button: 1, //BT_OK | BT_CANCEL

                      }, function (err, reason) {
                        self.chrome.loading_error(err, reason);
                      });
                }

                if (result.product_tag_names){
                    for (var pos in result.product_tag_names){
                        var product_tag_name = result.product_tag_names[pos];
                        if (product_tag_name.name == 'Removed label'){
                            if (self.chrome.module_code == 'eyepos_empty_shelve'){
                                var $btn_add = self.$('#add-to-list');
                                $btn_add.attr('disabled', true).addClass('disabled');
                            }
                            self.gui.show_popup('general', {
                                title: _t('Removed label product'),
                                html: _t('This product is in the removed label list.'),
                                button: 1, //BT_OK | BT_CANCEL

                              }, function (err, reason) {
                                self.chrome.loading_error(err, reason);
                              });
                        }
                    }
                }
            } else {
                self.gui.close_popup();
                self.gui.show_popup('general', {
                    title: _t('Stock Product Information'),
                    html: 'No information about stock for this product',
                    button: 1, //BT_OK | BT_CANCEL

                  }, function (err, reason) {
                    self.chrome.loading_error(err, reason);
                  });
            }

        },function(err, reason){
            self.gui.show_popup('error', {
                'title': 'System Error',
                'body': reason.message,
            });
        });

    },
    update_waiting_count: function(count){
        this.$('#waiting_count').text(count);
        var $load = this.$('#load-now');
        if (count)
            $load.removeClass('disabled').css('disabled', false);
        else
            $load.addClass('disabled').css('disabled', true);
    },
    add_product_to_order: function(product, qty, note){
        var self=this,
            db = self.model.db;

        if(self.current_request){
            var requestline = self.check_product_in_request(product.id,self.current_request);
            if(requestline){
                var data = {
                        qty:qty,
                        picking_time:self.get_current_UTCtime(),
                        note:note,
                        pack_size:product.pack_size
                    };
                db.add_product_to_requestline(requestline,data);
                self.render_list();
            }else{
                self.gui.show_popup('error', {body: _t('This product doesn\'t exists in the Request list')});
            }
            return;
        }

        self.gui.show_popup('error', {body: _t('Order not found')});
    },
    add_replacement_product_to_order: function(product, qty, note, replacement_detail){
        var self=this,
            db = self.model.db;

        if(self.current_request){

            var data = {
                    replacement_detail: replacement_detail,
                    qty:qty,
                    picking_time:self.get_current_UTCtime(),
                    note:note,
                    pack_size:product.pack_size
                };
            db.add_replacement_product_to_requestline(replacement_detail,data);
            self.render_list();

            return;
        }

        self.gui.show_popup('error', {body: _t('Order not found')});
    },
    render_request_list: function(){
        var self = this,db = self.model.db,
            count = db.get_request_count(),
            $request_list=self.$('#request_list'),
            $list=self.$('#items_list'),
            requests = db.get_all_request();
        if(count){
            self.$('#request_count').text(count);
            $request_list.html(qweb.render('ecompk_request_list_tmpl', {requests: requests,current_request:self.current_request}));
//            self.$('.js_new_request').on('click',function(ev){
//                self.pick_new_request(ev);
//            });
            self.$('.js_request_change').on('click',function(ev){
                self.request_change(ev);
            });
        }else{
            self.$('#request_count').text(0);
            $request_list.html('No request from the office');
        }
    },
    render_history_list: function(){
        var self = this,db = self.model.db,
            count = db.get_history_count(),
            $history_list=self.$('#history_list'),
            histories = db.get_all_histories();
        if(count){
            self.$('#history_count').text(count);
            $history_list.html(qweb.render('ecompk_history_list_tmpl', {requests: histories}));
        }else{
            self.$('#history_count').text(0);
            $history_list.html('No history data');
        }
        self.$('.js_history_change').off('click').on('click',function(ev){
            self.history_change(ev);
        });
    },
    render_list: function(){
        var self = this, db = self.model.db,
            $list = self.$('#items_list'),
            $btn = self.$('#submit_list'),
            request='', requestlines='';
        if(self.current_request){
            request = db.get_request_by_id(self.current_request);
            requestlines = db.get_requestline_by_request_id(self.current_request);
            $('#lock_list input').each(function(){
                $(this).prop("checked", true);
            });
            $('#order_name').html(request.name);
        } else {
            self.$('#request_status').text('');
            self.$('#request_note').text('');
            self.$('#request_date').text('');
            self.$('#order_count').text('-');
            $list.html(qweb.render('ecompk_requestline_tmpl', {order:null,requestlines: []}));
        }
        if(request && requestlines){
            var count=db.get_requestline_count(self.current_request),
                picked_count= requestlines.filter(function(item){return item.is_picked;}).length;

            self.$('#request_status').text(request.name);
            if(request.note){
                self.$('#request_note').text(request.note);
            }else{
                self.$('#request_note').text('');
            }
            self.$('#request_date').text(moment(request.date_order).format('DD/MM/YYYY'));
            self.$('#order_count').text(picked_count+'/'+count);
            $list.html(qweb.render('ecompk_requestline_tmpl', {order:request,requestlines: requestlines}));
            self.$('.input_without_scan').on('click',function(ev){
                self.input_without_scan(ev);
            });

            if (self.chrome.module_code != 'eyepos_empty_shelve') {
                self.$('.badge').on('click',function(ev){
                    var $li = $(ev.target).closest('.list-group-item'),db=self.model.db;
                    var chosenRequestline = $li.data('requestline-id');
                    var line = db.get_requestline_by_id(chosenRequestline);
                    if (!line || !line.is_picked){
                        return;
                    }

                    self.gui.show_popup('general', {
                        title: _t('Edit Picking'),
                        html: qweb.render('edit_order_line_ecompk_tmpl', {line:line,order_info:db.get_order_info()}),
                        focus: '#popup-qty',
                        button: 3, //BT_OK | BT_CANCEL
                        buttonText: {ok: _t('Update')},
                        confirm: function(){
                            var new_qty = parseInt(this.$('#qty').val()), change = false,
                                new_note = this.$('#note').val().trim(),
                                new_storage_qty = parseInt(this.$('#storage_qty').val());
                            if (!isNaN(new_qty) && new_qty != qty) {
                                line.product_qty = new_qty;
                                change = true;
                            }
                            if (!isNaN(new_storage_qty) && new_storage_qty != storage_qty) {
                                line.storage_qty = new_storage_qty;
                                change = true;
                            }
                            if (new_note != line.note) {
                                line.note = new_note;
                                change = true;
                            }

                            if (change) {
                                self.render_list();
                            }
                        }
                    })
                });
            }
            self.$('.more_info_click_js').on('click',function(ev){
                self.more_info_click(ev);
            });
            $btn.attr('disabled', false).removeClass('disabled');
            return;
        }

        //  Do not select order
    },
    set_picking_product: function (msg, replacement_detail) {
        var self=this, product = self.model.get_product();
        self.current_product = product;
        if (product){
            if(self.current_request){
                if (replacement_detail){
                    self.gui.close_popup();
                    self.gui.show_popup('number', {
                        title: "Replacement Picking confirmation",
                        html: qweb.render('popup_picking_ecompk_tmpl', {'product': product, 'requestline': replacement_detail}),
                        button: 3, //BT_OK | BT_CANCEL
                        buttonText: {ok: _t('Confirm')},
                        label: "Pick quantity",
//                        value: requestline.product_qty ? requestline.product_qty: requestline.product_uom_qty,
                        confirm: function (value) {
                            self.add_replacement_product_to_order(product, value, null, replacement_detail)
                        }
                    }, function (err, reason) {
                        self.chrome.loading_error(err, reason);
                    });
                } else {
                    var requestline = self.get_product_in_request(product.id,self.current_request);
                    if(requestline){
                        self.gui.close_popup();
                        self.gui.show_popup('number', {
                            title: "Picking confirmation",
                            html: qweb.render('popup_picking_ecompk_tmpl', {'product': product, 'requestline': requestline}),
                            button: 3, //BT_OK | BT_CANCEL
                            buttonText: {ok: _t('Confirm')},
                            label: "Pick quantity",
    //                        value: requestline.product_qty ? requestline.product_qty: requestline.product_uom_qty,
                            confirm: function (value) {
                                self.add_product_to_order(product, value)
                            }
                        }, function (err, reason) {
                            self.chrome.loading_error(err, reason);
                        });
                    }else{
                        self.gui.show_popup('error', {body: _t('This product doesn\'t exists in the Request list')});
                    }
                }
            } else {
                self.gui.show_popup('general', {html: _t('Order not found')});
            }
        } else {
            self.gui.show_popup('general', {html: _t('Product not found')});
        }

        self.current_product = product;
    },
    submit_list: function(){
        var self = this, save;
        if(self.current_request){
            save = self.model.submit_request_to_backend(self.current_request);
        }else{
            self.gui.show_popup('error', {body: _t('Order not found')});
            return;
        }
        if (save) {
            self.gui.show_popup('loading', {body: _t('Request submitting')});
            save.then(function (result) {
                self.gui.close_popup();
                self.current_request=null;
                if (result){
                    if(result.succeed==true){
                        self.gui.show_popup('general', {body: _t(result.msg), confirm: function(){}});
                    }else{
                        self.gui.show_popup('error', {body: _t(result.msg), confirm: function(){}});
                    }
                }
                var loaded=self.reload_request();
                loaded.then(function(){
                    self.deselect_request();
                    self.render_request_list();
                    self.render_list();
                });
            }, function (err, reason) {
                self.chrome.loading_error(err, reason);
            });
        }
    },
    enter_barcode: function(barcode){
        if (!!barcode && barcode.indexOf("BIN")==0){
            $('#bin_name').html(barcode);
            return;
        }
        var self=this,
            // loaded = self.model.search_by_barcode(barcode);
            loaded = self.model.find_product(barcode, false);

        self.gui.show_popup('loading', {body: _t('Searching product by')+' '+barcode, cancel: function(){
            loaded.reject();
        }});
        loaded.then(function(){
            self.gui.close_popup();
            self.set_picking_product(false);
            self.$('#scanned_code').text(barcode);
        }, function (err, reason) {
            self.chrome.loading_error(err, reason);
        });
    },
    request_change: function(ev){
        var $li = $(ev.target).closest('.list-group-item'),self=this,db=self.model.db;
        var $ip=$li.find("input[name='request_id']");
        $ip.prop("checked", true);
        $('#new_request input:checked').each(function(){
            $(this).prop("checked", false);
        });
        self.current_request = $li.data('request-id');
        db.clear_order();
        self.render_list();
        self.clear_current_product_info();
        
        self.gui.show_popup('textinput', {
            title: _t('Confirm Start Picking'),
            html: 'Please enter <span style="color: red;">your name*</span> to start picking?',
            button: 3, //BT_OK | BT_CANCEL
            buttonText: {ok: _t('Confirm')},
            cancel: function(){
                self.deselect_request()
            },
            confirm: function(value){
                if (!value){
                    self.gui.close_popup();
                    self.gui.show_popup('error', {
                        'title': 'Input Error',
                        'body': 'Your name is required',
                    });
                    return;
                }

                rpc.query({
                    model: 'sale.order',
                    method: 'start_request',
                    args: [],
                    kwargs: {
                        request_id: self.current_request,
                        start_picking_user:value,
                    }
                }, this.rpc_config).then(function(result){
                    console.info(result);
                },function(err, reason){
                    console.info(err, reason);
                });

                db.set_start_picking_user(value);
                setTimeout(function(){self.$('#tab_list').click();}, 500);
            }
        })
    },
    history_change: function(ev){
        var $li = $(ev.target).closest('.list-group-item'),self=this,db=self.model.db;
        var history_id = $li.data('request-id');
        var history_name = $li.data('request-name');
        var current_history = _.find(db.histories, function (history) {return history.id == history_id})

        var loaded = new $.Deferred();
        self.model.load_history_detail(history_id).then(function(data){
            loaded.resolve();
            self.gui.show_popup('general', {
                title: history_name,
                html: qweb.render('ecompk_history_detail_tmpl', {request: current_history, request_lines:db.current_history_detail}),
                button: 1, //BT_OK | BT_CANCEL
                confirm: function(){

                }
            });
        });
    },
    cant_pick_action: function(ev){
        var $li = $(ev.target).closest('.list-group-item'),self=this,db=self.model.db;
        var chosenRequestline = $li.data('requestline-id'),requestline=db.get_requestline_by_id(chosenRequestline);
        self.gui.show_popup('web_ui_selection', {
            title: _t("Can't pick reason"),
            html: "<div><b class='text-danger'>Becareful!!! Request will be cancel if any product can't pick</b></div>",
            list: [{
                'label': 'Out of stock',
                'item':  'out_of_stock'
            }, {
                'label': 'Product expired',
                'item':  'expired'
            }, {
                'label': 'Not enough stock',
                'item':  'not_enough'
            }],
            button: 2, //BT_OK | BT_CANCEL
            confirm: function (item) {
                var data = {
                        qty:0,
                        picking_time:self.get_current_UTCtime(),
                        note:item,
                    };
                self.model.db.add_product_to_requestline(chosenRequestline,data);
                self.render_list();

                if (requestline.replacement_details && requestline.replacement_details.length > 0){
                    self.replace_pick_action(requestline)
                }

//                self.submit_list();
            }
        });
    },

    replace_pick_action: function(requestline){
        var self=this,db=self.model.db;
        var list = [];
        for (var pos in requestline.replacement_details){
            list.push({
                'label': requestline.replacement_details[pos].product_id[1],
                'item':  requestline.replacement_details[pos]
            })
        }
        self.gui.show_popup('web_ui_selection', {
            title: _t("Replacement picking"),
            html: "<div><b class='text-danger'>Becareful!!! You can choose one of products above for replace " + requestline.product_id[1] + "</b></div>",
            list: list,
            button: 2, //BT_OK | BT_CANCEL
            confirm: function (item) {
                self.input_replacement_product(requestline, item)
            }
        });
    },

    pick_new_request: function(ev){
        var self=this,db=self.model.db;

        $('#request_list_radio input:checked').each(function(){
            $(this).prop("checked", false);
        });
        self.current_request = null;
        self.lock = false;
        self.model.db.clear_order();
        self.render_list();
        self.clear_current_product_info();
    },
    check_product_in_request:function(product_id,request_id){
        var self = this,db=self.model.db,i,
            lines = db.get_requestline_by_request_id(self.current_request);
        for(i in lines){
            if(lines[i].product_id[0]==product_id){
                return lines[i].id;
            }
        }
        return false;
    },
    get_product_in_request:function(product_id,request_id){
        var self = this,db=self.model.db,i,
            lines = db.get_requestline_by_request_id(self.current_request);
        for(i in lines){
            if(lines[i].product_id[0]==product_id){
                return lines[i];
            }

            if(lines[i].product_id[0]==product_id){
                return lines[i];
            }
        }
        return false;
    },
    deselect_request: function(ev){
        var self=this,db=self.model.db;
        $('#request_list_radio input:checked').each(function(){
            $(this).prop("checked", false);
        });
        $('#order_name').html("No order");
        self.current_request = null;
        self.model.db.clear_order();
        self.render_list();
        self.clear_current_product_info();
    },
    reload_request:function(){
        var loaded = new $.Deferred();
        var self = this;
        self.model.load_request().then(function(){
            self.model.load_requestline().then(function(){
                loaded.resolve();
            });
        });
        return loaded;
    },
    reload_history:function(){
        var loaded = new $.Deferred();
        var self = this;
        self.model.load_history().then(function(){
//            self.model.load_requestline().then(function(){
                loaded.resolve();
//            });
        });
        return loaded;
    },
    clear_current_product_info:function(msg){
        var self=this,db = self.model.db,product = self.model.get_product();
        var $btn_add = self.$('#add-to-list');
        self.current_code = '';
        db.select_product();
        self.$('#store_condition').text('');
//        self.$('#display_condition').text('');
        self.$('#itemcode').text('');
        self.$('#itemname').text(msg ? msg : _t('Not found'));
        self.$('#pack_size').text('');
        self.$('#qty_available').text('');
        self.$('#real_qty').val('');
        $btn_add.attr('disabled', true).addClass('disabled');
        self.$('#scanned_code').text('');
        self.$('#note').val('');
        self.current_product = product;
    },
    get_current_UTCtime:function(){
        ///forrmat : %Y-%m-%d %H:%M:%S %z
        var today = new Date();
        var date = today.getUTCFullYear()+'-'+(today.getUTCMonth()+1)+'-'+today.getUTCDate();
        var time = today.getUTCHours() + ":" + today.getUTCMinutes() + ":" + today.getUTCSeconds();
        var timezone = '+0000'// 'cause this function is get UTC time , the timezone is always UTC+0000
        var datetime = date+' '+time+' '+timezone;
        return datetime;
    },
    calculating_unit:function(){
        var self=this,real_qty=self.$('#real_qty').val();
        if(!self.current_product){
            return;
        }
        if(!real_qty||real_qty<0){
            real_qty=0;
        }
        var product = self.current_product,
            pack_size=product.pack_size;

        var data = {
            pack_size:pack_size,
            quotient:Math.floor(real_qty/pack_size),
            remainder:real_qty%pack_size,
            total_case:parseFloat((real_qty/pack_size).toFixed(3)),
            total_unit:real_qty,
        };
        self.gui.show_popup('general', {
            title: _t('Advanced Calculator'),
            html: qweb.render('popup_unit_calculator_tmpl',{data:data}),
            button: 3, //BT_OK | BT_CANCEL
            buttonText: {ok: _t('Ok')},
            confirm: function(){
                var case_qty=parseInt($('#case_qty').val()),
                    unit_qty=parseInt($('#unit_qty').val()),
                    total_unit = case_qty*pack_size+unit_qty;
                self.$('#real_qty').val(total_unit);
            },
            init: function(){
                var $case_qty=$('#case_qty'),$unit_qty=$('#unit_qty'),
                    $total_case_qty=$('#total_case_qty'),$total_unit_qty=$('#total_unit_qty'),
                    $case_or_cases=$('#case_or_cases'),$unit_or_units=$('#unit_or_units');
                $case_qty.change(function(){recalculating();});
                $unit_qty.change(function(){recalculating();});
                function recalculating(){
                    var case_qty=parseInt($case_qty.val()),unit_qty=parseInt($unit_qty.val()),
                        total_unit,total_case;
                    if(!case_qty||case_qty<0){
                        $case_qty.val(0);
                        case_qty=parseInt($case_qty.val());
                    }
                    if(!unit_qty||unit_qty<0){
                        $unit_qty.val(0);
                        unit_qty=parseInt($unit_qty.val());
                    }
                    if(unit_qty>pack_size){
                        case_qty=case_qty+Math.floor(unit_qty/pack_size);
                        $case_qty.val(case_qty);
                        unit_qty=unit_qty%pack_size;
                        $unit_qty.val(unit_qty);
                    }

                    total_unit=case_qty*pack_size+unit_qty;
                    total_case=parseFloat((total_unit/pack_size).toFixed(3));

                    $total_case_qty.text(total_case);
                    $total_unit_qty.text(total_unit);

                    //đều chỉnh flural hoặc singular
                    if(total_unit>1){
                        $unit_or_units.text('Units');
                    }else{
                        $unit_or_units.text('Unit');
                    }
                    if(total_case>1){
                        $case_or_cases.text('Cases');
                    }else{
                        $case_or_cases.text('Case');
                    }
                };
            },
        })
    },
    calculating_storage_unit:function(){
        var self=this;
        if(!self.current_product){
            return;
        }
        var product = self.current_product,
            pack_size=product.pack_size;

        var data = {
            pack_size:pack_size,
            quotient:Math.floor(storage_qty),
            remainder:((storage_qty - Math.floor(storage_qty)) * pack_size).toFixed(0),
            total_case:storage_qty,
            total_unit:(storage_qty * pack_size).toFixed(0),
        };
        self.gui.show_popup('general', {
            title: _t('Advanced Calculator'),
            html: qweb.render('popup_unit_calculator_tmpl',{data:data}),
            button: 3, //BT_OK | BT_CANCEL
            buttonText: {ok: _t('Ok')},
            confirm: function(){
                var case_qty=parseInt($('#case_qty').val()),
                    unit_qty=parseInt($('#unit_qty').val()),
                    total_unit = case_qty + unit_qty / pack_size;
            },
            init: function(){
                var $case_qty=$('#case_qty'),$unit_qty=$('#unit_qty'),
                    $total_case_qty=$('#total_case_qty'),$total_unit_qty=$('#total_unit_qty'),
                    $case_or_cases=$('#case_or_cases'),$unit_or_units=$('#unit_or_units');
                $case_qty.change(function(){recalculating();});
                $unit_qty.change(function(){recalculating();});
                function recalculating(){
                    var case_qty=parseInt($case_qty.val()),unit_qty=parseInt($unit_qty.val()),
                        total_unit,total_case;
                    if(!case_qty||case_qty<0){
                        $case_qty.val(0);
                        case_qty=parseInt($case_qty.val());
                    }
                    if(!unit_qty||unit_qty<0){
                        $unit_qty.val(0);
                        unit_qty=parseInt($unit_qty.val());
                    }
                    if(unit_qty>pack_size){
                        case_qty=case_qty+Math.floor(unit_qty/pack_size);
                        $case_qty.val(case_qty);
                        unit_qty=unit_qty%pack_size;
                        $unit_qty.val(unit_qty);
                    }

                    total_unit=case_qty*pack_size+unit_qty;
                    total_case=parseFloat((total_unit/pack_size).toFixed(3));

                    $total_case_qty.text(total_case);
                    $total_unit_qty.text(total_unit);

                    //đều chỉnh flural hoặc singular
                    if(total_unit>1){
                        $unit_or_units.text('Units');
                    }else{
                        $unit_or_units.text('Unit');
                    }
                    if(total_case>1){
                        $case_or_cases.text('Cases');
                    }else{
                        $case_or_cases.text('Case');
                    }
                };
            },
        })
    },
    input_without_scan: function(ev){
        var self=this,
            line=$(ev.target).closest('.list-group-item').data('requestline-id'),
            db =self.model.db,
            requestline=db.get_requestline_by_id(line);

        var loaded = self.model.find_product(parseInt(requestline.product_id), true);
        self.gui.show_popup('loading', {body: _t('Reloading product ')+requestline.product_code, cancel: function(){
            loaded.reject();
        }});
        loaded.then(function(){
            self.gui.close_popup();
            self.set_picking_product(0);
        }, function (err, reason) {
            self.chrome.loading_error(err, reason);
        });
    },
    input_replacement_product: function(requestline, replacement_detail){
        var self=this,
            db =self.model.db;

        var loaded = self.model.find_product(parseInt(replacement_detail.product_id[0]), true);
        self.gui.show_popup('loading', {body: _t('Reloading product ')+requestline.product_code, cancel: function(){
            loaded.reject();
        }});
        loaded.then(function(){
            self.gui.close_popup();
            self.set_picking_product(0, replacement_detail);
        }, function (err, reason) {
            self.chrome.loading_error(err, reason);
        });
    },
    more_info_click:function(ev){
        var self=this,
            line=$(ev.target).closest('.list-group-item').data('requestline-id'),
            db =self.model.db,
            requestline=db.get_requestline_by_id(line),
            gui_option = 3;
            //console.log(requestline.product_qty);
        self.gui.show_popup('general', {
            title: _t('Product Info'),
            html: '<strong>'+'['+requestline.product_code+'] '+requestline.product_name+'</strong><div><iframe style="width:100%" src="https://cz-epos.longdan.co.uk:18170/longdan_planogram/product_place?store_code=' + odoo.session_info.db + '&amp;product_code=' + requestline.product_code + '&application=' + self.chrome.module_code + '&amp;mini_iframe=True"></iframe></div>'
            + '<div><iframe style="width:100%;height:200px;" src="https://cz-epos.longdan.co.uk:18170/longdan_image/product_image?product_code=' + requestline.product_code + '"></iframe></div>',
            button: gui_option, //BT_OK | BT_CANCEL
            buttonText: {cancel: _t("Can't pick")},
            init: function(){
                //console.log('init');
            },
            cancel: function(){
                self.cant_pick_action(ev);
            }
        })
    },

    onClickReloadApp: function () {
      var self = this;
      self.gui.show_popup('general', {
        title: _t('Warning'),
        html: _t('Reload App will reload this app. All data still exists after reload'),
        button: 3, //BT_OK | BT_CANCEL
        buttonText: {ok: _t('Reload App')},
        confirm: function () {
          window.location.reload();
        }
      });
    },
});
gui.define_screen({name: 'first_website_main_screen', widget: MainScreenWidget});

return {
    ScreenWidget: screens.ScreenWidget,
    MainScreenWidget: MainScreenWidget
};

});
