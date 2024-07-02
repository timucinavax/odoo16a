
odoo.define('first_website.ui', function (require) {
"use strict";

var chrome = require('first_website.chrome');
var core = require('web.core');

core.action_registry.add('first_website.ui', chrome.Chrome);

});
