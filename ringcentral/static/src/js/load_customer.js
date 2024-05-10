odoo.define('ringcentral.load_customer', function (require){
    "use strict";

    var rpc = require('web.rpc');
    var session = require('web.session');

    console.log("/////////////////////////////")
    return rpc.query({
        model: 'res.partner',
        method: 'get_search_read',
        args: [],
        context: session.context
    })
    
})



