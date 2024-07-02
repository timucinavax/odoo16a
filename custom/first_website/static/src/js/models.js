odoo.define('first_website.models', function (require) {
"use strict";

var rpc = require('web.rpc');
var devices = require('vx_web_ui.devices');
var VXDB = require('first_website.DB');
var model = require('vx_web_ui.models');

model.EcomPickingModel = model.UiModel.extend({
    stock_expire: 10080,
    rpc_config: {
        timeout: 60*1000 //1 minute
    },
    initialize: function(session, attributes) {
        model.UiModel.prototype.initialize.apply(this, arguments);
        var  self = this;
        this.chrome = attributes.chrome;
        this.gui    = attributes.gui;
        this.barcode_reader = new devices.BarcodeReader({'model': this, proxy:this.proxy});
        this.db = new VXDB();
        this.wait_product_id = session.products || [];

        this.ready = this.load_server_data().then(function(){
            self.db.set_request_list(session.requests);
            self.db.set_requestline_list(session.requestlines);
            return self.after_load_server_data();
        });
        this.init_idle_job();
//        setInterval(function () {
//            self.update_active_product_ids_each_days();
//        }, 24*60*60000);//each days
        window.vx_PickingModel = this;
        this.load_method = 'first_website_search_by_product_ids';
    },
    get_waiting_count: function () {
        return this.wait_product_id.length;
    },
    onchange_waiting_count: function () {
        var self=this, c = self.gui ? self.gui.get_current_screen() : 0;
        if (c && c.update_waiting_count)
            c.update_waiting_count(self.wait_product_id.length);
    },
    after_load_server_data: function(){
        var db = this.db, list = this.wait_product_id;
        for(var i=0; i<list.length; i++){
            if (db.get_product(list[i])){
                list.splice(i, 1);
                i--;
            }
        }
    },
    do_idle_job: function () {
        var self = this;
        self.idle_time = 0;
        self.find_expired_product();
        self.background_load_product();
    },
    find_expired_product: function(){
        var list = this.db.get_expired_product_id(this.stock_expire);
        this.wait_product_id = [];
        if (list.length) {
            this.wait_product_id = list;
            this.onchange_waiting_count();
        }
    },
    update_active_product_ids_each_days: function(){
        var self = this, db = this.db;
        rpc.query({
            model: 'product.product',
            method: 'get_active_ids'
        }, this.rpc_config).then(function(result){
            if (result.ids){
                var a=0,n=0;
                for (var i in result.ids){
                    if (!db.get_product(result.ids[i])){
                        self.wait_product_id.push(result.ids[i]);
                        a++;
                    }else{
                        n++;
                    }
                }
            }
        },function(err, reason){
            // console.error(err, reason);
        });
    },

    get_product: function(product_id){
        var product = this.db.get_product(product_id);
        return product ? new model.EcomPickingProduct({}, product) : false;
    },
    remote_load_product: function(promise, params){
        var self = this;
        rpc.query(params, this.rpc_config).then(function(result){
            try{
                $.when().then(function(){
                    self.load_product(result.product, result.barcodes);
                    promise.resolve();
                },function(err){ promise.reject(err);
                });
            }catch(err){
                console.error(err.message, err.stack);
                promise.reject(err);
            }
        },function(err, reason){
            promise.reject(err, reason);
        });
    },
    search_by_barcode: function(barcode){
        var loaded = new $.Deferred(), db = this.db;
        this.idle_time = 0;
        var product = db.search_product(barcode);
        if (product){
            db.select_product(product);
            loaded.resolve();
            return loaded;
        }
        this.remote_load_product(loaded, {
            model: 'product.product',
            method: 'ecompk_search_by_barcode',
            kwargs: {
                barcode: barcode
            }
        });
        return loaded;
    },
    find_product: function(query, by_id){
        var loaded = new $.Deferred(), db = this.db;
        this.idle_time = 0;
        var product = by_id ? 0 : db.search_product(0, query);
        if (product){
            db.select_product(product);
            loaded.resolve();
            return loaded;
        }
        this.remote_load_product(loaded, {
            model: 'product.product',
            method: 'ecompk_search_by_query',
            kwargs: {
                query: query,
                by_id: !!by_id
            }
        });
        return loaded;
    },

    submit_list_done: function(){
        this.db.remove_order();
    },
    load_product: function(product, barcodes){
        this.db.add_product(product, barcodes);
        if (product){
            var index = this.wait_product_id.indexOf(product.id);
            if (index >= 0)
                this.wait_product_id.splice(index, 1);
        }
        this.db.select_product(product);
    },
    submit_request_to_backend: function(request_id){
        var self = this,db = self.db,
            request = db.get_request_by_id(request_id),
            requestlines = db.get_requestline_by_request_id(request_id);
            request['picking_user'] = db.get_picking_user();
        if (!request||!requestlines)
            return false;
        var loaded = new $.Deferred();
        var params = {
            model: 'sale.order',
            method: 'confirm_request_to_sent',
            args: [],
            kwargs: {
                request: request,
                requestlines:requestlines,
            }
        };

        rpc.query(params, this.rpc_config).then(function(result){
            try{
                $.when().then(function(){
                    loaded.resolve(result);
                }, function(err, reason){
                    loaded.reject(err, reason);
                });
            }catch(err){
                loaded.reject(err);
            }
        },function(err, reason){
            loaded.reject(err, reason);
        });
        return loaded;
    },
    load_request: function(){
        var db = this.db;
        var self = this;
        return rpc.query({
                model: 'sale.order',
                method: 'get_request',
                args: [self.chrome.module_code],
            }, this.rpc_config).then(function(result){
                db.set_request_list(result);
            },function(err, reason){
                 console.error(err, reason);
            });
    },
    load_history: function(){
        var db = this.db;
        var self = this;
        return rpc.query({
                model: 'sale.order',
                method: 'get_history',
                args: [self.chrome.module_code],
            }, this.rpc_config).then(function(result){
                db.set_history_list(result);
            },function(err, reason){
                 console.error(err, reason);
            });
    },
    load_requestline: function(){
        var db = this.db;
        var self = this;
        return rpc.query({
            model: 'sale.order.line',
            method: 'get_requestline',
            args: [self.chrome.module_code],
        }, this.rpc_config).then(function(result){
            db.set_requestline_list(result);
        },function(err, reason){
             console.error(err, reason);
        });
    },
    load_history_detail: function(history_id){
        var db = this.db;
        var self = this;
        return rpc.query({
            model: 'sale.order.line',
            method: 'get_history_detail',
            args: [history_id, self.chrome.module_code],
        }, this.rpc_config).then(function(result){
            db.current_history_detail = result;
        },function(err, reason){
             console.error(err, reason);
        });
    },
});

model.EcomPickingProduct = Backbone.Model.extend({
    initialize: function(attr, options) {
        this.id = options.id || 0;
        this.code = options.code || '';
        this.name = options.name || '';
        this.pack_size = options.pack_size || 1;
        this.qty_available = options.qty_available || 0;
        this.update = options.update || 0;
        this.store_condition = options.store_condition || '';
        this.display_condition = options.display_condition || '';
    }
});

model.EcompickingProductRequest = Backbone.Model.extend({
    initialize: function(attr, options) {
        this.product_id = options.product_id || 0;
        this.code = options.code || '';
        this.name = options.name || '';
        this.pack_size = options.pack_size || 1;
        this.qty_available = options.qty_available || 0;
        this.qty = options.qty || 1;
    }
});

return model;

});
