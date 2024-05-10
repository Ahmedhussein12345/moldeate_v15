from odoo import models, fields, api, _


class ShippingAPILog(models.Model):
    _name = 'shipping.api.log'
    _description = "Log"
    _order = 'id desc'

    name = fields.Char('Name', readonly=True, required=True, default=lambda self: _('New'))
    shipping_partner_id = fields.Many2one('shipping.partner', "Provider", ondelete='cascade', required=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user, copy=False)
    request_data = fields.Text('Request Data', copy=False, readonly=True)
    response_data = fields.Text('Response Data', copy=False, readonly=True)

    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('shipping.api.log') or _('New')
        res = super(ShippingAPILog, self).create(vals)
        return res