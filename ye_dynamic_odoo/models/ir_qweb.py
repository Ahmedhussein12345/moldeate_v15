from odoo import models, api, fields


class IRQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    def load(self, name, options):
        # _options = options.get("options", {})
        # report_id = _options.get("REPORT_ID", False)
        return super(IRQWeb, self).load(name, options)

IRQWeb()
