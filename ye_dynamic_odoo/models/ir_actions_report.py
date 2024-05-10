from odoo import models, api, fields


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def _render_qweb_html(self, docids, data=None):
        return super(IrActionsReport, self.with_context(REPORT_ID=self.id))._render_qweb_html(docids, data=data)

