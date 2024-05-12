odoo.define('first_website.DB', function (require) {
"use strict";

var core = require('web.core');
var localStorage = require('web.local_storage');

return core.Class.extend({
    name: 'ecom_picking_230601', //the prefix of the localstorage data
    product_selected: null,
    module_code: null,
    cache: {},
    cache_change: {},
    ecom_picking_product_codes: {"id":"i","name":"n","uom_id":"ui","code":"c","pack_size":"ps","qty_available":"qa","update":"u"},
    uom_name_mapping: {"1":"Unit(s)", "3":"kg"},
    compress_local_storage: false,
    data_to_compress: [
        'product',
        'barcode',
        'itemcode',
    ],

    init: function(options){
        options = options || {};
        this.name = options.name || this.name;

        this.init_local_storage_compression();
        this.queue_product_id = {};
        this.product_by_id = this.ecom_picking_product_decode(this.load('product', {}));
        this.product_id_by_barcode = this.load('barcode', {});
        this.product_id_by_code = this.load('itemcode', {});
        this.module_code = odoo.session_info.module_code?odoo.session_info.module_code:'epos_ecom_picking';
        this.order = this.load('order_'+this.module_code, this.new_order());
        //request từ office
        //this.requests=this.new_request();
        //this.requestlines=this.new_requestline();
        this.requests = this.load('requests',[]);
        this.requestlines = this.load('requestlines',[]);
        this.histories = [];
        this.history_lines = [];
    },
    init_local_storage_compression: function() {
      var data = localStorage[this.name + '_compress_local_storage'];
      if (data === undefined || data === "") {
        data = "false";
        var exist_data = false;
        for (var i = 0; i < this.data_to_compress.length; i++) {
          var store = this.data_to_compress[i];
          var store_data = localStorage[this.name + '_' + store];
          if (store_data !== undefined) {
            exist_data = true;
            break;
          }
        }
        if (!exist_data) {
          // Enable compression by default if there are no existing data
          data = "true";
        }
      }
      this.compress_local_storage = JSON.parse(data);
      localStorage[this.name + '_compress_local_storage'] = this.compress_local_storage;
    },
    set_local_storage_compression: function(value) {
      var self = this;
      if ((!this.compress_local_storage && value) || (this.compress_local_storage && !value)) {
        // Store old datas
        var datas = {};
        _.each(this.data_to_compress, function(store) {
          datas[store] = self.load(store);
        });

        // Changing compressionflag
        this.compress_local_storage = value;
        localStorage[this.name + '_compress_local_storage'] = this.compress_local_storage;
        console.log('Compression set to ' + this.compress_local_storage);

        // Compress/Decompress old data
        _.each(this.data_to_compress, function(store) {
          self.save(store, datas[store]);
        });
      }
    },
    isDataToBeCompress: function(store) {
        return this.compress_local_storage && this.data_to_compress.includes(store);
    },
    compressLocalStorage: function(store, data, force) {
      if (force || this.isDataToBeCompress(store)) {
        try {
          var startTime = performance.now();
          if ($.browser.webkit) {
            data = LZString.compress(data);
          } else {
            data = LZString.compressToUTF16(data);
          }
          var endTime = performance.now();
          console.debug("CompressLocalStorage for '" + store + "' took " + (endTime - startTime) + "ms.");
        } catch (err) {
          console.error("Error compressing data", err);
        }
      }
      return data;
    },
    decompressLocalStorage: function(store, data, force) {
      if (force || this.isDataToBeCompress(store)) {
        try {
          var decompressed_data = null;
          var startTime = performance.now();
          if ($.browser.webkit) {
            decompressed_data = LZString.decompress(data);
          } else {
            decompressed_data = LZString.decompressFromUTF16(data);
          }
          var endTime = performance.now();
          console.debug("DecompressLocalStorage for '" + store + "' took " + (endTime - startTime) + "ms.");
          if (decompressed_data == null) {
            console.warn("A problem happened when decompressing local storage data. Trying too fix it...");
            var compressed_data = LZString.compress(data);
            decompressed_data = LZString.decompress(compressed_data);
            if (decompressed_data == null) {
              console.warn("Cannot fix the decompression data");
            } else {
              console.warn("Local storage data was recompressed");
              localStorage[this.name + '_' + store] = compressed_data;
              data = decompressed_data;
            }
          } else {
            data = decompressed_data;
          }
        } catch (err) {
          console.error("Error decompressing data", err);
        }

      }
      return data;
    },
    /* loads a record store from the database. returns default if nothing is found */
    load: function (store, def) {
      var data = localStorage[this.name + '_' + store];
      if (data !== undefined && data !== "") {
        var decompressed_data = this.decompressLocalStorage(store, data);
        var parsed_data = null;

        try {
          parsed_data = JSON.parse(this.decompressLocalStorage(store, data));
        } catch (err) {
          console.warn("Problem parsing data from local storage. Trying to fix...");
          try {
            parsed_data = JSON.parse(this.decompressLocalStorage(store, data, true));
            if (parsed_data) {
              console.warn("Local storage data was fixed");
              localStorage[this.name + '_' + store] = JSON.stringify(parsed_data);
            } else {
              console.warn("Cannot fix local storage data");
              parsed_data = def;
            }
          } catch (err) {
            console.error("Error parsing data", err);
            parsed_data = def;
          }
        }

        data = parsed_data;
        return data;
      } else {
        return def;
      }
    },
    /* saves a record store to the database */
    save: function(store,data){
        try {
            localStorage[this.name + '_' + store] = this.compressLocalStorage(store, JSON.stringify(data));
            this.cache[store] = data;
        } catch (e) {
            console.error(e);
        }
    },
    getLocalStorageSize: function() {
      var total = 0;
      for (var x in localStorage) {
          // Value is multiplied by 2 due to data being stored in `utf-16` format, which requires twice the space.
          var amount = (localStorage[x].length * 2) / 1024 / 1024;
          if (amount) {
            total += amount;
          }
      }
      console.log("Total Local Storage size : " + total.toFixed(2) + " MB");
      return total.toFixed(2);
    },
    ecom_picking_product_encode: function(data){
        var clone_data = JSON.parse(JSON.stringify(data));
        for (var i in clone_data){
            var clone_data_product = clone_data[i];
            if(clone_data_product.update){
                clone_data_product.update = Math.floor(moment(clone_data_product.update).valueOf() / 60000);
            }
            if(clone_data_product.uom_id && clone_data_product.uom_id.length == 2 && this.uom_name_mapping[clone_data_product.uom_id[0]]){
                clone_data_product.uom_id.pop();
            }
            for(let [key, value] of Object.entries(this.ecom_picking_product_codes)){
                if (key in clone_data_product){
                    clone_data_product[value] = clone_data_product[key];
                    delete clone_data_product[key];
                }
            }
        }
        return clone_data;
    },
    ecom_picking_product_decode: function(data){
        var clone_data = JSON.parse(JSON.stringify(data));
        for (var i in clone_data){
            var clone_data_product = clone_data[i];
            for(let [key, value] of Object.entries(this.ecom_picking_product_codes)){
                if (value in clone_data_product){
                    clone_data_product[key] = clone_data_product[value];
                    delete clone_data_product[value];
                }
            }
            if(clone_data_product.update){
                clone_data_product.update = moment(clone_data_product.update * 60000).format();
            }
            if(clone_data_product.uom_id && clone_data_product.uom_id.length == 1 && this.uom_name_mapping[clone_data_product.uom_id[0]]){
                clone_data_product.uom_id.push(this.uom_name_mapping[clone_data_product.uom_id[0]]);
            }
        }
        return clone_data;
    },
    select_product: function(product){
        this.product_selected = product;
    },
    get_product: function (product_id) {
        if (product_id === undefined)
            return this.product_selected;
        return this.product_by_id[product_id];
    },
    search_by_weight_code: function(code){
        var r = code.match(/^\d{2}(\d{6})\d{5}$/);
        if (r){
            var pid = this.product_id_by_code[r[1]], product;
            if (pid) {
                product = this.product_by_id[pid];
                if (product && product.uom_id && product.uom_id[1] == 'kg')
                    return product;
            }
        }
        return false;
    },
    search_product: function(barcode, query){
        var pid;
        if (barcode) {
            barcode = barcode.replace(/^0+/, ''); // Remove leading zero from barcode
            pid = this.product_id_by_barcode[barcode];
            if (pid)
                return this.product_by_id[pid];
            return this.search_by_weight_code(barcode);
        }else{
            barcode = query.replace(/^0+/, ''); // Remove leading zero from barcode
            pid = this.product_id_by_barcode[barcode] || this.product_id_by_code[query];
            if (pid)
                return this.product_by_id[pid];
            var reg = new RegExp(query,'i');
            for (pid in this.product_by_id){
                if (reg.test(this.product_by_id[pid].name))
                    return this.product_by_id[pid];
            }
            return this.search_by_weight_code(query);
        }
    },
    add_product: function(product, barcodes){
        if (product){
            this._update_product(product);
            this._update_product_by_code(product);
            this._update_barcode(barcodes, product.id);
        }
    },
    add_batch_product: function(list){
        var product;
        var s = this.cache_change;
        for (var i=0,len=list.length; i<len; i++){
            product = list[i].product;
            if (product) {
                this._update_product(product, true);
                if (this._update_product_by_code(product, true))
                s.itemcode = 1;
            if (this._update_barcode(list[i]['barcodes'], product.id, true))
                s.barcode = 1;
            }
        }
        s.product = 1;
    },
    batch_save_cache: function(){
        var s = this.cache_change;
        if (s.product){
            this.save('product', this.ecom_picking_product_encode(this.product_by_id));
        }
        if (s.itemcode){
            this.save('itemcode', this.product_id_by_code);
        }
        if (s.barcode){
            this.save('barcode', this.product_id_by_barcode);
        }
        this.cache_change = {};
    },
    get_expired_product_id: function(minutes){
        var list = [], products = this.product_by_id, now = moment();
        var ml_seconds = minutes * 60000;
        for(var pid in products){
            if (!this.queue_product_id[pid] && ml_seconds < now.diff(moment(products[pid].update))) {
                list.push(parseInt(pid));
                this.queue_product_id[pid] = 1;
            }
        }
        return list;
    },
    clear_cache: function () {
        var ids = [];
        for (var id in this.product_by_id)
            ids.push(parseInt(id));
        this.queue_product_id = {};
        this.product_by_id = {};
        this.product_id_by_barcode = {};
        this.product_id_by_code = {};
        this.order = this.new_order();
        this.select_product(0);
        //this.requests=[];
        //this.requestlines=[];
        this.save('product', {});
        this.save('barcode', {});
        this.save('itemcode', {});
        this.save('order_'+this.module_code, this.order);
        return ids;
    },
    _update_product: function(product, no_cache){
        product.update = moment().format();
        this.queue_product_id[product.id] = 0;
        this.product_by_id[product.id] = product;
        if (!no_cache)
            this.save('product', this.ecom_picking_product_encode(this.product_by_id));
    },
    _update_product_by_code: function(product, no_cache){
        if (!this.product_id_by_code[product.code]) {
            this.product_id_by_code[product.code] = product.id;
            if (!no_cache)
                this.save('itemcode', this.product_id_by_code);
            return true;
        }
        return false;
    },
    _update_barcode: function(barcodes, product_id, no_cache){
        var i,len, update = false;
        for(i=0, len=barcodes.length; i<len; i++) {
            var barcode = barcodes[i];
            barcode = barcode.replace(/^0+/, ''); // Remove leading zero from barcode
            if (!this.product_id_by_barcode[barcode]) {
                this.product_id_by_barcode[barcode] = product_id;
                update = true;
            }
        }
        if (update && !no_cache)
            this.save('barcode', this.product_id_by_barcode);
        return update;
    },
    new_order: function(){
        return {
            by_product_id: {},
            count: 0
        };
    },
    add_order: function(request){
        var order = this.order, id = request.product_id;
        if (order.by_product_id[id]) {
            // order.by_product_id[id].qty = request.qty;
            return 0;
        }else{
            order.by_product_id[id] = request;
            order.count++;
            this.save('order_'+this.module_code, order);
            return 1;
        }
    },
    get_order: function(){
        return this.order.count ? this.order.by_product_id : false;
    },
    set_order_type: function(type){
        if (this.order_info) {
        this.order_info['type'] = type;
      } else {
        this.order_info = {'type':type};
      }
    },
    get_order_info: function(){
        return this.order_info ? this.order_info : false;
    },
    set_picking_user: function (picking_user) {
      if (this.order_info) {
        this.order_info['picking_user'] = picking_user;
      } else {
        this.order_info = {'picking_user':picking_user};
      }
    },
    set_start_picking_user: function (picking_user) {
      if (this.order_info) {
        this.order_info['start_picking_user'] = picking_user;
      } else {
        this.order_info = {'start_picking_user':picking_user};
      }
    },
    get_start_picking_user: function () {
      return this.order_info ? this.order_info['start_picking_user'] : false;
    },
    get_picking_user: function () {
      return this.order_info ? this.order_info['picking_user'] : false;
    },
    get_order_count: function(){
        return this.order.count;
    },
    remove_order: function(){
        this.order = this.new_order();
        this.save('order_'+this.module_code, this.order);
    },
    get_request_line: function(product_id){
        return this.order.by_product_id[product_id];
    },
    get_all_line: function(){
        var list = [], i;
        for(i in this.order.by_product_id) {
            var item = $.extend({}, this.order.by_product_id[i]),
                product = this.get_product(item.product_id);
            list.push($.extend(item, product));
        }
        return list;
    },
    set_request_line: function(product_id, data){
        this.order.by_product_id[product_id] = data;
        this.save('order_'+this.module_code, this.order);
    },
    remove_product_request: function(product_id){
        var order = this.order;
        if (order.by_product_id[product_id]) {
            delete order.by_product_id[product_id];
            order.count--;
            this.save('order_'+this.module_code, this.order);
        }
    },
    clear_order: function () {
        this.order = this.new_order();
        this.save('order_'+this.module_code, this.order);
    },
    //code cho phần request từ office
    new_request: function(){
        return {
            by_product_id: {},
            count: 0
        };
    },
    set_request_list:function(request_list){
        this.requests=request_list;
        return 1;
    },
    set_history_list:function(history_list){
        this.histories=history_list;
        return 1;
    },
    get_all_request:function(){
        var list = [], i;
        for(i in this.requests) {
            var item = $.extend({},this.requests[i]);
            list.push(item);
        }
        return list;
    },
    get_all_histories:function(){
        var list = [], i;
        for(i in this.histories) {
            var item = $.extend({},this.histories[i]);
            list.push(item);
        }
        return list;
    },
    get_request_by_id: function(request_id){
        var i;
        for(i in this.requests)
            if(this.requests[i].id==request_id)
                return this.requests[i];
        return null;
    },
    get_request_count:function(){
        if(!this.requests){return 0;}
        return this.requests.length;
    },
    get_history_count:function(){
        if(!this.histories){return 0;}
        return this.histories.length;
    },
    new_requestline: function(){
        return {
            by_product_id: {},
            count: 0
        };
    },
    set_requestline_list:function(requestline_list){
        var old_requestlines = this.load('requestlines', []);

        for(var pos in requestline_list){
            var requestline = requestline_list[pos];
            for(var old_pos in old_requestlines){
                var old_requestline = old_requestlines[old_pos];
                if(requestline.id == old_requestline.id){
                    requestline_list[pos] = old_requestline;
                    break;
                }
            }
        }
        this.requestlines=requestline_list;
        this.save('requestlines', requestline_list);
        return 1;
    },
    get_all_requestline:function(){
        var list = [], i;
        for(i in this.requestlines) {
            var item = $.extend({},this.requestlines[i]);
            list.push(item);
        }
        return list;
    },
    get_requestline_by_id: function(requestline_id){
        var i;
        for(i in this.requestlines)
            if(this.requestlines[i].id==requestline_id)
                return this.requestlines[i];
        return null;
    },
    get_requestline_by_request_id: function(request_id){
        var list = [], i;
        for(i in this.requestlines) {
            if (this.requestlines[i].order_id[0]==request_id){
                var item = $.extend({},this.requestlines[i]);
                list.push(item);
            }
        }
        return list;
    },
    get_requestline_count: function(request_id){
        if(!this.requestlines){
            return 0;
        }
        var count=0,i;
        for(i in this.requestlines) {
            if (this.requestlines[i].order_id[0]==request_id)
                count++;
        }
        return count;
    },
    add_product_to_requestline: function(requestline_id,data){
        if(!this.requestlines||!requestline_id){
            return 0;
        }
        var i;
        for(i in this.requestlines)
            if(this.requestlines[i].id==requestline_id){
                this.requestlines[i].product_qty=data.qty;
                this.requestlines[i].is_picked=true;
                this.requestlines[i].is_replaced=false;
                this.requestlines[i].picking_time=data.picking_time;
                this.requestlines[i].note=data.note;
                this.requestlines[i].pack_size=data.pack_size;
                this.requestlines[i].replacement_data=null;
                this.requestlines[i].scanned=data.scanned;
                this.save('requestlines', this.requestlines);
                return true;
            }

        return false
    },
    add_replacement_product_to_requestline: function(replacement_detail,data){
        if(!this.requestlines||!replacement_detail||!replacement_detail.replacement_line_id){
            return 0;
        }
        var i;
        for(i in this.requestlines)
            if(this.requestlines[i].id==replacement_detail.replacement_line_id[0]){
                this.requestlines[i].is_replaced = true;
                this.requestlines[i].replacement_data = data;
                this.save('requestlines', this.requestlines);
                return true;
            }

        return false
    },
    reset_ecom_picking_line: function(requestline_id){
        if(!requestline_id){
            return false;
        }
        var i;
        for(i in this.requestlines)
            if(this.requestlines[i].id==requestline_id){
                this.requestlines[i].is_picked=false;
                this.requestlines[i].product_qty=0;
                this.requestlines[i].note='';
                return true;
            }
        this.save('requestlines', this.requestlines);
        return false;
    },
});
});
