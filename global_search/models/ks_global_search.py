# Copyright (C) Softhealer Technologies.
from odoo import fields, models, api, _
FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]
from odoo.osv import expression
from odoo.exceptions import ValidationError



class GlobalSearch(models.Model):
    _inherit = 'global.search'
    _order = 'sequence'

    sequence = fields.Integer(string='Sequence')
    ks_icon = fields.Binary(string="Icon")
    file_name = fields.Char('File Name')

    # Method for add constrain. Code add by Manmohan Singh
    @api.constrains('sequence')
    def _check_sequence(self):
        rec = self.env['global.search'].search([('id', '!=', self.id)])
        for record in rec:
            if record.sequence == self.sequence:
                raise ValidationError(_("Sequence Already Exits"))

    # Method add for Search page Results. Code added by Manmohan Singh
    @api.model
    def ks_get_search_result(self, query):
        ks_rec = {}
        ks_menu = {}
        search_result = {}
        available_table = {}
        non_available_table = {}
        search_result_keys = {}
        table_icon = {}
        uniq_rec_set = set()

        if self.env.user.company_id.enable_menu_search:
            menu_roots = self.env['ir.ui.menu'].search([('parent_id', '=', False)])
            menu_data = self.env['ir.ui.menu'].search([('id', 'child_of', menu_roots.ids), ('name', 'ilike', query[0].lower()), ('action', '!=', False)])
            if menu_data:
                menu_data = menu_data._filter_visible_menus()
                for menu in menu_data:
                    ks_menu['menu| ' + menu.complete_name] = {'id': menu.id, 'action': menu.action.id, 'name': menu.complete_name}

        # if company id field is not in model
        for search_rec in self.env['global.search'].sudo().search([]):
            table_icon[search_rec.display_name] = search_rec.ks_icon
            # All Field List including name field
            normal_fields_list = []
            m2o_fields_list = []
            o2m_fields_list = []

            for fields in search_rec.global_field_ids:
                field = fields.field_id
                if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float', 'integer', 'selection', 'monetary', 'html']:
                    normal_fields_list.append(field)
                elif field.ttype in ['many2one']:
                    if search_rec.main_field_id not in m2o_fields_list:
                        m2o_fields_list.append(search_rec.main_field_id)
                    m2o_fields_list.append(field)
                elif field.ttype in ['one2many']:
                    o2m_fields_list.append(field)

            # Fetch all record of this current model with defined field list
            try:
                # check company_id field in model
                company_id_field = self.env['ir.model.fields'].sudo().search(
                    [('name', '=', 'company_id'), ('model_id', '=', search_rec.model_id.id)])

                if not company_id_field:
                    if normal_fields_list:
                        normal_fields = []
                        domain = []
                        count = 0
                        for field_row in normal_fields_list:
                            field = field_row.name
                            normal_fields.append(field)
                            if field != 'display_name':
                                domain.append((field, 'ilike', query[0]))
                            else:
                                count += 1
                        if normal_fields:
                            model_obj = self.env[search_rec.model_id.model].search_read(domain, order='id')
                            for model_rec in model_obj:

                                for field_row in normal_fields_list:
                                    field = field_row
                                    if model_rec.get(field.name):
                                        object_data = model_rec.get(field.name)
                                        # soup = BeautifulSoup(object_data)
                                        # object_data = soup.get_text()
                                        non_available_table[field.model_id.name] = search_rec.ks_icon
                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            field_dict = {}
                                            field_key = {}

                                            for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                            for obj_fields in m2o_fields_list:
                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                            for obj_fields in normal_fields_list:
                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                            if field.model_id.name not in search_result:
                                                search_result_keys[field.model_id.name] = field_key
                                                available_table[field.model_id.name] = search_rec.ks_icon

                                            model_rec['model'] = field.model_id.model
                                            model_rec['model_name'] = field.model_id.name
                                            current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])

                                            if current_rec not in uniq_rec_set:
                                                uniq_rec_set.add(current_rec)
                                                search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                search_result[self.env.user.company_id.name + '|' + search_result_record + ' > ' + str(list(field_dict.values()))] = model_rec

                        if count != 0:
                            field_list = ['display_name']
                            model_obj = self.env[search_rec.model_id.model].search_read([], field_list, order='id')

                            for model_rec in model_obj:

                                if model_rec.get('display_name'):
                                    object_data = model_rec.get('display_name')
                                    non_available_table[field.model_id.name] = search_rec.ks_icon

                                    if object_data and query[0].lower() in str(object_data).casefold():
                                        field_dict = {}
                                        field_key = {}

                                        for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                            field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                        for obj_fields in m2o_fields_list:
                                            field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                        for obj_fields in normal_fields_list:
                                            field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                        if field.model_id.name not in search_result:
                                            search_result_keys[field.model_id.name] = field_key
                                            available_table[field.model_id.name] = search_rec.ks_icon

                                        model_rec['model'] = search_rec.model_id.model
                                        model_rec['model_name'] = search_rec.model_id.name
                                        current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])

                                        if current_rec not in uniq_rec_set:
                                            uniq_rec_set.add(current_rec)
                                            search_result[self.env.user.company_id.name + '|' + "Display Name" + ' : ' + str(list(field_dict.values()))] = model_rec
                    if m2o_fields_list:
                        m2o_fields = []
                        domain = []

                        for field_row in m2o_fields_list:
                            field = field_row.name
                            m2o_fields.append(field)
                            domain.append(('%s.name' % (field), 'ilike', query[0]))

                        model_obj = self.env[search_rec.model_id.model].search_read(domain, order='id')
                        for model_rec in model_obj:

                            for field_row in m2o_fields_list:
                                field = field_row

                                if field.name != 'display_name':

                                    if model_rec.get(field.name):
                                        object_data = model_rec.get(field.name)
                                        non_available_table[field.model_id.name] = search_rec.ks_icon

                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            field_dict = {}
                                            field_key = {}

                                            for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                            for obj_fields in m2o_fields_list:
                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                            for obj_fields in normal_fields_list:
                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                            if field.model_id.name not in search_result:
                                                search_result_keys[field.model_id.name] = field_key
                                                available_table[field.model_id.name] = search_rec.ks_icon

                                            model_rec['model'] = field.model_id.model
                                            model_rec['model_name'] = field.model_id.name
                                            current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])

                                            if current_rec not in uniq_rec_set:
                                                uniq_rec_set.add(current_rec)
                                                search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                search_result[self.env.user.company_id.name + '|' + search_result_record + ' > ' + str(list(field_dict.values()))] = model_rec

                    if o2m_fields_list:

                        for super_field_row in o2m_fields_list:
                            field = super_field_row.field_id.name
                            inside_normal_fields = []
                            inside_m2o_field_list = []

                            for o2m_field in super_field_row.field_ids:
                                field = o2m_field.field_id

                                if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float', 'integer',
                                                   'selection', 'monetary', 'html']:
                                    inside_normal_fields.append(field)
                                elif field.ttype in ['many2one']:
                                    inside_m2o_field_list.append(field)
                                    if search_rec.main_field_id not in inside_m2o_field_list:
                                        inside_m2o_field_list.append(search_rec.main_field_id)
                                if search_rec.main_field_id not in inside_normal_fields:
                                    inside_normal_fields.append(search_rec.main_field_id)

                        if inside_normal_fields:
                            normal_fields = []
                            domain = []

                            for field_row in inside_normal_fields:
                                field = field_row.name
                                normal_fields.append(field)
                                domain.append((field, 'ilike', query[0]))

                            model_obj = self.env[search_rec.model_id.model].search_read(domain, order='id')
                            for model_rec in model_obj:

                                for field_row in inside_normal_fields:
                                    field = field_row

                                    if model_rec.get(field.name):
                                        object_data = model_rec.get(field.name)

                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            field_dict = {}
                                            field_key = {}

                                            for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                            for obj_fields in m2o_fields_list:
                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                            for obj_fields in normal_fields_list:
                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                            if field.model_id.name not in search_result:
                                                search_result_keys[field.model_id.name] = field_key

                                            some_id = model_rec['id']
                                            some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                            parent_obj = getattr(some_record, super_field_row.field_id.relation_field)
                                            model_rec['model'] = parent_obj._name
                                            model_rec['model_name'] = parent_obj._name.upper()
                                            model_rec['id'] = parent_obj.id
                                            search_result[self.env.user.company_id.name + '|' + parent_obj.name + ' > ' + str(list(field_dict.values()))] = model_rec

                        if inside_m2o_field_list:
                            m2o_fields = []
                            domain = []

                            for field_row in inside_m2o_field_list:
                                field = field_row.name
                                m2o_fields.append(field)
                                domain.append(('%s.name' % (field), 'ilike', query[0]))

                            model_obj = self.env[search_rec.model_id.model].search_read(domain, order='id')
                            for model_rec in model_obj:

                                for field_row in inside_m2o_field_list:
                                    field = field_row

                                    if field.name != 'display_name':

                                        if model_rec.get(field.name):
                                            object_data = model_rec.get(field.name)

                                            if object_data and query[0].lower() in str(object_data).casefold():
                                                field_dict = {}
                                                field_key = {}

                                                for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                    field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                                for obj_fields in m2o_fields_list:
                                                    field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                                for obj_fields in normal_fields_list:
                                                    field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                                if field.model_id.name not in search_result:
                                                    search_result_keys[field.model_id.name] = field_key

                                                some_id = model_rec['id']
                                                some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                                parent_obj = getattr(some_record, super_field_row.field_id.relation_field)
                                                model_rec['model'] = parent_obj._name
                                                model_rec['model_name'] = parent_obj._name.upper()
                                                model_rec['id'] = parent_obj.id
                                                search_result[self.env.user.company_id.name + '|' + parent_obj.name + ' > ' + str(list(field_dict.values()))] = model_rec

            except Exception as e:
                print(e)

        # if company id field is in model
        # All Global Search Records
        count = 1
        for company in self.env['res.company'].search([]):

            if company.id in self.env.context.get('allowed_company_ids'):

                for search_rec in self.env['global.search'].sudo().search([]):
                    table_icon[search_rec.display_name] = search_rec.ks_icon
                    # All Field List including name field
                    field_list = []

                    for field in search_rec.global_field_ids:
                        field_list.append(field.field_id.name)

                    if search_rec.main_field_id.name not in field_list:
                        field_list.append(search_rec.main_field_id.name)

                    normal_fields_list = []
                    m2o_fields_list = []
                    o2m_fields_list = []
                    external_addition = 0

                    for fields in search_rec.global_field_ids:
                        field = fields.field_id

                        if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float', 'integer',
                                           'selection', 'monetary', 'html']:
                            normal_fields_list.append(field)
                        elif field.ttype in ['many2one']:
                            m2o_fields_list.append(field)
                        elif field.ttype in ['one2many']:
                            o2m_fields_list.append(fields)

                    if search_rec.main_field_id not in m2o_fields_list:
                        m2o_fields_list.append(search_rec.main_field_id)

                    if search_rec.main_field_id not in normal_fields_list:
                        external_addition += 1
                        normal_fields_list.append(search_rec.main_field_id)

                    try:
                        # check company_id field in model
                        company_id_field = self.env['ir.model.fields'].sudo().search(
                            [('name', '=', 'company_id'), ('model_id', '=', search_rec.model_id.id)])

                        if company_id_field:

                            if normal_fields_list:
                                normal_fields = [field_row.name for field_row in normal_fields_list]
                                domain_multi_company = [('company_id', 'in', [company.id, False])]
                                field_domain = expression.OR(
                                    [[(field_row.name, 'ilike', query[0])] for field_row in normal_fields_list if
                                     field_row.name != 'display_name'])
                                domain = expression.AND([domain_multi_company, field_domain])

                                if normal_fields:
                                    model_obj = self.env[search_rec.model_id.model].search_read(domain, order='id')

                                    for model_rec in model_obj:

                                        for field_row in normal_fields_list:
                                            field = field_row

                                            if field.name != 'display_name':

                                                if model_rec.get(field.name):
                                                    object_data = model_rec.get(field.name)
                                                    # soup = BeautifulSoup(object_data)
                                                    # object_data = soup.get_text()
                                                    non_available_table[field.model_id.name] = search_rec.ks_icon
                                                    if object_data and query[0].lower() in str(object_data).casefold():
                                                        field_dict = {}
                                                        field_key = {}
                                                        # if model_rec.get(obj_fields.name):

                                                        for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                            field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                                        for obj_fields in m2o_fields_list:
                                                            if model_rec.get(obj_fields.name):
                                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]
                                                            else:
                                                                field_dict[obj_fields.field_description] = ''
                                                            # field_key[obj_fields.name] = obj_fields.field_description

                                                        for obj_fields in normal_fields_list:
                                                            field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)
                                                        if field.model_id.name not in search_result:
                                                            available_table[field.model_id.name] = search_rec.ks_icon
                                                            search_result_keys[field.model_id.name] = field_key

                                                        model_rec['model'] = field.model_id.model
                                                        model_rec['model_name'] = field.model_id.name
                                                        current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                        if current_rec not in uniq_rec_set:
                                                            uniq_rec_set.add(current_rec)
                                                            search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                            search_result[company.name + '|' + search_result_record + ' > ' + str(list(field_dict.values()))] = model_rec

                                if external_addition == 0:
                                    model_obj = self.env[search_rec.model_id.model].search_read(
                                        ['|', ('company_id', '=', company.id), ('company_id', '=', False)], order='id')

                                    for model_rec in model_obj:

                                        if model_rec.get('display_name'):
                                            object_data = model_rec.get('display_name')
                                            non_available_table[field.model_id.name] = search_rec.ks_icon

                                            if object_data and query[0].lower() in str(object_data).casefold():
                                                field_dict = {}
                                                field_key = {}

                                                for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                    field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                                for obj_fields in m2o_fields_list:
                                                    if model_rec.get(obj_fields.name):
                                                        field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]
                                                    else:
                                                        field_dict[obj_fields.field_description] = ''

                                                for obj_fields in normal_fields_list:
                                                    field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                                if field.model_id.name not in search_result:
                                                    search_result_keys[field.model_id.name] = field_key
                                                    available_table[field.model_id.name] = search_rec.ks_icon

                                                model_rec['model'] = search_rec.model_id.model
                                                model_rec['model_name'] = search_rec.model_id.name
                                                current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                if current_rec not in uniq_rec_set:
                                                    uniq_rec_set.add(current_rec)
                                                    search_result[company.name + '|' + "Display Name" + ' : ' + str(list(field_dict.values()))] = model_rec

                            if m2o_fields_list:
                                domain_multi_company = [('company_id', 'in', [company.id, False])]
                                field_domain = expression.OR(
                                    [[('%s.name' % (field_row.name), 'ilike', query[0])] for field_row in
                                     m2o_fields_list if field_row.name != 'display_name'])
                                domain = expression.AND([domain_multi_company, field_domain])
                                model_obj = self.env[search_rec.model_id.model].search_read(domain, order='id')
                                for model_rec in model_obj:

                                    for field_row in m2o_fields_list:
                                        field = field_row

                                        if field.name != 'display_name':

                                            if model_rec.get(field.name):
                                                object_data = model_rec.get(field.name)
                                                non_available_table[field.model_id.name] = search_rec.ks_icon

                                                if object_data and query[0].lower() in str(object_data[1]).casefold():
                                                    field_dict = {}
                                                    field_key = {}

                                                    for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                        field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                                    for obj_fields in m2o_fields_list:
                                                        field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                                    for obj_fields in normal_fields_list:
                                                        field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                                    if field.model_id.name not in search_result:
                                                        available_table[field.model_id.name] = search_rec.ks_icon
                                                        search_result_keys[field.model_id.name] = field_key

                                                    model_rec['model'] = field.model_id.model
                                                    model_rec['model_name'] = field.model_id.name
                                                    current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                    if current_rec not in uniq_rec_set:
                                                        uniq_rec_set.add(current_rec)
                                                        search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                        search_result[company.name + '|' + search_result_record + ' > ' + str(list(field_dict.values()))] = model_rec

                            if o2m_fields_list:
                                for super_field_row in o2m_fields_list:
                                    field = super_field_row.field_id.name
                                    inside_normal_fields = []
                                    inside_m2o_field_list = []

                                    for o2m_field in super_field_row.field_ids:
                                        field = o2m_field.field_id
                                        if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float',
                                                           'integer', 'selection', 'monetary', 'html']:
                                            inside_normal_fields.append(field)
                                        elif field.ttype in ['many2one']:
                                            if search_rec.main_field_id not in inside_m2o_field_list:
                                                inside_m2o_field_list.append(search_rec.main_field_id)
                                            inside_m2o_field_list.append(field)
                                        if search_rec.main_field_id not in inside_normal_fields:
                                            inside_normal_fields.append(search_rec.main_field_id)

                                    if inside_normal_fields:
                                        domain_multi_company = [('company_id', 'in', [company.id, False])]
                                        field_domain = expression.OR(
                                            [[(field_row.name, 'ilike', query[0])] for field_row in inside_normal_fields
                                             if field_row.name != 'display_name'])
                                        domain = expression.AND([domain_multi_company, field_domain])
                                        model_obj = self.env[super_field_row.related_model_id].search_read(domain,
                                                                                                           order='id')
                                        for model_rec in model_obj:

                                            for field_row in inside_normal_fields:
                                                field = field_row

                                                if model_rec.get(field.name):
                                                    object_data = model_rec.get(field.name)
                                                    if object_data and query[0].lower() in str(object_data).casefold():
                                                        field_dict = {}
                                                        field_key = {}
                                                        for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                            field_key[field_seq.field_id.name] = field_seq.field_id.field_description
                                                        for obj_fields in m2o_fields_list:
                                                            field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]
                                                        for obj_fields in normal_fields_list:
                                                            field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)
                                                        if field.model_id.name not in search_result:
                                                            search_result_keys[field.model_id.name] = field_key
                                                        some_id = model_rec['id']
                                                        some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                                        parent_obj = getattr(some_record, super_field_row.field_id.relation_field)
                                                        model_rec['model'] = parent_obj._name
                                                        model_rec['model_name'] = parent_obj._name.upper()
                                                        model_rec['id'] = parent_obj.id
                                                        search_result[company.name + '|' + parent_obj.name + ' > ' + str(list(field_dict.values()))] = model_rec

                                    if inside_m2o_field_list:
                                        m2o_fields = [field_row.name for field_row in inside_m2o_field_list]
                                        domain_multi_company = [('company_id', 'in', [company.id, False])]
                                        if len(m2o_fields) > 1:
                                            field_domain = expression.OR(
                                                [[('%s.name' % (field_row.name), 'ilike', query[0])] for field_row in
                                                 inside_m2o_field_list if field_row.name != 'display_name'])
                                        else:
                                            field_domain = ([('%s.name' % (field_row.name), 'ilike', query[0])] for
                                                            field_row in m2o_fields)
                                        domain = expression.AND([domain_multi_company, field_domain])
                                        model_obj = self.env[super_field_row.related_model_id].search_read(domain,
                                                                                                           order='id')
                                        for model_rec in model_obj:

                                            for field_row in inside_m2o_field_list:
                                                field = field_row

                                                if field.name != 'display_name':

                                                    if model_rec.get(field.name):
                                                        object_data = model_rec.get(field.name)

                                                        if object_data and query[0].lower() in str(object_data[1]).casefold():
                                                            field_dict = {}
                                                            field_key = {}

                                                            for field_seq in search_rec.global_field_ids.sorted(lambda p: p.sequence):
                                                                field_key[field_seq.field_id.name] = field_seq.field_id.field_description

                                                            for obj_fields in m2o_fields_list:
                                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)[1]

                                                            for obj_fields in normal_fields_list:
                                                                field_dict[obj_fields.field_description] = model_rec.get(obj_fields.name)

                                                            if field.model_id.name not in search_result:
                                                                search_result_keys[field.model_id.name] = field_key

                                                            some_id = model_rec['id']
                                                            some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                                            parent_obj = getattr(some_record, super_field_row.field_id.relation_field)
                                                            model_rec['model'] = parent_obj._name
                                                            model_rec['model_name'] = parent_obj._name.upper()
                                                            model_rec['id'] = parent_obj.id
                                                            search_result[company.name + '|' + parent_obj.name + ' > ' + str(list(field_dict.values()))] = model_rec
                    except Exception as e:
                        print(e)

        ks_rec['search_result'] = search_result
        ks_rec['search_result_keys'] = search_result_keys
        ks_rec['search_result_menu'] = ks_menu
        ks_menu_record = {}
        dict_key = ''

        for rec in search_result:
            if search_result[rec]['model_name'] not in ks_menu_record:
                ks_menu_record[search_result[rec]['model_name']] = {}
                dict_key = str(search_result[rec]['model_name'])
            if str(search_result[rec]['model_name']) == dict_key:
                ks_menu_record[search_result[rec]['model_name']][rec] = search_result[rec]

        ks_rec['ks_menu_record'] = ks_menu_record
        ks_rec['table_icon'] = table_icon

        def r_table(non_available_table, available_table):
            dict={}
            for key,value in non_available_table.items():
                if key not in available_table:
                    dict[key] = value
            return dict

        remain_table = r_table(non_available_table,available_table)
        ks_rec['remain_table'] = remain_table

        return ks_rec

    # Method inherit for Search bar suggestions and change result format. Code added by Manmohan Singh
    @api.model
    def get_search_result(self, query):
        search_result = {}
        table_icon = {}
        ks_rec = {}
        uniq_rec_set = set()
        uniq_rec_set_count = set()
        ks_search_result = {}

        if self.env.user.company_id.enable_menu_search:
            menu_roots = self.env['ir.ui.menu'].search([('parent_id', '=', False)])
            menu_data = self.env['ir.ui.menu'].search(
                [('id', 'child_of', menu_roots.ids), ('name', 'ilike', query[0].lower()), ('action', '!=', False)])
            if menu_data:
                menu_data = menu_data._filter_visible_menus()
                for menu in menu_data:
                    search_result['menu| ' + menu.complete_name] = {'id': menu.id, 'action': menu.action.id,
                                                                    'name': menu.complete_name}

        # if company id field is not in model
        for search_rec in self.env['global.search'].sudo().search([], limit=5):
            # All Field List including name field
            table_icon[search_rec.display_name] = search_rec.ks_icon
            normal_fields_list = []
            m2o_fields_list = []
            o2m_fields_list = []
            limit_count = 0

            for fields in search_rec.global_field_ids:
                field = fields.field_id

                if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float', 'integer', 'selection', 'monetary', 'html']:
                    normal_fields_list.append(field)
                elif field.ttype in ['many2one']:
                    if search_rec.main_field_id not in m2o_fields_list:
                        m2o_fields_list.append(search_rec.main_field_id)
                    m2o_fields_list.append(field)
                elif field.ttype in ['one2many']:
                    o2m_fields_list.append(field)

            # Fetch all record of this current model with defined field list
            try:
                # check company_id field in model
                company_id_field = self.env['ir.model.fields'].sudo().search([('name', '=', 'company_id'), ('model_id', '=', search_rec.model_id.id)])
                if not company_id_field:
                    if normal_fields_list:
                        normal_fields = []
                        domain = []
                        count = 0

                        for field_row in normal_fields_list:
                            field = field_row.name
                            normal_fields.append(field)
                            if field != 'display_name':
                                domain.append((field, 'ilike', query[0]))
                            else:
                                count += 1

                        if normal_fields:
                            model_obj = self.env[search_rec.model_id.model].search_read(domain, normal_fields,order='id')

                            for model_rec in model_obj:

                                for field_row in normal_fields_list:
                                    field = field_row

                                    if model_rec.get(field.name):
                                        object_data = model_rec.get(field.name)
                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            model_rec['model'] = field.model_id.model
                                            model_rec['model_name'] = field.model_id.name
                                            search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                            current_rec_count = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                            if current_rec_count not in uniq_rec_set_count:
                                                uniq_rec_set_count.add(current_rec_count)
                                                ks_search_result[self.env.user.company_id.name + '|' +search_result_record+' > '+ field.field_description + ' : ' + str(object_data)] = model_rec

                                    if model_rec.get(field.name) and limit_count < 5:
                                        object_data = model_rec.get(field.name)
                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            model_rec['model'] = field.model_id.model
                                            model_rec['model_name'] = field.model_id.name
                                            current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                            if current_rec not in uniq_rec_set:
                                                uniq_rec_set.add(current_rec)
                                                search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                search_result[self.env.user.company_id.name + '|' +search_result_record+' > '+ field.field_description + ' : ' + str(object_data)] = model_rec
                                                limit_count = limit_count + 1

                        if count != 0:
                            field_list = ['display_name']
                            model_obj = self.env[search_rec.model_id.model].search_read([], field_list, order='id')
                            for model_rec in model_obj:

                                if model_rec.get(field.name):
                                    object_data = model_rec.get(field.name)
                                    if object_data and query[0].lower() in str(object_data).casefold():
                                        model_rec['model'] = field.model_id.model
                                        model_rec['model_name'] = field.model_id.name
                                        search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                        current_rec_count = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                        if current_rec_count not in uniq_rec_set_count:
                                            uniq_rec_set_count.add(current_rec_count)
                                            ks_search_result[self.env.user.company_id.name + '|' + search_result_record + ' > ' + field.field_description + ' : ' + str(object_data)] = model_rec

                                if model_rec.get('display_name') and limit_count < 5:
                                    object_data = model_rec.get('display_name')
                                    if object_data and query[0].lower() in str(object_data).casefold():
                                        model_rec['model'] = search_rec.model_id.model
                                        model_rec['model_name'] = search_rec.model_id.name
                                        current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                        if current_rec not in uniq_rec_set:
                                            uniq_rec_set.add(current_rec)
                                            search_result[self.env.user.company_id.name + '|' + "Display Name" + ' : ' + str(object_data)] = model_rec
                                            limit_count = limit_count + 1

                    if m2o_fields_list:
                        m2o_fields = []
                        domain = []

                        for field_row in m2o_fields_list:
                            field = field_row.name
                            m2o_fields.append(field)
                            domain.append(('%s.name' % (field), 'ilike', query[0]))

                        model_obj = self.env[search_rec.model_id.model].search_read(domain, m2o_fields, order='id')
                        for model_rec in model_obj:

                            for field_row in m2o_fields_list:
                                field = field_row

                                if field.name != 'display_name':

                                    if model_rec.get(field.name):
                                        object_data = model_rec.get(field.name)
                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            model_rec['model'] = field.model_id.model
                                            model_rec['model_name'] = field.model_id.name
                                            search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                            current_rec_count = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                            if current_rec_count not in uniq_rec_set_count:
                                                uniq_rec_set_count.add(current_rec_count)
                                                ks_search_result[self.env.user.company_id.name + '|' +search_result_record+' > '+ field.field_description + ' : ' + str(object_data)] = model_rec

                                    if model_rec.get(field.name) and limit_count < 5:
                                        object_data = model_rec.get(field.name)
                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            model_rec['model'] = field.model_id.model
                                            model_rec['model_name'] = field.model_id.name
                                            current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                            if current_rec not in uniq_rec_set:
                                                uniq_rec_set.add(current_rec)
                                                search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                str_object_data = str(object_data[1])
                                                search_result[self.env.user.company_id.name + '|' +search_result_record+' > '+ field.field_description + ' : ' + str_object_data] = model_rec
                                                limit_count = limit_count + 1
                    if o2m_fields_list:

                        for super_field_row in o2m_fields_list:
                            field = super_field_row.field_id.name
                            inside_normal_fields = []
                            inside_m2o_field_list = []

                            for o2m_field in super_field_row.field_ids:
                                field = o2m_field.field_id
                                if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float', 'integer',
                                                   'selection', 'monetary', 'html']:
                                    inside_normal_fields.append(field)
                                elif field.ttype in ['many2one']:
                                    inside_m2o_field_list.append(field)
                                    if search_rec.main_field_id not in inside_m2o_field_list:
                                        inside_m2o_field_list.append(search_rec.main_field_id)
                                if search_rec.main_field_id not in inside_normal_fields:
                                    inside_normal_fields.append(search_rec.main_field_id)

                        if inside_normal_fields:
                            normal_fields = []
                            domain = []
                            for field_row in inside_normal_fields:
                                field = field_row.name
                                normal_fields.append(field)
                                domain.append((field, 'ilike', query[0]))

                            model_obj = self.env[search_rec.model_id.model].search_read(domain, normal_fields,order='id')
                            for model_rec in model_obj:
                                for field_row in inside_normal_fields:
                                    field = field_row
                                    if model_rec.get(field.name) and limit_count < 5:
                                        object_data = model_rec.get(field.name)
                                        if object_data and query[0].lower() in str(object_data).casefold():
                                            some_id = model_rec['id']
                                            some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                            search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                            parent_obj = getattr(some_record, super_field_row.field_id.relation_field)
                                            model_rec['model'] = parent_obj._name
                                            model_rec['model_name'] = parent_obj._name.upper()
                                            model_rec['id'] = parent_obj.id
                                            str_object_data = str(object_data)
                                            search_result[self.env.user.company_id.name + '|' +search_result_record+' > '+ field.field_description + ' : ' + str_object_data] = model_rec
                                            limit_count = limit_count + 1

                        if inside_m2o_field_list:
                            m2o_fields = []
                            domain = []

                            for field_row in inside_m2o_field_list:
                                field = field_row.name
                                m2o_fields.append(field)
                                domain.append(('%s.name' % (field), 'ilike', query[0]))

                            model_obj = self.env[search_rec.model_id.model].search_read(domain, m2o_fields, order='id')
                            for model_rec in model_obj:

                                for field_row in inside_m2o_field_list:
                                    field = field_row

                                    if field.name != 'display_name':
                                        if model_rec.get(field.name) and limit_count < 5:
                                            object_data = model_rec.get(field.name)
                                            if object_data and query[0].lower() in str(object_data).casefold():
                                                some_id = model_rec['id']
                                                some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                                search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                parent_obj = getattr(some_record,super_field_row.field_id.relation_field)
                                                model_rec['model'] = parent_obj._name
                                                model_rec['model_name'] = parent_obj._name.upper()
                                                model_rec['id'] = parent_obj.id
                                                str_object_data = str(object_data[1])
                                                search_result[self.env.user.company_id.name + '|'+search_result_record+' > ' + field.field_description + ' : ' + str_object_data] = model_rec
                                                limit_count = limit_count + 1

            except Exception as e:
                print(e)

        # if company id field is in model
        # All Global Search Records
        count = 1
        for company in self.env['res.company'].search([]):

            if company.id in self.env.context.get('allowed_company_ids'):

                for search_rec in self.env['global.search'].sudo().search([], limit=5):
                    # All Field List including name field
                    table_icon[search_rec.display_name] = search_rec.ks_icon
                    field_list = []

                    for field in search_rec.global_field_ids:
                        field_list.append(field.field_id.name)

                    if search_rec.main_field_id.name not in field_list:
                        field_list.append(search_rec.main_field_id.name)
                    normal_fields_list = []
                    m2o_fields_list = []
                    o2m_fields_list = []
                    external_addition = 0
                    limit_count = 0

                    for fields in search_rec.global_field_ids:
                        field = fields.field_id
                        if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float', 'integer',
                                           'selection', 'monetary', 'html']:
                            normal_fields_list.append(field)
                        elif field.ttype in ['many2one']:
                            m2o_fields_list.append(field)
                        elif field.ttype in ['one2many']:
                            o2m_fields_list.append(fields)

                    if search_rec.main_field_id not in m2o_fields_list:
                        m2o_fields_list.append(search_rec.main_field_id)

                    if search_rec.main_field_id not in normal_fields_list:
                        external_addition += 1
                        normal_fields_list.append(search_rec.main_field_id)
                    try:
                        # check company_id field in model
                        company_id_field = self.env['ir.model.fields'].sudo().search(
                            [('name', '=', 'company_id'), ('model_id', '=', search_rec.model_id.id)])

                        if company_id_field:

                            if normal_fields_list:
                                normal_fields = [field_row.name for field_row in normal_fields_list]
                                domain = []
                                domain_multi_company = [('company_id', 'in', [company.id, False])]
                                field_domain = expression.OR(
                                    [[(field_row.name, 'ilike', query[0])] for field_row in normal_fields_list if
                                     field_row.name != 'display_name'])
                                domain = expression.AND([domain_multi_company, field_domain])

                                if normal_fields:
                                    model_obj = self.env[search_rec.model_id.model].search_read(domain, normal_fields,order='id')
                                    for model_rec in model_obj:

                                        for field_row in normal_fields_list:
                                            field = field_row
                                            if field.name != 'display_name':
                                                if model_rec.get(field.name):
                                                    object_data = model_rec.get(field.name)
                                                    if object_data and query[0].lower() in str(object_data).casefold():
                                                        model_rec['model'] = field.model_id.model
                                                        model_rec['model_name'] = field.model_id.name
                                                        search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                        current_rec_count = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                        if current_rec_count not in uniq_rec_set_count:
                                                            uniq_rec_set_count.add(current_rec_count)
                                                            ks_search_result[self.env.user.company_id.name + '|' + search_result_record + ' > ' + field.field_description + ' : ' + str(object_data)] = model_rec

                                                if model_rec.get(field.name) and limit_count < 5:
                                                    object_data = model_rec.get(field.name)
                                                    if object_data and query[0].lower() in str(object_data).casefold(): #event
                                                        model_rec['model'] = field.model_id.model
                                                        model_rec['model_name'] = field.model_id.name
                                                        current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                        if current_rec not in uniq_rec_set:
                                                            uniq_rec_set.add(current_rec)
                                                            search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                            search_result[company.name + '|' +search_result_record+' > '+ field.field_description + ' : ' + str(object_data)] = model_rec
                                                            limit_count = limit_count + 1

                                if external_addition == 0:
                                    field_list = ['display_name']
                                    model_obj = self.env[search_rec.model_id.model].search_read(['|', ('company_id', '=', company.id), ('company_id', '=', False)], field_list,order='id')
                                    for model_rec in model_obj:
                                        if model_rec.get('display_name'):
                                            object_data = model_rec.get('display_name')
                                            if object_data and query[0].lower() in str(object_data).casefold():
                                                model_rec['model'] = field.model_id.model
                                                model_rec['model_name'] = field.model_id.name
                                                search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                current_rec_count = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                if current_rec_count not in uniq_rec_set_count:
                                                    uniq_rec_set_count.add(current_rec_count)
                                                    ks_search_result[self.env.user.company_id.name + '|' + search_result_record + ' > ' + field.field_description + ' : ' + str(object_data)] = model_rec

                                        if model_rec.get('display_name') and limit_count < 5:
                                            object_data = model_rec.get('display_name')
                                            if object_data and query[0].lower() in str(object_data).casefold():  #product
                                                model_rec['model'] = search_rec.model_id.model
                                                model_rec['model_name'] = search_rec.model_id.name
                                                current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                if current_rec not in uniq_rec_set:
                                                    uniq_rec_set.add(current_rec)
                                                    search_result[company.name + '|' + "Display Name" + ' : ' + str(object_data)] = model_rec
                                                    limit_count = limit_count + 1

                            if m2o_fields_list:
                                m2o_fields = [field_row.name for field_row in m2o_fields_list]
                                domain = []
                                domain_multi_company = [('company_id', 'in', [company.id, False])]
                                field_domain = expression.OR(
                                    [[('%s.name' % (field_row.name), 'ilike', query[0])] for field_row in
                                     m2o_fields_list if field_row.name != 'display_name'])
                                domain = expression.AND([domain_multi_company, field_domain])
                                model_obj = self.env[search_rec.model_id.model].search_read(domain, m2o_fields,order='id')

                                for model_rec in model_obj:

                                    for field_row in m2o_fields_list:
                                        field = field_row

                                        if field.name != 'display_name':
                                            if model_rec.get(field.name):
                                                object_data = model_rec.get(field.name)
                                                if object_data and query[0].lower() in str(object_data).casefold():
                                                    model_rec['model'] = field.model_id.model
                                                    model_rec['model_name'] = field.model_id.name
                                                    search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                    current_rec_count = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                    if current_rec not in uniq_rec_set_count:
                                                        uniq_rec_set_count.add(current_rec_count)
                                                        ks_search_result[self.env.user.company_id.name + '|' + search_result_record + ' > ' + field.field_description + ' : ' + str(object_data)] = model_rec

                                            if model_rec.get(field.name) and limit_count < 5:
                                                object_data = model_rec.get(field.name)
                                                if object_data and query[0].lower() in str(object_data[1]).casefold():
                                                    model_rec['model'] = field.model_id.model
                                                    model_rec['model_name'] = field.model_id.name
                                                    search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                    str_object_data = str(object_data[1])
                                                    current_rec = str(search_rec.model_id.id) + str(model_rec['model_name']) + str(model_rec['display_name'])
                                                    if current_rec not in uniq_rec_set:
                                                        uniq_rec_set.add(current_rec)
                                                        search_result[company.name + '|'+search_result_record+' > ' + field.field_description + ' : ' + str_object_data] = model_rec
                                                        limit_count = limit_count + 1

                            if o2m_fields_list:
                                for super_field_row in o2m_fields_list:
                                    field = super_field_row.field_id.name
                                    inside_normal_fields = []
                                    inside_m2o_field_list = []

                                    for o2m_field in super_field_row.field_ids:
                                        field = o2m_field.field_id

                                        if field.ttype in ['char', 'boolean', 'text', 'date', 'datetime', 'float',
                                                           'integer', 'selection', 'monetary', 'html']:
                                            inside_normal_fields.append(field)
                                        elif field.ttype in ['many2one']:
                                            if search_rec.main_field_id not in inside_m2o_field_list:
                                                inside_m2o_field_list.append(search_rec.main_field_id)
                                            inside_m2o_field_list.append(field)
                                        if search_rec.main_field_id not in inside_normal_fields:
                                            inside_normal_fields.append(search_rec.main_field_id)

                                    if inside_normal_fields:
                                        normal_fields = [field_row.name for field_row in inside_normal_fields]
                                        domain = []
                                        domain_multi_company = [('company_id', 'in', [company.id, False])]
                                        field_domain = expression.OR(
                                            [[(field_row.name, 'ilike', query[0])] for field_row in inside_normal_fields
                                             if field_row.name != 'display_name'])
                                        domain = expression.AND([domain_multi_company, field_domain])
                                        model_obj = self.env[super_field_row.related_model_id].search_read(domain,normal_fields,order='id')

                                        for model_rec in model_obj:
                                            for field_row in inside_normal_fields:
                                                field = field_row
                                                if model_rec.get(field.name) and limit_count < 5:
                                                    object_data = model_rec.get(field.name)
                                                    if object_data and query[0].lower() in str(object_data).casefold():
                                                        some_id = model_rec['id']
                                                        some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                                        search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                        parent_obj = getattr(some_record,super_field_row.field_id.relation_field)
                                                        model_rec['model'] = parent_obj._name
                                                        model_rec['model_name'] = parent_obj._name.upper()
                                                        model_rec['id'] = parent_obj.id
                                                        str_object_data = str(object_data)
                                                        search_result[company.name + '|'+search_result_record+' > ' + field.field_description + ' : ' + str_object_data] = model_rec
                                                        limit_count = limit_count + 1

                                    if inside_m2o_field_list:
                                        m2o_fields = [field_row.name for field_row in inside_m2o_field_list]
                                        domain = []
                                        domain_multi_company = [('company_id', 'in', [company.id, False])]
                                        if len(m2o_fields) > 1:
                                            field_domain = expression.OR(
                                                [[('%s.name' % (field_row.name), 'ilike', query[0])] for field_row in
                                                 inside_m2o_field_list if field_row.name != 'display_name'])
                                        else:
                                            field_domain = ([('%s.name' % (field_row.name), 'ilike', query[0])] for field_row in m2o_fields)

                                        domain = expression.AND([domain_multi_company, field_domain])
                                        model_obj = self.env[super_field_row.related_model_id].search_read(domain,m2o_fields,order='id')
                                        for model_rec in model_obj:

                                            for field_row in inside_m2o_field_list:
                                                field = field_row
                                                if field.name != 'display_name':
                                                    if model_rec.get(field.name) and limit_count < 5:
                                                        object_data = model_rec.get(field.name)
                                                        if object_data and query[0].lower() in str(object_data[1]).casefold():
                                                            some_id = model_rec['id']
                                                            some_record = self.env[super_field_row.model_id.model].browse(some_id)
                                                            search_result_record = model_rec.get(search_rec.main_field_id.name) or ''
                                                            parent_obj = getattr(some_record,super_field_row.field_id.relation_field)
                                                            model_rec['model'] = parent_obj._name
                                                            model_rec['model_name'] = parent_obj._name.upper()
                                                            model_rec['id'] = parent_obj.id
                                                            str_object_data = str(object_data[1])
                                                            search_result[company.name + '|'+search_result_record+' > ' + field.field_description + ' : ' + str_object_data] = model_rec
                                                            limit_count = limit_count + 1
                    except Exception as e:
                        print(e)

        ks_rec['search_result'] = search_result
        ks_rec['table_icon'] = table_icon

        ks_menu_record = {}
        dict_key = ''

        for rec in ks_search_result:
            if ks_search_result[rec]['model_name'] not in ks_menu_record:
                ks_menu_record[ks_search_result[rec]['model_name']] = {}
                dict_key = str(ks_search_result[rec]['model_name'])
            if str(ks_search_result[rec]['model_name']) == dict_key:
                ks_menu_record[ks_search_result[rec]['model_name']][rec] = ks_search_result[rec]

        ks_rec['ks_menu_record'] = ks_menu_record

        return ks_rec
