from odoo import fields, models, api


class ReportStudio(models.Model):
    _name = "odo.studio.report"

    xml = fields.Text(string="Xml")
    view_id = fields.Many2one(string="View id", comodel_name="ir.ui.view")
    report_id = fields.Many2one(string="Report Id", comodel_name="ir.actions.report")

    @api.model
    def undo_view(self, report_id):
        if report_id:
            return self.search([['report_id', '=', report_id]]).unlink()
        return False

    @api.model
    def change_report_props(self, data):
        report_action = self.env['ir.actions.report'].browse(data['id'])
        values = {}
        for key, value in data['values'].items():
            if key == "binding_model_id":
                values[key] = report_action.model_id.id if value else False
            elif key == "paperformat_id":
                values[key] = value['id'] if value else False
            elif key == "display_name":
                values["name"] = value
            elif key == "groups_id":
                values[key] = value if value else False
            else:
                values[key] = value
        report_action.write(values)

    @api.model
    def create_new_report(self, values):
        self.env['ir.ui.view']._load_records([dict(xml_id=values.get("xml_id", False), values={
            'name': values.get("name", False),
            'arch': values.get("xml", False),
            'key': values.get("xml_id", False),
            'inherit_id': False,
            'type': 'qweb',
        })])
        model_id = self.env['ir.model'].search([["model", '=', values['model']]]).id
        report = self.env["ir.actions.report"].create({
            'model': values['model'],
            "binding_type": "report",
            "binding_model_id":  model_id,
            "model_id": model_id,
            "name": values['string'],
            "report_file": values['report_file'],
            "report_name": values['report_name'],
            "report_type": "qweb-pdf",
            "type": "ir.actions.report",
            "xml_id": values['report_xml_id']
        })
        return {'id': report.id, 'name': report.name, 'report_name': report.report_name}

    @api.model
    def store_view(self, values):
        templates = values.get("templates", {})
        report_id = values.get("reportId", False)
        if report_id:
            for templateId in templates.keys():
                xml_template = templates[templateId]
                template = self.search([['report_id', '=', report_id], ['view_id', '=', int(templateId)]], limit=1)
                if len(template):
                    template.write({'xml': xml_template})
                else:
                    self.create({'report_id': report_id, 'xml': xml_template, 'view_id': templateId})
        return True

    @api.model
    def get_field_widget(self):
        all_models = self.env.registry.models
        models_name = all_models.keys()
        widgets = {}
        for model_name in models_name:
            if model_name.find("ir.qweb.field.") >= 0:
                widget_name = model_name.replace("ir.qweb.field.", "")
                self.env[model_name].get_available_options()
                widgets[widget_name] = self.env[model_name].get_available_options()

        return widgets


ReportStudio()


