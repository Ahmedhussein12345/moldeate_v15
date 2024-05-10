from odoo import fields, models, api


class BaseAutomation(models.Model):
    _inherit = "base.automation"

    model_name = fields.Char(string="Model Name", relation='model_id.model')


BaseAutomation()


class IrFilter(models.Model):
    _inherit = "ir.filters"

    model_name = fields.Char(string="Model Name", relation='model_id.model')

IrFilter()


class IrModelAccess(models.Model):
    _inherit = "ir.model.access"

    model_name = fields.Char(string="Model Name", relation='model_id.model')


IrModelAccess()


