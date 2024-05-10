from odoo.models import BaseModel, AbstractModel
from odoo import api
from lxml import etree

_fields_view_get = AbstractModel.fields_view_get

class Http(AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super(Http, self).session_info()
        if self.env.user.has_group('ye_dynamic_odoo.group_dynamic'):
            result['showEdit'] = True
        return result


@api.model
def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
    res = _fields_view_get(self, view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
    res['fieldsGet'] = self.env[self._name].fields_get()
    if 'odo.studio' in self.env.registry.models and res and 'view_id' in res:
        ui_view = self.env['ir.ui.view']
        model_view = "odo.studio.sub_view" if self.env.context.get("useSubView", False) else 'odo.studio'
        view_studio = self.env[model_view].search([['view_id', '=', res['view_id']]], limit=1)
        if len(view_studio):
            old_fields = res['fields']
            # res['arch'] = view_studio[0].xml
            x_arch, x_fields = ui_view.with_context(DynamicOdo=True).postprocess_and_fields(etree.fromstring(view_studio.xml), model=self._name)
                # self._name, etree.fromstring(view_studio.xml), view_studio.view_id.id)
            res['arch'] = x_arch
            res['fields'] = x_fields
            # set subviews from base view
            for field_name in old_fields:
                old_field = old_fields[field_name]
                if 'views' in old_field and len(old_field['views'].keys()) and field_name in res['fields']:
                    res['fields'][field_name]['views'] = old_field['views']

        sub_view_exist = self.env['odo.studio.sub_view'].search([['parent_view_id', '=', res.get('view_id', False)]])
        for sub_view in sub_view_exist:
            field_name = sub_view.field_name
            view_type = sub_view.view_type
            views = res['fields'][field_name]['views']
            sub_view_model = res['fields'][field_name]['relation']
            if type(views) is dict:
                if view_type not in views:
                    views[view_type] = {}
                view_process = ui_view.postprocess_and_fields(etree.fromstring(sub_view.xml), model=sub_view_model)
                views[view_type]['arch'] = sub_view.xml
                views[view_type]['fields'] = view_process[1]

    return res


AbstractModel.fields_view_get = fields_view_get