class ODOOStudio(models.Model):
    _name = "odo.studio"

    xml = fields.Text(string="Xml")
    view_id = fields.Many2one(string="View id", comodel_name="ir.ui.view")
    new_fields = fields.Many2many('ir.model.fields', string="New Fields", copy=False)

    @api.model
    def get_field_id(self, field_name, model_name):
        model_obj = self.env['ir.model'].search([['model', '=', model_name]], limit=1)
        field_obj = self.env['ir.model.fields'].search([['model_id', '=', model_obj.id], ['name', '=', field_name]], limit=1)
        if len(field_obj):
            return field_obj.id
        return False

    @api.model
    def get_group_xmlid(self, res_ids=[]):
        groups = self.env['ir.model.data'].search([['model', '=', 'res.groups'], ['res_id', 'in', res_ids]])
        return ",".join([x.complete_name for x in groups])

    @api.model
    def get_group_id(self, xmlid=""):
        result = []
        for x in xmlid.split(","):
            group = self.env.ref(x)
            result.append({'id': group.id, 'display_name': group.display_name})
        return result

    @api.model
    def get_relation_id(self, model):
        model_obj = self.env['ir.model'].search([['model', '=', model]], limit=1)
        if len(model_obj):
            return {'id': model_obj.id, 'display_name': model_obj.display_name}
        return {}

    @api.model
    def get_fields(self, model_name):
        return self.env['ir.model'].search([['model', '=', model_name]]).field_id.read()

    @api.model
    def create_new_view(self, values):
        view_mode = values.get('view_mode', False)
        action_id = values.get('action_id', False)
        data = values.get("data", {})
        if view_mode == "list":
            view_mode = "tree"
        view_id = self.env['ir.ui.view'].create(data)
        values_action_view = {'sequence': 100, 'view_id': view_id.id,
                              'act_window_id':action_id, 'view_mode': view_mode}
        self.env['ir.actions.act_window.view'].create(values_action_view)
        return view_id

    @api.model
    def create_m2o_from_o2m(self, new_field):
        field_m2one = new_field.get('fieldM2one', {})
        model_m2one = self.env['ir.model'].search([('model', '=', field_m2one.get("model_name", False))])
        field_m2one.update({'model_id': model_m2one.id, 'state': 'manual'})
        del field_m2one['model_name']
        self.env['ir.model.fields'].create(field_m2one)
        del new_field['fieldM2one']

    @api.model
    def store_view(self, values):
        views_exist = self.search([['view_id', '=', values.get('view_id', False)]], limit=1)
        new_fields = values.get("new_fields", False)
        model_name = values.get("model_name", False)
        if model_name and new_fields and len(new_fields):
            model_obj = self.env['ir.model'].search([('model', '=', model_name)])
            for newField in new_fields:
                if newField['t_type'.replace("_", "")] == "one2many":
                    self.create_m2o_from_o2m(newField)
                newField.update({'model_id': model_obj.id, 'state': 'manual'})
            # [new_field.update({'model_id': model_obj.id, 'state': 'manual'}) for new_field in new_fields]
            values['new_fields'] = [(0, 0, new_field) for new_field in new_fields]
        if len(views_exist) > 0:
            views_exist.write({'xml': values['xml'], 'new_fields': values['new_fields']})
        else:
            for attr in [x for x in values.keys() if x not in self._fields]:
                del values[attr]
            self.create(values)
        return True

    @api.model
    def undo_view(self, values):
        self.env['odo.studio.sub_view'].search([['parent_view_id', '=', values.get('view_id', False)]]).unlink()
        return self.search([['view_id', '=', values.get('view_id', False)]]).unlink()

    @api.model
    def load_field_get(self, model_name):
        return self.env[model_name].fields_get()


ODOOStudio()


class OdoStudioSubView(models.Model):
    _name = "odo.studio.sub_view"

    xml = fields.Text(string="Xml")
    view_key = fields.Char(string="View Key") # sale_order_field_order_line_list
    view_id = fields.Many2one(string="View id", comodel_name="ir.ui.view")
    parent_view_id = fields.Many2one(string="Parent View Id", comodel_name="ir.ui.view")
    parent_model_name = fields.Char(string="Parent Model Name")
    field_name = fields.Char(string="Field Name")
    view_type = fields.Selection([('tree', 'Tree'), ('form', 'Form')], string="View Type")
    new_fields = fields.Many2many('ir.model.fields', string="New Fields", copy=False)

    @api.model
    def store_view(self, values):
        views_exist = self.search([['view_key', '=', values.get('view_key', False)]])
        new_fields = values.get("new_fields", False)
        model_name = values.get("model_name", False)
        if model_name and new_fields and len(new_fields):
            model_obj = self.env['ir.model'].search([('model', '=', model_name)])
            [new_field.update({'model_id': model_obj.id, 'state': 'manual'}) for new_field in new_fields]
            values['new_fields'] = [(0, 0, new_field) for new_field in new_fields]
        for attr in [x for x in values.keys() if x not in self._fields]:
            del values[attr]
        if len(views_exist) > 0:
            views_exist.write(values)
        else:
            self.create(values)
        return True

    @api.model
    def undo_view(self, values):
        return self.search([['view_id', '=', values.get('view_id', False)], ['field_name', '=', values.get('field_name', False)],
                            ['parent_view_id', '=', values.get('parent_view_id', False)]]).unlink()


OdoStudioSubView()
