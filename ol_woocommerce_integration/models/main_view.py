import datetime

from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
import requests


class productproduct(models.Model):
    _inherit = "product.product"
    is_woocommerce_update_required = fields.Boolean("Is Woocommerce Update Required")
    source_name = fields.Char('Product Source')
    woocommerce_instance_id = fields.Many2one('woocommerce.main', 'WooCommerce Instance')
    sync_to_woocommerce = fields.Boolean("Sync to Woocommerce", default=True)
    woocommerce_sync_error_message = fields.Text("Sync Error")
    yet_to_be_uploaded = fields.Boolean("Yet To Be Uploaded", default=True)
    woocommerce_product_id = fields.Integer("Woocommerce Product Id")
    woocommerce_end_point = fields.Char("Woocommerce Endpoint")
    woocommerce_product_url = fields.Char("Woocommerce Product URL")

    # @api.onchange('lst_price','rent_per_month','regular_price','price_from','price_too')
    def woocommerce_update_sync(self, subtract_quantity=0):
        specifics = []
        for rec in self:
            if rec.sync_to_woocommerce:
                rec.is_woocommerce_update_required = True
                specifics.append(rec)
        if specifics:

            wocom_instances = self.env["woocommerce.main"].search([])
            for instance in wocom_instances:
                instance.update_product(specifics=specifics, subtract_quantity=subtract_quantity)

    def woocommerce_create_sync(self):
        specifics = []
        for rec in self:
            if rec.sync_to_woocommerce:
                specifics.append(rec)
        if specifics:
            wocom_instances = self.env["woocommerce.main"].search([])
            for instance in wocom_instances:
                instance.upload_product(specifics=specifics)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    is_woocommerce_update_required = fields.Boolean("Is Woocommerce Update Required")
    source_name = fields.Char('Product Source')
    woocommerce_instance_id = fields.Many2one('woocommerce.main', 'WooCommerce Instance')
    sync_to_woocommerce = fields.Boolean("Sync to Woocommerce", default=True)
    woocommerce_sync_error_message = fields.Text("Sync Error")
    yet_to_be_uploaded = fields.Boolean("Yet To Be Uploaded", default=True)
    woocommerce_product_id = fields.Integer("Woocommerce Product Id")
    woocommerce_end_point = fields.Char("Woocommerce Endpoint")
    woocommerce_product_url = fields.Char("Woocommerce Product URL")

    # deposit_fee=fields.Float(compute="compute_fee")
    # service_fee=fields.Float(compute="compute_fee")
    # rent_per_month=fields.Float(compute="compute_fee")
    # regular_price=fields.Float(compute="compute_fee")
    # price_from=fields.Date(compute="compute_fee")
    # price_too=fields.Date(compute="compute_fee")
    # def compute_fee(self):
    #     for rec in self:
    #         rec.deposit_fee=0
    #         rec.service_fee=0
    #         rec.rent_per_month=0
    #         rec.regular_price=0
    #         rec.price_from=False
    #         rec.price_too=False
    #         for variant in rec.product_variant_ids:
    #             rec.deposit_fee=variant.deposit_fee
    #             rec.service_fee=variant.service_fee
    #             rec.rent_per_month=variant.rent_per_month
    #             rec.regular_price=variant.regular_price
    #             rec.price_from=variant.price_from
    #             rec.price_too=variant.price_too
    #             break
    # @api.onchange('lst_price','rent_per_month','regular_price','price_from','price_too')
    def woocommerce_update_sync(self):
        self.product_variant_ids.woocommerce_update_sync()

    def woocommerce_create_sync(self):
        self.product_variant_ids.woocommerce_create_sync()


class location(models.Model):
    _inherit = "stock.location"
    sync_to_woocommerce = fields.Boolean("Sync to Woocommerce")


class mrp_production(models.Model):
    _inherit = "mrp.production"

    def woocommerce_product_update_sync(self):
        # raise UserError('change')

        if self.location_dest_id == self.location_src_id and self.location_dest_id:
            raise UserError("Source and Destination locations could not be same")
        if self.state not in ('draft', 'confirmed'):
            #     raise UserError("Test")
            # else:
            #     return
            product_inventory_difference_dict = {}
            # for rec in self:
            #     if not rec.move_line_ids:
            #         continue
            rec = self
            key = rec.product_id.id
            if rec.location_dest_id.sync_to_woocommerce and (
            not rec.location_src_id.sync_to_woocommerce):  ##if quantity moving from some other location to woocommerce location then add
                product_inventory_difference_dict[key] = product_inventory_difference_dict.get(key, 0) - (
                    rec.product_qty)
            elif (
            not rec.location_dest_id.sync_to_woocommerce) and rec.location_src_id.sync_to_woocommerce:  ##if quantity moving from woocommerce location to some other location then subtract
                product_inventory_difference_dict[key] = product_inventory_difference_dict.get(key, 0) + (
                    rec.product_qty)

                if rec.state == "cancel":
                    product_inventory_difference_dict[key] = product_inventory_difference_dict[key] * -1

            for key in product_inventory_difference_dict.keys():
                quantity = product_inventory_difference_dict[key]
                product = self.env['product.product'].search([('id', '=', key)])
                product.woocommerce_update_sync(subtract_quantity=0)


class stock_move(models.Model):
    _inherit = "stock.move"

    def woocommerce_product_update_sync(self):
        # raise UserError('change')
        product_inventory_difference_dict = {}
        for rec in self:
            if not rec.move_line_ids:
                continue
            key = rec.product_id.id
            if rec.location_dest_id.sync_to_woocommerce and (
            not rec.location_id.sync_to_woocommerce):  ##if quantity moving from some other location to woocommerce location then add
                product_inventory_difference_dict[key] = product_inventory_difference_dict.get(key, 0) - (
                    rec.quantity_done if rec.quantity_done > 0 else rec.reserved_availability)
            elif (
            not rec.location_dest_id.sync_to_woocommerce) and rec.location_id.sync_to_woocommerce:  ##if quantity moving from woocommerce location to some other location then subtract
                product_inventory_difference_dict[key] = product_inventory_difference_dict.get(key, 0) + (
                    rec.quantity_done if rec.quantity_done > 0 else rec.reserved_availability)

            if rec.state == "cancel":
                product_inventory_difference_dict[key] = product_inventory_difference_dict[key] * -1

        for key in product_inventory_difference_dict.keys():
            quantity = product_inventory_difference_dict[key]
            product = self.env['product.product'].search([('id', '=', key)])
            product.woocommerce_update_sync(subtract_quantity=0)


# class quant(models.Model):
#     _inherit = "stock.quant"
#     def woocommerce_product_update_sync(self):
#         for rec in self:
#             if rec.location_id.sync_to_woocommerce:
#                 rec.product_id.woocommerce_update_sync()
class picking(models.Model):
    _inherit = "stock.picking"

    def woocommerce_product_update_sync(self):
        self.move_ids_without_package.woocommerce_product_update_sync()
        # for rec in self:
        #     for line in rec.move_ids_without_package:
        #         if line.location_dest_id.sync_to_woocommerce or line.location_id.sync_to_woocommerce:
        #             line.product_id.woocommerce_update_sync()

        # Shams


# class stock_inventory(models.Model):
#     _inherit = "stock.inventory"
#     def woocommerce_product_update_sync(self):
#         self.move_ids.woocommerce_product_update_sync()


# for rec in self:
#     for line in rec.move_ids:
#         if line.location_dest_id.sync_to_woocommerce or line.location_id.sync_to_woocommerce:
#             line.product_id.woocommerce_update_sync()

class respartnerInherit(models.Model):
    _inherit = "res.partner"
    source_name = fields.Char('Contact Source')
    woocommerce_instance_id = fields.Many2one('woocommerce.main', 'WooCommerce Instance')


class SaleOrder(models.Model):
    _inherit = "sale.order"
    is_woocommerce_update_required = fields.Boolean("Is Woocommerce Update Required")
    woo_currency = fields.Char('Woo Currency')
    source_name = fields.Char('Order Source')
    woocommerce_instance_id = fields.Many2one('woocommerce.main', 'WooCommerce Instance')
    source_ecommerce2 = fields.Char("Source Ecommerce")
    payment_method = fields.Char("Payment Method")
    woocommerce_order_id = fields.Integer("Woocommerce Order Id")
    woocommerce_order_url = fields.Char("Woocommerce Order URL")
    woocommerce_sync_error_message = fields.Char("Sync Error")
    payment_method_main = fields.Many2one('account.payment.method', 'Payment Method')

    def convert_currency(self):

        if self.woo_currency != 'SGD' or self.woo_currency != False:
            base_currency = self.woo_currency
            target_currency = "SGD"
            api_key = "1ipa1dd6drgseh5jsoebaorni24pf9b4gt3643b8k998jjui2ktam1g"
            amount = 1
            convert_api = f"https://anyapi.io/api/v1/exchange/convert?base={base_currency}&to={target_currency}&amount={amount}&apiKey={api_key}"
            response = requests.get(convert_api)
            data = response.json()
            convert_rate = data["rate"]

            for lines in self.order_line:
                lines.price_unit = convert_rate * lines.price_unit

        self.action_confirm()

    def update_order_lines_with_coupon_code(self):

        woocomm = self.env['woocommerce.main'].search([('name', '=', 'Woocommerce Integration')])
        for order in self:

            wcapi = API(
                url=woocomm.url,
                consumer_key=woocomm.consumer_key,
                consumer_secret=woocomm.consumer_secret,
                version="wc/v3",
                query_string_auth=True,
                verify_ssl=False
            )
            woo = wcapi.get("orders/" + str(order.woocommerce_order_id)).json()

            # #update cuurency
            # woo_curr = str(woo['currency'])
            # currency = self.env['res.currency'].search([('name', '=', woo_curr)])
            # if not currency.active:
            #     currency.write({'active': True})

            # order.write({'currency_id': currency.id})

            # update coupon
            if woo['coupon_lines'] != []:
                coupon_code = woo['coupon_lines'][0][
                    'code']  # Replace XYZ with the actual coupon code retrieved from WooCommerce
                for line in order.order_line:
                    if line.product_id.name == 'Discount':
                        line.write({'name': f"Coupon Code: {coupon_code}"})

        return True

    def update_country_city(self):

        woocomm = self.env['woocommerce.main'].search([('name', '=', 'Woocommerce Integration')])
        for order in self:

            wcapi = API(
                url=woocomm.url,
                consumer_key=woocomm.consumer_key,
                consumer_secret=woocomm.consumer_secret,
                version="wc/v3",
                query_string_auth=True,
                verify_ssl=False
            )
            woo = wcapi.get("orders/" + str(order.woocommerce_order_id)).json()
            woo_country = str(woo['billing']['country'])
            if not order.partner_id.country_id:
                get_country = self.env['res.country'].search([('code', '=', woo_country)])
                order.partner_id.country_id = get_country.id
            if not order.partner_id.city:
                city = woo['billing']['city']
                order.partner_id.city = city
                if city == "" and woo_country == 'SG':
                    city = 'singapore'
    # @api.onchange('state')
    # def _onchange_state(self):
    #     # raise UserError("OK")
    #     for rec in self:
    #         raise UserError("Test")
    #         rec.is_woocommerce_update_required=True


class ProductsWoo(models.Model):
    _name = 'woocommerce.main'
    name = fields.Char("Name")
    url = fields.Char("Url")
    consumer_key = fields.Char("Consumer Key")
    consumer_secret = fields.Char("Consumer Secret")
    company_id = fields.Many2one('res.company')
    my_domain = fields.Char(string='My Domain')
    # warehouse_id = fields.Many2one('stock.warehouse')
    # location_id = fields.Many2one('stock.location')

    color = fields.Integer(string='Color Index')
    # sub_instance_ids= fields.One2many("woocommerce.sub.instances","main_instances_id",string="Main Instence")

    product_woo_to_odoo_active = fields.Boolean("Activate")
    product_woo_to_odoo_delay = fields.Integer("Delay In Minutes")
    product_woo_to_odoo_from_date = fields.Date("From Date")
    product_woo_to_odoo_log_ids = fields.One2many("woocommerce.product.logs", "main_id", string="Logs", readonly="True")

    product_odoo_to_woo_active = fields.Boolean("Activate")
    product_odoo_to_woo_force_remap = fields.Boolean("Force Remap All")
    product_odoo_to_woo_from_date = fields.Date("From Date")
    product_odoo_to_woo_delay = fields.Integer("Delay In Minutes")
    product_odoo_to_woo_log_ids = fields.One2many("woocommerce.product.down.logs", "main_id", string="Logs",
                                                  readonly="True")

    order_woo_to_odoo_active = fields.Boolean("Activate")
    order_woo_to_odoo_from_date = fields.Date("From Date")
    order_woo_to_odoo_delay = fields.Integer("Delay In Minutes")
    order_woo_to_odoo_log_ids = fields.One2many("woocommerce.orders.logs", "main_id", string="Logs", readonly="True")

    produpdate_odoo_to_woo_active = fields.Boolean("Activate")
    produpdate_odoo_to_woo_force_remap = fields.Boolean("Force Update All")
    produpdate_odoo_to_woo_from_date = fields.Date("From Date")
    produpdate_odoo_to_woo_price = fields.Boolean("Update Price")
    produpdate_odoo_to_woo_inventory = fields.Boolean("Update Inventory")
    produpdate_odoo_to_woo_delay = fields.Integer("Delay In Minutes")
    produpdate_odoo_to_woo_log_ids = fields.One2many("woocommerce.product.update.logs", "main_id", string="Logs",
                                                     readonly="True")
    Schedule_actions = fields.Many2one('ir.cron', "Schedule Action")

    order_status_woo_to_odoo_active = fields.Boolean("Activate")
    order_status_woo_to_odoo_force_update = fields.Boolean("Force Update All")
    order_status_odoo_to_woo_log_ids = fields.One2many("woocommerce.orders.status.logs", "main_id", string="Logs",
                                                       readonly="True")
    order_status_woo_to_odoo_from_date = fields.Date(string="From Date")
    categoryUpdate_w_o_active = fields.Boolean("Activate")

    def prepare_uploadable_product(self, product, sku):
        prodcreate = {
            'name': product['name'],
            'description': product['description'] if product['description'] else '',
            'sku': sku,
            'regular_price': str(product.list_price),

            # 'regular_price':str(product.rent_per_month),
            # 'sale_price':str(product.regular_price),
            # #### special requirment of tastenexpress for lease purchase price sync
            # "meta_data":[
            #         {"key":"wccaf_producttional_mietkauf","value":str(product.lst_price)},
            #         {"key":"wccaf_servicepauschale","value":str(product.service_fee)},
            #         {"key":"wccaf_kaution","value":str(product.deposit_fee)}
            #         ],
            # ###mapping custom prices of tasteNexpress
            # 'regular_price':str(product.rent_per_month),
            # 'sale_price':str(product.regular_price),
        }
        # if product.price_from:
        #     prodcreate['date_on_sale_from']=product.price_from.strftime('%Y-%m-%dT%H:%M:%S.%f')
        # if product.price_too:
        #     prodcreate['date_on_sale_to']=product.price_too.strftime('%Y-%m-%dT%H:%M:%S.%f')
        if product.type == "product" and product._name == "product.product":  ## if product is storable. manage quantity.
            quants = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('quantity', '>=', 0)])
            inventory_sum = sum([quant.available_quantity for quant in quants if quant.location_id.sync_to_woocommerce])
            prodcreate['stock_quantity'] = inventory_sum
            prodcreate['manage_stock'] = True
        if product._name == "product.product":
            attributes = []
            for attribute in product.product_template_attribute_value_ids:
                attributes.append({"name": str(attribute.attribute_id.name), "option": str(attribute.name)})
            if attributes:
                prodcreate['attributes'] = attributes
        else:
            attributes = []
            for attribute in product.attribute_line_ids:
                att = {"name": str(attribute.attribute_id.name),
                       "visible": True,
                       "variation": True,
                       "options": []
                       }
                for value in attribute.value_ids:
                    att['options'].append(str(value.name))
                attributes.append(att)
            if attributes:
                prodcreate['attributes'] = attributes
        ##creating image attachment and getting its url
        url = ""

        try:
            # have to comment this part on local env. uncomment this and this will work on servers.
            if product.image_1920:
                image_attachment = self.env['ir.attachment'].search(
                    [('res_model', '=', product._name), ('res_id', '=', product.id), ('res_field', '=', "image_1920")])

                if not image_attachment:
                    image_attachment = self.env['ir.attachment'].create({
                        'datas': product.image_1920,
                        'type': 'binary',
                        'name': product.name,
                        'public': True,
                        'res_model': product._name,
                        "res_id": product.id,
                        "res_field": "image_1920"
                    })

                if len(image_attachment) > 1:
                    image_attachment = image_attachment[0]
                if self.my_domain:
                    url = str(self.my_domain) + '/my_module/get_attachment/' + str(image_attachment.id) + "." + \
                          str(image_attachment.mimetype).split('/')[1]
        except:
            pass
        # #if image url created bind it in product object
        if url != "":
            prodcreate['images'] = [{"src": url}]

        return prodcreate

    def woo_product_uploader(self, wcapi, endpoint, odoo_object, prepared_object, sku, skumap):
        ##tastenexpress has specific requirement to map odoo ids as sku on woo commerce products.

        odoo_object.woocommerce_sync_error_message = ""
        wooproduct = skumap.get(sku, None)
        if not wooproduct:  ##if product does not already exist on woocommerce, then create it and map it in odoo

            created = wcapi.post(endpoint, prepared_object).json()

            if 'id' in created.keys():
                create_log = {
                    'odoo_id': odoo_object.id if odoo_object._name == "product.product" else False,
                    "odoo_template_id": odoo_object.id if odoo_object._name == "product.template" else odoo_object.product_tmpl_id.id,
                    'woo_id': created['id'],
                    'sku': created['sku'],
                    'status': 'complete',
                    'details': "Product Has Been Created Successfully",
                    'main_id': self.id
                }
                odoo_object.is_woocommerce_update_required = False
                odoo_object.yet_to_be_uploaded = False
                odoo_object.woocommerce_product_id = created['id']
                try:
                    odoo_object.woocommerce_product_url = created["_links"]["self"][0]['href']
                except:
                    odoo_object.woocommerce_product_url = "Error while picking url"

                woocommcreate = self.env['woocommerce.product.logs'].create(create_log)

                skumap[sku] = created
            else:
                self.env['woocommerce.product.logs'].create({
                    'odoo_id': odoo_object.id if odoo_object._name == "product.product" else False,
                    "odoo_template_id": odoo_object.id if odoo_object._name == "product.template" else odoo_object.product_tmpl_id.id,
                    'sku': sku,
                    'status': 'error',
                    'details': str(created),
                    'main_id': self.id
                })
                odoo_object.woocommerce_sync_error_message = str(created)

        else:  ## if product exists then update the product and map it in odoo

            response_woo = wcapi.put(endpoint + "/" + str(wooproduct['id']), prepared_object)
            create_log = {
                'odoo_id': odoo_object.id if odoo_object._name == "uct" else False,
                "odoo_template_id": odoo_object.id if odoo_object._name == "product.template" else odoo_object.product_tmpl_id.id,
                'woo_id': wooproduct['id'],
                'sku': sku,
                'status': 'complete',
                'details': "Product already exists. It Has Been updated and remapped Successfully",
                'main_id': self.id
            }
            odoo_object.is_woocommerce_update_required = False
            odoo_object.yet_to_be_uploaded = False
            odoo_object.woocommerce_product_id = wooproduct['id']
            try:
                odoo_object.woocommerce_product_url = wooproduct["_links"]["self"][0]['href']
            except:
                odoo_object.woocommerce_product_url = "Error while picking url"

            woocommcreate = self.env['woocommerce.product.logs'].create(create_log)

    def upload_product(self, specifics=[]):
        # try:
        # raise UserError("Test")
        RunUpdate = False
        if self.product_woo_to_odoo_active:
            filters = [("company_id", '=', self.company_id.id),
                       ('sync_to_woocommerce', "=", True),
                       ]
            if not self.product_odoo_to_woo_force_remap:  ## if force remap is not enabled. only then apply this filter and continue. else disable the check for future runs and continue
                filters.append(("yet_to_be_uploaded", '=', True))
            else:
                self.product_odoo_to_woo_force_remap = False
            uploadableProducts = self.env['product.product'].search(filters)
            # raise UserError(str(uploadableProducts))

            # Create Categories

            uploadableProducts = self._combine(uploadableProducts, specifics)
            if not uploadableProducts:
                return
            # raise UserError(str(uploadableProducts))
            wcapi = API(
                url=self.url,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                version="wc/v3",
                query_string_auth=True,
                verify_ssl=False
            )
            prodobj = self.env['product.product']
            page = 1
            woo_products = []
            r = wcapi.get("products/", params={"per_page": 100, "page": page}).json()
            woo_products.extend(r)

            # if woo_products and woo_products[0] != 'code':
            while r != []:
                page += 1
                r = wcapi.get("products/",
                              params={"per_page": 100, "page": page}).json()
                woo_products.extend(r)
            skumap = {}
            # for wd in woo_products:
            # skuslist.append(wd['sku'])
            # skumap[wd['sku']]=wd

            for op in uploadableProducts:
                product_template = op.product_tmpl_id
                if len(product_template.product_variant_ids) > 1:  ### if there are more then 1 variants to the template. then we create the template and then create the variant.

                    sku = str(product_template.id)
                    template_create = self.prepare_uploadable_product(product_template, sku)
                    template_create['type'] = 'variable'
                    r = wcapi.get("products/categories",
                                  params={"slug": str(op.categ_id.name).lower().replace(' ', '-')}).json()
                    # raise UserError(str(r))
                    if r:
                        template_create['categories'] = [{'id': r[0]['id']}]
                    else:
                        self.create_categories(op)
                        r = wcapi.get("products/categories",
                                      params={"slug": str(op.categ_id.name).lower().replace(' ', '-')}).json()
                        template_create['categories'] = [{'id': r[0]['id']}]
                    # template_create['status']='publish'
                    self.woo_product_uploader(wcapi, "products", product_template, template_create, sku, skumap)
                    product_template.woocommerce_end_point = "products" + "/" + str(
                        product_template.woocommerce_product_id)
                    variantskumap = {}
                    variantsEndpoint = "products/" + str(product_template.woocommerce_product_id) + "/variations"
                    variants = wcapi.get(variantsEndpoint).json()

                    for wd in variants:
                        # skuslist.append(wd['sku'])
                        variantskumap[wd['sku']] = wd
                    # sku=str(op.id)
                    sku = op.default_code
                    variant_create = self.prepare_uploadable_product(op, sku)
                    self.woo_product_uploader(wcapi, variantsEndpoint, op, variant_create, sku, variantskumap)
                    op.woocommerce_end_point = variantsEndpoint + "/" + str(op.woocommerce_product_id)
                else:
                    sku = str(op.product_tmpl_id.default_code)

                    template_create = self.prepare_uploadable_product(op, sku)
                    if r:
                        template_create['categories'] = [{'id': r[0]['id']}]
                    else:
                        self.create_categories(op)
                        r = wcapi.get("products/categories",
                                      params={"slug": str(op.categ_id.name).lower().replace(' ', '-')}).json()
                        template_create['categories'] = [{'id': r[0]['id']}]

                    # template_create['status']='publish'
                    self.woo_product_uploader(wcapi, "products", op, template_create, sku, skumap)
                    op.woocommerce_end_point = "products" + "/" + str(op.woocommerce_product_id)
                    ##copying all mapping info from variant to template since its same
                    product_template.woocommerce_end_point = op.woocommerce_end_point
                    product_template.is_woocommerce_update_required = op.is_woocommerce_update_required
                    product_template.yet_to_be_uploaded = op.yet_to_be_uploaded
                    product_template.woocommerce_product_id = op.woocommerce_product_id
                    product_template.woocommerce_product_url = op.woocommerce_product_url
                    product_template.woocommerce_sync_error_message = op.woocommerce_sync_error_message

            # if RunUpdate:
            #     self.update_product()

    # except:
    #     return 0

    # def get_parentID(self,category):
    #     if category.parent_id:
    #         a=self.get_parentID(category.parent_id)

    #     else:
    #         return None

    def create_categories(self, u):
        categs = []

        c = u.categ_id

        wcapi = API(
            url=self.url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version="wc/v3",
            query_string_auth=True,
            verify_ssl=False
        )

        while True:
            if c:
                if c.parent_id:
                    categs.append(
                        {'name': c.name,
                         'parent': c.parent_id.name}
                    )
                    c = c.parent_id
                else:
                    categs.append(
                        {
                            'name': c.name,
                            'parent': None
                        }
                    )
                    break

        # temp=[]
        # catID=''
        for c in reversed(list(categs)):
            r = wcapi.get("products/categories", params={"slug": str(c['name']).lower().replace(' ', '-')}).json()

            if r:
                pass
            else:
                data = {
                    "name": c['name'],
                    "slug": str(c['name']).lower().replace(' ', '-'),
                    "description": "Category From Odoo",
                    "parent": 0
                    # "display": "default"
                }
                if c['parent']:
                    r = wcapi.get("products/categories",
                                  params={"slug": str(c['parent']).lower().replace(' ', '-')}).json()
                    if r:
                        data['parent'] = r[0]['id']
                    else:
                        break
                x = wcapi.post("products/categories", data).json()
                # temp.append(x)

        # raise UserError(str(temp))

    def download_product(self):
        # raise UserError("OK")
        self.update_categories()
        try:
            if self.product_odoo_to_woo_active:
                if self.product_odoo_to_woo_from_date:
                    DN = str(self.product_odoo_to_woo_from_date.strftime("%Y-%m-%d"))
                    wcapi = API(
                        url=self.url,
                        consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret,
                        version="wc/v3",
                        query_string_auth=True,
                        verify_ssl=False
                    )
                    prodobj = self.env['product.product']
                    page = 1
                    woo_products = []
                    r = wcapi.get("products/", params={"per_page": 100, "page": page, "after": DN + "T00:00:00"}).json()
                    woo_products.extend(r)

                    # raise UserError(r)
                    if not woo_products:
                        return

                    if woo_products[0] != 'code':
                        # while r != []:
                        #     page+=1
                        #     r = wcapi.get("products/", params={"per_page": 100, "page": page,"after":DN + "T00:00:00"}).json()
                        #     woo_products.extend(r)
                        skuslist = []
                        allodooproduct = prodobj.search([('company_id', '=', self.company_id.id)])
                        for wo in allodooproduct:
                            skuslist.append(wo.default_code)
                        for wo in woo_products:
                            # raise UserError(str(wo))
                            try:
                                # print(wo)
                                #

                                # raise UserError(wo)

                                def pass_image(image_url):
                                    bin = base64.b64encode(requests.get(image_url.strip()).content).replace(b"\n", b"")
                                    return bin  # or you could print it

                                # if wo['type']!='simple':
                                #     prodobj=self.env['product.template']
                                #     variations=wcapi.get("products/"+str(wo['id'])+"/variations").json()
                                #     raise UserError(variations[0])
                                # continue
                                variations = []
                                if wo['type'] == 'variable':
                                    # prodobj=self.env['product.template']
                                    variations = wcapi.get("products/" + str(wo['id']) + "/variations").json()
                                    # raise UserError(str(variations[0]))

                                prodobj = self.env['product.product']

                                categ_id = self.env["product.category"].search(
                                    [('id', '=', 1)])  ##selecting default category as 1
                                ##if Id provided, we select the first one
                                # raise UserError(wo["categories"])
                                for category in wo["categories"]:
                                    new_id = self.env["product.category"].search([('name', '=', category['name'])])
                                    if new_id:
                                        categ_id = new_id
                                    break

                                if not wo['sku'] in skuslist and not variations:

                                    # raise UserError("Check")

                                    # check=False

                                    # continue

                                    prodcreate = {
                                        'name': wo['name'],
                                        'description': wo['description'] if wo['description'] else '',
                                        'default_code': wo['sku'],
                                        'type': 'product',
                                        "categ_id": categ_id.id,
                                        "company_id": self.company_id.id,
                                        'source_name': "Woocommerce : " + str(self.name),
                                        'woocommerce_instance_id': self.id,
                                        'woocommerce_product_id': wo['id'],
                                        'woocommerce_product_url': str(wo['permalink']) + str(wo['id']),
                                        'yet_to_be_uploaded': False,
                                        'woocommerce_end_point': "products" + "/" + str(wo['id']),

                                        # 'qty_available': float(wo['stock_quantity']),
                                        # 'price': float(wo['regular_price']),
                                        'list_price': float(wo['regular_price']) if wo['regular_price'] else 0,
                                        # 'image_1920':pass_image(wo['images'][0]['src']) if wo['images'] else False
                                    }

                                    # raise UserError(str(prodcreate))

                                    created = prodobj.create(prodcreate)
                                    try:
                                        created.image_1920 = pass_image(wo['images'][0]['src']) if wo[
                                            'images'] else False
                                    except:
                                        created.image_1920 = False

                                    if wo['type'] == 'simple':
                                        created.product_tmpl_id.source_name = created.source_name
                                        created.product_tmpl_id.woocommerce_instance_id = created.woocommerce_instance_id
                                        created.product_tmpl_id.company_id = created.company_id
                                    else:
                                        created.source_name = created.source_name
                                        created.woocommerce_instance_id = created.woocommerce_instance_id
                                        created.company_id = created.company_id
                                    # created.

                                    # raise UserError("Test")
                                    create_log = {
                                        'odoo_id': created.id,
                                        'woo_id': wo['id'],
                                        'sku': wo['sku'],
                                        'status': 'complete',
                                        'details': "Product Has Been Created Scussfully",
                                        'main_id': self.id
                                    }
                                    master = created

                                    # woocommcreate=self.env['woocommerce.product.down.logs'].create(create_log)

                                else:
                                    master = prodobj.search([('default_code', '=', wo['sku'])], limit=1)

                                if variations:

                                    prodobj = self.env['product.product']

                                    for v in variations:
                                        exist = prodobj.search([('default_code', '=', v['sku'])])
                                        if exist:
                                            continue
                                        prodcreate = {
                                            'name': wo['name'],
                                            'description': v['description'] if v['description'] else '',
                                            'default_code': v['sku'],
                                            'type': 'product',
                                            "categ_id": categ_id.id,
                                            "company_id": self.company_id.id,
                                            'source_name': "Woocommerce : " + str(self.name),
                                            'woocommerce_instance_id': self.id,
                                            'woocommerce_product_id': v['id'],
                                            'woocommerce_product_url': str(v['_links']['self'][0]['href']),
                                            'yet_to_be_uploaded': False,
                                            'woocommerce_end_point': "products/" + str(wo['id']) + "/variations/" + str(
                                                v['id']),
                                            # 'product_tmpl_id':master.id,
                                            # 'qty_available': float(wo['stock_quantity']),
                                            # 'price': float(wo['regular_price']),
                                            'list_price': float(v['regular_price']) if v['regular_price'] else 0,
                                            # 'image_1920':pass_image(wo['images'][0]['src']) if wo['images'] else False
                                        }

                                        # raise UserError(str(prodcreate))

                                        created = prodobj.create(prodcreate)
                                        # raise UserError(str(prodcreate))
                                        try:
                                            created.image_1920 = pass_image(v['images'][0]['src']) if v[
                                                'images'] else False
                                        except:
                                            created.image_1920 = False

                                        # created.product_tmpl_id=master.id
                                        # created.product_tmpl_id.source_name=master.source_name
                                        # raise UserError(str(created))
                                        # created.product_tmpl_id.woocommerce_instance_id=created.woocommerce_instance_id
                                        # created.product_tmpl_id.company_id=created.company_id

                                        # created.

                                        create_log = {
                                            'odoo_id': created.id,
                                            'woo_id': v['id'],
                                            'sku': v['sku'],
                                            'status': 'complete',
                                            'details': "Product Has Been Created Scussfully",
                                            'main_id': self.id
                                        }

                                        woocommcreate = self.env['woocommerce.product.down.logs'].create(create_log)

                                    # if wo['type']=='simple':

                                    self.product_odoo_to_woo_from_date = datetime.datetime.now().date()

                            except Exception as e:
                                raise UserError(str(e))
                                print(e)
                                created = self.env['woocommerce.product.down.logs'].create({
                                    'woo_id': wo['id'],
                                    'sku': wo['sku'],
                                    'status': 'error',
                                    'details': str(e),
                                    'main_id': self.id
                                })
                else:
                    raise UserError("Date Field Not Set")
            else:
                raise UserError("Activate it first!!")
            # self.update_product()
            return 1
        except  Exception as e:
            raise UserError(str(e))

    def update_status(self):
        if self.order_status_woo_to_odoo_active:
            filters = [("company_id", '=', self.company_id.id), ('source_ecommerce2', '=', self.name),
                       ("woocommerce_order_id", "!=", False)]

            orders = self.env['sale.order'].search(filters)
            # raise UserError(orders)
            if not orders:
                return 1
            wcapi = API(
                url=self.url,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                version="wc/v3",
                query_string_auth=True,
                verify_ssl=False
            )

            for odo in orders:
                try:
                    woo = wcapi.get("orders/" + str(odo.woocommerce_order_id)).json()
                except Exception as e:
                    odo.woocommerce_sync_error_message = str(e)
                    odo.is_woocommerce_update_required = False
                    create_log = {
                        'odoo_id': odo.id,
                        'woo_id': odo.woocommerce_order_id,
                        'status': 'error',
                        'details': str(e),
                        'main_id': self.id
                    }
                    self.env['woocommerce.orders.status.logs'].create(create_log)
                    continue
                # raise UserError(str(woo))
                if not woo.get('id', None):
                    odo.is_woocommerce_update_required = False
                    odo.woocommerce_sync_error_message = str(woo)
                    create_log = {
                        'odoo_id': odo.id,
                        'woo_id': odo.woocommerce_order_id,
                        'status': 'error',
                        'details': str(woo),
                        'main_id': self.id
                    }
                    self.env['woocommerce.orders.status.logs'].create(create_log)
                    continue

                if woo['status'] == "cancelled":
                    odo['state'] = 'cancel'

                if not self.order_status_woo_to_odoo_force_update:
                    if odo['is_woocommerce_update_required'] == "false":
                        continue

                self.order_status_woo_to_odoo_force_update = False
                # raise UserError("ok")

                if str(woo['id']) == odo['origin']:
                    # raise UserError("Mil Gya")
                    status = None
                    # raise UserError(str(odo['invoice_status']) + " - " + str(odo['name']))

                    if str(odo['state']) == "sale":
                        status = "processing"
                        picking_ids = odo['picking_ids']

                        for p in picking_ids:
                            if p['origin'] == odo['name']:
                                if str(picking_ids[0].state) == "done":
                                    status = "completed"



                    # xxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    # if str(odo['invoice_status'])=="invoiced":
                    #     odoo_invoice=self.env['account.move'].search([('id', '=', odo['invoice_ids'][0].id)])
                    #     odo_invoice_status=odoo_invoice[0]['payment_state']

                    #     # if odo_inv_state=="draft":
                    #     #     status="draft"
                    #     # else:
                    #     if odo_invoice_status=="in_payment":
                    #         picking_ids=odo['picking_ids']

                    #         if str(picking_ids[0].state)=="done":
                    #             status="completed"
                    #         else:
                    #             status="processing"

                    #     else:
                    #         status="pending"

                    # else:
                    #     status="pending"
                    # xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
                    # raise UserError(odo_invoice_status)
                    # print(odo_invoice_status)
                    # if odo_invoice_status=="paid" and woo['status'] != "completed":
                    #     status="completed"
                    # elif odo_invoice_status=="canceled" and woo['status'] != "canceled":
                    #     status="canceled"
                    # elif odo_invoice_status=="not_paid" and woo['status'] != "processing":
                    #     status="processing"

                    elif (str(odo['state']) == "cancel"):
                        status = "cancelled"
                    else:
                        status = "on-hold"

                    # cancel_run=False
                    # if woo['status']=="cancelled":
                    #     odo['state']='cancel'
                    #     # continue
                    #     status="cancelled"
                    #     cancel_run=True

                    # raise UserError(status + " - " +  odo['name'])

                    updated = {}
                    if status and woo['status'] != status:
                        data = {"status": status}

                        try:
                            odo.woocommerce_sync_error_message = ""
                            response_woo = wcapi.put("orders/" + str(woo['id']), data).json()
                            updated = response_woo
                            odo.is_woocommerce_update_required = False
                        except Exception as e:
                            create_log = {
                                'odoo_id': odo.id,
                                'woo_id': woo['id'],
                                'status': 'error',
                                'details': e,
                                'main_id': self.id
                            }
                            anyError = True
                            odo.woocommerce_sync_error_message = str(e)
                        if 'id' in updated.keys():
                            print("Odoo Status : " + str(odo['state']) + " - Woo Old status : " + woo[
                                'status'] + " - New Status : " + status)
                            create_log = {
                                'odoo_id': odo.id,
                                'woo_id': woo['id'],
                                'status': 'complete',
                                'details': "Status Updated from " + woo['status'] + " to " + status,
                                'main_id': self.id
                            }
                        else:
                            create_log = {
                                'odoo_id': odo.id,
                                'woo_id': woo['id'],
                                'status': 'error',
                                'details': str(response_woo),
                                'main_id': self.id
                            }
                            anyError = True
                            odo.woocommerce_sync_error_message = str(response_woo)
                        # raise UserError(str(create_log))
                        self.env['woocommerce.orders.status.logs'].create(create_log)
                    else:

                        create_log = {
                            'odoo_id': odo.id,
                            'woo_id': woo['id'],
                            'status': "complete",
                            'details': "Status Same woo : " + woo['status'] + " - Odoo : " + status,
                            'main_id': self.id
                        }
                        # raise UserError(str(create_log))
                        self.env['woocommerce.orders.status.logs'].create(create_log)

            # raise UserError(str(self.name))
        else:
            raise UserError("Active First")

    def recursive_add_category_with_parent(self, woocategory, woocategories):
        category_found = self.env['product.category'].search([('name', '=', woocategory['name'])])
        if category_found:
            return category_found[0]
        if woocategory['parent'] == 0:
            all_parent_category = self.env['product.category'].search([('name', '=', 'All')])
            category_id = self.env['product.category'].create(
                {'name': woocategory['name'], 'parent_id': all_parent_category.id})
            return category_id
        for checkingCategory in woocategories:
            if checkingCategory['id'] == woocategory['parent']:
                parent_id = self.recursive_add_category_with_parent(checkingCategory, woocategories)
                category_id = self.env['product.category'].create(
                    {'name': woocategory['name'], 'parent_id': parent_id.id})

                return category_id

    def update_categories(self):
        if self.categoryUpdate_w_o_active:
            wcapi = API(
                url=self.url,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                version="wc/v3",
                query_string_auth=True,
                verify_ssl=False
            )
            categories = []
            page = 1
            while True:
                response = wcapi.get('products/categories', params={"per_page": 100, "page": page}).json()
                if response == []:
                    break
                categories.extend(response)
                page = page + 1

            for category in categories:
                self.recursive_add_category_with_parent(category, categories)
            return categories
        return

    def _combine(self, l1, l2):
        l3 = []
        for rec in l1:
            l3.append(rec)
        for rec in l2:
            l3.append(rec)
        return l3

    def update_product(self, specifics=[], subtract_quantity=0):

        # try:
        force = False  ##this is a carry forward force var

        if self.produpdate_odoo_to_woo_active:
            prodobj = self.env['product.product']
            filters = [('company_id', "=", self.company_id.id),
                       ("sync_to_woocommerce", "=", True),
                       ("woocommerce_product_id", '!=', False)
                       ]

            if not self.produpdate_odoo_to_woo_force_remap:
                filters.append(("is_woocommerce_update_required", '=', True))
            else:
                self.produpdate_odoo_to_woo_force_remap = False
                force = True

            updateable_products = prodobj.search(filters)
            updateable_products = self._combine(updateable_products, specifics)

            # raise UserError(str(updateable_products))
            if not updateable_products:
                return 1
            wcapi = API(
                url=self.url,
                consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret,
                version="wc/v3",
                query_string_auth=True,
                verify_ssl=False
            )

            for odoo_product in updateable_products:
                try:
                    woo_product = wcapi.get(odoo_product.woocommerce_end_point).json()
                except Exception as e:
                    odoo_product.woocommerce_sync_error_message = str(e)
                    odoo_product.is_woocommerce_update_required = False
                    create_log = {
                        'odoo_id': odoo_product.id,
                        'woo_id': odoo_product.woocommerce_product_id,
                        'status': 'error',
                        'details': str(e),
                        'main_id': self.id
                    }
                    self.env['woocommerce.product.update.logs'].create(create_log)
                    continue
                # raise UserError(str(odoo_product.woocommerce_end_point))
                if not woo_product.get('id', None):
                    odoo_product.is_woocommerce_update_required = False
                    odoo_product.woocommerce_sync_error_message = str(woo_product)
                    create_log = {
                        'odoo_id': odoo_product.id,
                        'woo_id': odoo_product.woocommerce_product_id,
                        'status': 'error',
                        'details': str(woo_product),
                        'main_id': self.id
                    }
                    self.env['woocommerce.product.update.logs'].create(create_log)
                    continue

                update = {}
                details = ""
                # raise UserError(str(woo_product["meta_data"]))
                ###mapping custom prices of tasteNexpress
                if (force or woo_product['regular_price'] != str(
                        odoo_product.list_price)) and self.produpdate_odoo_to_woo_price:
                    if details != "":
                        details += "<br></br>"
                    details += "Updated Regular Price Woocommerce=" + woo_product['regular_price'] + ", Odoo=" + str(
                        odoo_product.list_price)
                    update['regular_price'] = str(odoo_product.list_price)
                # ###special requirement for tastenexpress
                # if (force or woo_product['sale_price'] != str(odoo_product.regular_price)) and self.produpdate_odoo_to_woo_price:
                #     if details!="":
                #         details+="<br></br>"
                #     details+="Updated Sale Price Woocommerce="+str(woo_product['sale_price'])+", Odoo="+str(odoo_product.regular_price)
                #     update['sale_price']=str(odoo_product.regular_price)
                # ###special requirement for tastenexpress
                # odoofromtime=odoo_product.price_from.strftime('%Y-%m-%dT%H:%M:%S.%f') if odoo_product.price_from else None
                # if (force or odoofromtime != woo_product.get('date_on_sale_from',None)) and self.produpdate_odoo_to_woo_price:
                #         update['date_on_sale_from']=odoofromtime
                #         if details!="":
                #             details+="<br></br>"
                #         details+="Updated Date From On Sale Woocommerce="+str(woo_product.get('date_on_sale_from',None))+", Odoo="+str(odoofromtime)
                # ###special requirement for tastenexpress
                # odoototime=odoo_product.price_too.strftime('%Y-%m-%dT%H:%M:%S.%f') if odoo_product.price_too else None

                # if (force or odoototime != woo_product.get('date_on_sale_to',None)) and self.produpdate_odoo_to_woo_price:
                #         update['date_on_sale_to']=odoototime
                #         if details!="":
                #             details+="<br></br>"
                #         details+="Updated Date To On Sale Woocommerce="+str(woo_product.get('date_on_sale_to',None))+", Odoo="+str(odoototime)

                ##updating custom metafields of tasteNexpress
                metadata = []
                # for meta in woo_product["meta_data"]:  #### special requirment of tastenexpress for lease purchase price sync
                #     if meta["key"]=="wccaf_optional_mietkauf" and (force or meta['value'] != str(odoo_product.lst_price)) and self.produpdate_odoo_to_woo_price:
                #         metadata.append({"key":"wccaf_optional_mietkauf","value":str(odoo_product.lst_price)})
                #         if details!="":
                #             details+="<br></br>"
                #         details+="Updated Lease Purchace Price Woocommerce="+meta['value']+", Odoo="+str(odoo_product.lst_price)
                #     if meta["key"]=="wccaf_kaution" and (force or meta['value'] != str(odoo_product.deposit_fee)) and self.produpdate_odoo_to_woo_price:
                #         metadata.append({"key":"wccaf_kaution","value":str(odoo_product.deposit_fee)})
                #         if details!="":
                #             details+="<br></br>"
                #         details+="Updated Deposit Fee Woocommerce="+meta['value']+", Odoo="+str(odoo_product.deposit_fee)
                #     if meta["key"]=="wccaf_servicepauschale" and (force or meta['value'] != str(odoo_product.service_fee)) and self.produpdate_odoo_to_woo_price:
                #         metadata.append({"key":"wccaf_servicepauschale","value":str(odoo_product.service_fee)})
                #         if details!="":
                #             details+="<br></br>"
                #         details+="Updated Service Fee Woocommerce="+meta['value']+", Odoo="+str(odoo_product.service_fee)
                # if metadata:
                #     update['meta_data']=metadata

                quants = self.env['stock.quant'].search([
                    ('product_id', '=', odoo_product.id),
                    ('quantity', '>=', 0)])
                # raise UserError(str(quants))
                inventory_sum = sum([quant.available_quantity for quant in quants if
                                     quant.location_id.sync_to_woocommerce]) - subtract_quantity
                # raise UserError("Updated Stock Woocommerce=" + str(woo_product['stock_quantity']) + ", Odoo=" + str(inventory_sum))

                try:
                    if odoo_product.type == "product" and (force or float(woo_product['stock_quantity']) != float(
                            inventory_sum)) and self.produpdate_odoo_to_woo_inventory:  ## if product is storable. manage quantity.
                        update['stock_quantity'] = str(inventory_sum)
                        if details != "":
                            details += "<br></br>"
                        details += "Updated Stock Woocommerce=" + str(woo_product['stock_quantity']) + ", Odoo=" + str(
                            inventory_sum)
                except:
                    pass
                # raise UserError(str(update))
                if update:
                    try:
                        # response_woo=wcapi.put("products/" + str(woo_product['id']), update)
                        response_woo = wcapi.put(odoo_product.woocommerce_end_point, update)
                        updated = response_woo.json()
                        if 'id' in updated.keys():
                            create_log = {
                                'odoo_id': odoo_product.id,
                                'woo_id': updated['id'],
                                'sku': updated['sku'],
                                'status': 'complete',
                                'details': details,
                                'main_id': self.id
                            }
                            self.env['woocommerce.product.update.logs'].create(create_log)
                            odoo_product.is_woocommerce_update_required = False
                        else:
                            create_log = {
                                'odoo_id': odoo_product.id,
                                'sku': odoo_product.id,
                                'woo_id': odoo_product.woocommerce_product_id,
                                'status': 'error',
                                'details': updated['message'],
                                'main_id': self.id
                            }
                            self.env['woocommerce.product.update.logs'].create(create_log)

                    except Exception as e:
                        print(e)
                        created = self.env['woocommerce.product.update.logs'].create({
                            'odoo_id': odoo_product.id,
                            'sku': odoo_product.id,
                            'woo_id': odoo_product.woocommerce_product_id,
                            'status': 'error',
                            'details': str(e),
                            'main_id': self.id
                        })
                else:
                    odoo_product.is_woocommerce_update_required = False

        return 1

    # except Exception as e:
    #     return 0
    def update_old_orders(self):

        woocomm = self.env['woocommerce.main'].search([('name', '=', 'Woocommerce Integration')])

        try:
            self.order_woo_to_odoo_delay = 1
            if self.order_woo_to_odoo_active:
                if self.order_woo_to_odoo_from_date:
                    print("orders Function")

                    wcapi = API(
                        url=woocomm.url,
                        consumer_key=woocomm.consumer_key,
                        consumer_secret=woocomm.consumer_secret,
                        version="wc/v3",
                        query_string_auth=True,
                        verify_ssl=False
                    )

                    def findIDbyEmail(data, type):
                        address2 = data['address_2'] + ' ' + data['city'] + ' ' + data['country']
                        country_code = data['country']
                        get_country = self.env['res.country'].search([('code', '=', country_code)])
                        city = data['city']
                        if city == "" and data['country'] == 'SG':
                            city = 'singapore'
                        customer = self.env['res.partner'].search([
                            ('street', '=', data['address_1']),
                            ('street2', '=', address2),
                            ('zip', '=', data['postcode']),
                            ('mobile', '=', data['phone']),
                        ], limit=1)
                        if customer:
                            return customer
                        else:
                            d_customer = {
                                'name': data['first_name'] + ' ' + data['last_name'],
                                'street': data['address_1'],
                                'street2': address2,
                                'zip': data['postcode'],
                                'commercial_company_name': data['company'],
                                'company_type': 'person',
                                "company_id": self.company_id.id,
                                'source_name': "Woocommerce : " + str(self.name),
                                'woocommerce_instance_id': self.id,
                                'mobile': data['phone'],
                                'phone': data['phone'],
                                'email': data['email'] if 'email' in data.keys() else '',
                                'type': type,
                                'city': city,
                                'country_id': get_country.id,

                            }

                            created_customer = self.env['res.partner'].create(d_customer)

                            return created_customer

                    wo = wcapi.get("orders/" + str(15696)).json()
                    try:
                        # raise UserError(wo)
                        billing_customer = 0
                        shipping_customer = 0
                        billing_obj = 0
                        if 'billing' in wo.keys():
                            billing_obj = findIDbyEmail(wo['billing'], 'invoice')
                            billing_customer = billing_obj.id
                        if 'shipping' in wo.keys():
                            ship = wo['shipping']
                            if ship['address_1'] or ship['address_2']:
                                shipping_customer_data = findIDbyEmail(wo['shipping'], 'delivery')
                                if not shipping_customer_data.phone:
                                    shipping_customer_data.phone = billing_obj.phone
                                    shipping_customer = shipping_customer_data.id
                                shipping_customer = shipping_customer_data.id


                            else:
                                if 'phone' not in ship.keys() or not ship['phone']:
                                    ship['phone'] = billing_obj.phone if billing_obj else '0'
                                wo['shipping']['first_name'] = "Not Set"
                                wo['shipping']['address_1'] = "Not Set"
                                wo['shipping']['address_1'] = "Not Set"
                                shipping_customer = findIDbyEmail(wo['shipping'], 'delivery').id

                        else:
                            shipping_customer = billing_customer

                        products = []
                        product_found = True
                        # raise UserError('here')

                        # raise UserError(str(wo['line_items']))
                        # for item in wo['tax_lines']:
                        #     tax=self.env['account.tax'].search([("name",'=',item['rate_code'])],limit=1)
                        #     if not tax:
                        #         tax=self.env['account.tax'].create({
                        #             'name':item['rate_code'],
                        #             'type_tax_use':'sale',
                        #             'amount_type':'percent',
                        #             'amount':item['rate_percent']
                        #         })
                        for item in wo['line_items']:
                            product_id = self.env['product.product'].search(
                                [("company_id", '=', self.company_id.id), ('default_code', '=', item['sku'])], limit=1)
                            # taxes=product_id.taxes_id.ids
                            t_inseertt = []
                            # for t in taxes:
                            #
                            # raise UserError(str(t_inseertt))
                            # taxes_list
                            for taxes in item['taxes']:
                                for all_taxes in wo['tax_lines']:
                                    if taxes['id'] == all_taxes['rate_id']:
                                        t = self.env['account.tax'].search([("name", '=', all_taxes['rate_code'])],
                                                                           limit=1)
                                        if not t:
                                            t = self.env['account.tax'].create({
                                                'name': all_taxes['rate_code'],
                                                'type_tax_use': 'sale',
                                                'amount_type': 'percent',
                                                'amount': all_taxes['rate_percent']
                                            })
                                        t_inseertt.append((4, t.id))

                            raise UserError(str(t_inseertt))
                            if product_id:
                                x = {
                                    'tax_id': t_inseertt if t_inseertt else False,
                                    'product_id': product_id.id,
                                    'product_uom_qty': item['quantity'],
                                    'price_unit': float(item['subtotal']) / int(item['quantity']),
                                    # 'tax_id':False
                                }
                                products.append((0, 0, x))
                            # else:
                            #     product_found=False
                        ## add shipping lines
                        # raise UserError('1')
                        for item in wo['shipping_lines']:
                            product_id = self.env['product.product'].search(
                                [("company_id", "=", self.company_id.id), ('default_code', '=', item['method_id'])],
                                limit=1)
                            if not product_id:
                                product_data = {
                                    "name": item["method_title"],
                                    "default_code": item['method_id'],
                                    "detailed_type": "service",
                                    "purchase_ok": False,
                                    "company_id": self.company_id.id,
                                    # "price_unit":0
                                    'source_name': "Woocommerce : " + str(self.name),
                                    'woocommerce_instance_id': self.id,

                                }

                                product_id = self.env['product.product'].create(product_data)
                                product_id.product_tmpl_id.source_name = product_id.source_name
                                product_id.product_tmpl_id.woocommerce_instance_id = product_id.woocommerce_instance_id
                                product_id.product_tmpl_id.company_id = product_id.company_id
                            x = {
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'price_unit': item['total'],
                            }
                            products.append((0, 0, x))

                        if wo['discount_total'] != "0.00":
                            product_id = self.env['product.product'].search(
                                [("name", "=", "Discount"), ("detailed_type", "=", "service")], limit=1)
                            if not product_id:
                                product_data = {
                                    "name": "Discount",
                                    "default_code": "Discount",
                                    "detailed_type": "service",
                                    "purchase_ok": False,
                                    "company_id": self.company_id.id,
                                    # "price_unit":0
                                    'source_name': "Woocommerce : " + str(self.name),
                                    'woocommerce_instance_id': self.id,

                                }

                                product_id = self.env['product.product'].create(product_data)
                                product_id['sync_to_woocommerce'] = False
                            coupon_code = str(wo['coupon_lines'][0]['code'])
                            x = {
                                'product_id': product_id.id,
                                'product_uom_qty': 1,
                                'price_unit': -float(str(wo['discount_total'])),
                                'name': f"Coupon Code: {coupon_code}",
                            }
                            products.append((0, 0, x))
                        # raise UserError(products)
                        # raise UserError(product_found)

                        if product_found:
                            # raise UserError('here')

                            exisit = self.env['sale.order'].search(
                                [('origin', '=', wo['id']), ('company_id', '=', self.company_id.id),
                                 ('source_ecommerce2', '=', self.name)])
                            if not exisit:

                                # woo_pm=wo.get('payment_method_title',"")
                                # if woo_pm:
                                #     PM= self.env['account.payment.method'].search([('name','=',woo_pm)])
                                #     if not PM:
                                #         PM=self.env['account.payment.method'].create({
                                #             'name':wo.get('payment_method_title',""),
                                #             'payment_type':'inbound',
                                #             'code':str(woo_pm).lower()
                                #         })
                                # woo_curr = str(wo['currency'])
                                # currency = self.env['res.currency'].search([('name', '=', woo_curr)])
                                order = {
                                    'partner_id': billing_customer,
                                    'partner_invoice_id': billing_customer,
                                    'partner_shipping_id': shipping_customer,
                                    # 'pricelist_id': 2,
                                    'name': "WOO" + str(wo['id']),
                                    'source_name': "Woocommerce : " + str(self.name),
                                    'woocommerce_instance_id': self.id,
                                    'state': 'sale',
                                    'payment_method_main': 1,
                                    'date_order': wo['date_created'].replace('T', ' '),
                                    'order_line': products,
                                    'origin': wo['id'],
                                    'woocommerce_order_id': wo['id'],
                                    'company_id': self.company_id.id,
                                    # 'origin':wo['status'],
                                    'source_ecommerce2': self.name,
                                    #  'currency_id':currency.id,
                                    'note': wo['customer_note'],
                                    'woo_currency': wo['currency'],
                                }

                                # raise UserError(str(order))

                                # order['internal_note']=wo["customer_note"] if wo["customer_note"] else ''
                                ##

                                created = self.env['sale.order'].create(order)
                                if wo['status'] == 'failed':
                                    created.action_cancel()

                                order_lines = self.env['sale.order.line'].search([('order_id', '=', created.id)])
                                # for ol in order_lines:
                                #     taxes=[]
                                #     for t in ol.product_id.taxes_id.ids:
                                #         taxes.append((4,t))
                                #     ol.write({'tax_id': taxes if taxes else False})

                                # invoice=created._create_invoices()
                                # if invoice:

                                # a=self.env['account.payment.register'].create({
                                #     'communication':invoice.name,
                                #     'amount':invoice.amount_residual,

                                # })

                                # a.action_create_payments()

                                created_log = self.env['woocommerce.orders.logs'].create({
                                    'odoo_id': created.id,
                                    'woo_id': wo['id'],
                                    'customer_name': billing_obj.name,
                                    'status': 'complete',
                                    'details': "Order Has Been Created Successfully",
                                    'main_id': self.id
                                })
                                self.order_woo_to_odoo_from_date = datetime.datetime.now().date()
                            else:
                                raise UserError('not exist')

                        else:
                            created_log = self.env['woocommerce.orders.logs'].create({
                                'woo_id': wo['id'],
                                'status': 'error',
                                'details': "Product Not Found In Odoo",
                                'main_id': self.id
                            })

                    except Exception as e:
                        # raise UserError(str(e))
                        print(e)
                        created_log = self.env['woocommerce.orders.logs'].create({
                            'woo_id': wo['id'],
                            'status': 'error',
                            'details': str(e),
                            'main_id': self.id
                        })

                else:
                    raise UserError("Date Field Not Set")
            else:
                raise UserError("Activate it first!!")

        except Exception as e:
            # raise UserError(str(e))
            return 0

    def download_orders(self):

        # raise UserError("Test")

        try:
            self.order_woo_to_odoo_delay = 1
            if self.order_woo_to_odoo_active:
                if self.order_woo_to_odoo_from_date:
                    print("orders Function")

                    wcapi = API(
                        url=self.url,
                        consumer_key=self.consumer_key,
                        consumer_secret=self.consumer_secret,
                        version="wc/v3",
                        query_string_auth=True,
                        verify_ssl=False
                    )

                    def findIDbyEmail(data, type):
                        address2 = data['address_2'] + ' ' + data['city'] + ' ' + data['country']
                        country_code = data['country']
                        get_country = self.env['res.country'].search([('code', '=', country_code)])
                        city = data['city']
                        if city == "" and data['country'] == 'SG':
                            city = 'singapore'
                        customer = self.env['res.partner'].search([
                            ('street', '=', data['address_1']),
                            ('street2', '=', address2),
                            ('zip', '=', data['postcode']),
                            ('mobile', '=', data['phone']),
                        ], limit=1)
                        if customer:
                            return customer
                        else:
                            d_customer = {
                                'name': data['first_name'] + ' ' + data['last_name'],
                                'street': data['address_1'],
                                'street2': address2,
                                'zip': data['postcode'],
                                'commercial_company_name': data['company'],
                                'company_type': 'person',
                                "company_id": self.company_id.id,
                                'source_name': "Woocommerce : " + str(self.name),
                                'woocommerce_instance_id': self.id,
                                'mobile': data['phone'],
                                'phone': data['phone'],
                                'email': data['email'] if 'email' in data.keys() else '',
                                'type': type,
                                'city': city,
                                'country_id': get_country.id,

                            }

                            created_customer = self.env['res.partner'].create(d_customer)

                            return created_customer

                    woo_orders = []
                    page = 1
                    DN = str(self.order_woo_to_odoo_from_date.strftime("%Y-%m-%d"))
                    # Schedule_actions = fields.Many2one(comodel_name='ir.cron', string="Cron Job")
                    r = wcapi.get("orders/", params={"per_page": 100, "page": page, "after": DN + "T00:00:00"}).json()
                    woo_orders.extend(r)
                    # raise UserError(str(woo_orders))
                    if woo_orders[0] != 'code':
                        while r != []:
                            page += 1
                            r = wcapi.get("orders/",
                                          params={"per_page": 100, "page": page, "after": DN + "T00:00:00"}).json()
                            woo_orders.extend(r)
                        print(woo_orders)
                        for wo in woo_orders:

                            if str(wo['status']) in ["pending", "cancelled"]:
                                continue

                            try:
                                billing_customer = 0
                                shipping_customer = 0
                                billing_obj = 0
                                if 'billing' in wo.keys():
                                    billing_obj = findIDbyEmail(wo['billing'], 'invoice')
                                    billing_customer = billing_obj.id
                                if 'shipping' in wo.keys():
                                    ship = wo['shipping']
                                    if ship['address_1'] or ship['address_2']:
                                        shipping_customer_data = findIDbyEmail(wo['shipping'], 'delivery')
                                        if not shipping_customer_data.phone:
                                            shipping_customer_data.phone = billing_obj.phone
                                            shipping_customer = shipping_customer_data.id
                                        shipping_customer = shipping_customer_data.id


                                    else:
                                        if 'phone' not in ship.keys() or not ship['phone']:
                                            ship['phone'] = billing_obj.phone if billing_obj else '0'
                                        wo['shipping']['first_name'] = "Not Set"
                                        wo['shipping']['address_1'] = "Not Set"
                                        wo['shipping']['address_1'] = "Not Set"
                                        shipping_customer = findIDbyEmail(wo['shipping'], 'delivery').id

                                else:
                                    shipping_customer = billing_customer

                                products = []
                                product_found = True

                                # raise UserError(str(wo['line_items']))
                                for item in wo['line_items']:
                                    product_id = self.env['product.product'].search(
                                        [("company_id", '=', self.company_id.id), ('default_code', '=', item['sku'])],
                                        limit=1)

                                    t_inseertt = []
                                    # for t in taxes:
                                    #
                                    # raise UserError(str(t_inseertt))
                                    # taxes_list
                                    for taxes in item['taxes']:
                                        for all_taxes in wo['tax_lines']:
                                            if taxes['id'] == all_taxes['rate_id']:
                                                t = self.env['account.tax'].search(
                                                    [("name", '=', all_taxes['rate_code'])], limit=1)
                                                if not t:
                                                    t = self.env['account.tax'].create({
                                                        'name': all_taxes['rate_code'],
                                                        'type_tax_use': 'sale',
                                                        'amount_type': 'percent',
                                                        'amount': all_taxes['rate_percent']
                                                    })
                                                t_inseertt.append((4, t.id))
                                    # raise UserError(str(t_inseertt))
                                    if product_id:
                                        x = {
                                            'tax_id': t_inseertt if t_inseertt else False,
                                            'product_id': product_id.id,
                                            'product_uom_qty': item['quantity'],
                                            'price_unit': float(item['subtotal']) / int(item['quantity']),
                                            # 'tax_id':False
                                        }
                                        products.append((0, 0, x))
                                    else:
                                        product_found = False
                                ## add shipping lines
                                for item in wo['shipping_lines']:
                                    product_id = self.env['product.product'].search(
                                        [("company_id", "=", self.company_id.id),
                                         ('default_code', '=', item['method_id'])], limit=1)
                                    if not product_id:
                                        product_data = {
                                            "name": item["method_title"],
                                            "default_code": item['method_id'],
                                            "detailed_type": "service",
                                            "purchase_ok": False,
                                            "company_id": self.company_id.id,
                                            # "price_unit":0
                                            'source_name': "Woocommerce : " + str(self.name),
                                            'woocommerce_instance_id': self.id,

                                        }

                                        product_id = self.env['product.product'].create(product_data)
                                        product_id.product_tmpl_id.source_name = product_id.source_name
                                        product_id.product_tmpl_id.woocommerce_instance_id = product_id.woocommerce_instance_id
                                        product_id.product_tmpl_id.company_id = product_id.company_id
                                    x = {
                                        'product_id': product_id.id,
                                        'product_uom_qty': 1,
                                        'price_unit': item['total'],
                                    }
                                    products.append((0, 0, x))

                                if wo['discount_total'] != "0.00":
                                    product_id = self.env['product.product'].search(
                                        [("name", "=", "Discount"), ("detailed_type", "=", "service")], limit=1)
                                    if not product_id:
                                        product_data = {
                                            "name": "Discount",
                                            "default_code": "Discount",
                                            "detailed_type": "service",
                                            "purchase_ok": False,
                                            "company_id": self.company_id.id,
                                            # "price_unit":0
                                            'source_name': "Woocommerce : " + str(self.name),
                                            'woocommerce_instance_id': self.id,

                                        }

                                        product_id = self.env['product.product'].create(product_data)
                                        product_id['sync_to_woocommerce'] = False
                                    coupon_code = str(wo['coupon_lines'][0]['code'])
                                    x = {
                                        'product_id': product_id.id,
                                        'product_uom_qty': 1,
                                        'price_unit': -float(str(wo['discount_total'])),
                                        'name': f"Coupon Code: {coupon_code}",
                                    }
                                    products.append((0, 0, x))

                                if product_found:
                                    exisit = self.env['sale.order'].search(
                                        [('origin', '=', wo['id']), ('company_id', '=', self.company_id.id),
                                         ('source_ecommerce2', '=', self.name)])
                                    if not exisit:
                                        # woo_pm=wo.get('payment_method_title',"")
                                        # if woo_pm:
                                        #     PM= self.env['account.payment.method'].search([('name','=',woo_pm)])
                                        #     if not PM:
                                        #         PM=self.env['account.payment.method'].create({
                                        #             'name':wo.get('payment_method_title',""),
                                        #             'payment_type':'inbound',
                                        #             'code':str(woo_pm).lower()
                                        #         })
                                        # woo_curr = str(wo['currency'])
                                        # currency = self.env['res.currency'].search([('name', '=', woo_curr)])
                                        order = {
                                            'partner_id': billing_customer,
                                            'partner_invoice_id': billing_customer,
                                            'partner_shipping_id': shipping_customer,
                                            # 'pricelist_id': 2,
                                            'name': "WOO" + str(wo['id']),
                                            'source_name': "Woocommerce : " + str(self.name),
                                            'woocommerce_instance_id': self.id,
                                            'state': 'sale',
                                            'payment_method_main': 1,
                                            'date_order': wo['date_created'].replace('T', ' '),
                                            'order_line': products,
                                            'origin': wo['id'],
                                            'woocommerce_order_id': wo['id'],
                                            'company_id': self.company_id.id,
                                            # 'origin':wo['status'],
                                            'source_ecommerce2': self.name,
                                            #  'currency_id':currency.id,
                                            'note': wo['customer_note'],
                                            'woo_currency': wo['currency'],
                                        }

                                        # raise UserError(str(order))

                                        # order['internal_note']=wo["customer_note"] if wo["customer_note"] else ''
                                        ##

                                        created = self.env['sale.order'].create(order)
                                        if wo['status'] == 'failed':
                                            created.action_cancel()

                                        order_lines = self.env['sale.order.line'].search(
                                            [('order_id', '=', created.id)])
                                        # for ol in order_lines:
                                        #     taxes=[]
                                        #     for t in ol.product_id.taxes_id.ids:
                                        #         taxes.append((4,t))
                                        #     ol.write({'tax_id': taxes if taxes else False})

                                        # invoice=created._create_invoices()
                                        # if invoice:

                                        # a=self.env['account.payment.register'].create({
                                        #     'communication':invoice.name,
                                        #     'amount':invoice.amount_residual,

                                        # })

                                        # a.action_create_payments()

                                        created_log = self.env['woocommerce.orders.logs'].create({
                                            'odoo_id': created.id,
                                            'woo_id': wo['id'],
                                            'customer_name': billing_obj.name,
                                            'status': 'complete',
                                            'details': "Order Has Been Created Successfully",
                                            'main_id': self.id
                                        })
                                        self.order_woo_to_odoo_from_date = datetime.datetime.now().date()
                                else:
                                    created_log = self.env['woocommerce.orders.logs'].create({
                                        'woo_id': wo['id'],
                                        'status': 'error',
                                        'details': "Product Not Found In Odoo",
                                        'main_id': self.id
                                    })

                            except Exception as e:
                                # raise UserError(str(e))
                                print(e)
                                created_log = self.env['woocommerce.orders.logs'].create({
                                    'woo_id': wo['id'],
                                    'status': 'error',
                                    'details': str(e),
                                    'main_id': self.id
                                })

                else:
                    raise UserError("Date Field Not Set")
            else:
                raise UserError("Activate it first!!")
            return 0
        except Exception as e:
            # raise UserError(str(e))
            return 0

    def run_product_download(self):
        print("inside run_product_download")
        products = self.env['woocommerce.main'].search([])
        Notrun = True
        for o in products:
            if o.product_woo_to_odoo_delay == 0:
                o.product_woo_to_odoo_delay = 1
                Notrun = False
                o.download_product()
        if Notrun:
            for o in products:
                o.product_woo_to_odoo_delay = 0

    def run_product_upload(self):
        print("inside run_product_upload")
        products = self.env['woocommerce.main'].search([])
        Notrun = True
        for o in products:
            if o.product_odoo_to_woo_delay == 0:
                o.product_odoo_to_woo_delay = 1
                Notrun = False
                o.upload_product()
        if Notrun:
            for o in products:
                o.product_odoo_to_woo_delay = 0

    def run_product_update(self):
        print("inside run_product_update")
        products = self.env['woocommerce.main'].search([])
        Notrun = True
        for o in products:
            if o.produpdate_odoo_to_woo_delay == 0:
                o.produpdate_odoo_to_woo_delay = 1
                Notrun = False
                o.update_product()
        if Notrun:
            for o in products:
                o.produpdate_odoo_to_woo_delay = 0

    def run_order_download(self):
        print("inside run_order_download")
        orders = self.env['woocommerce.main'].search([])
        Notrun = True
        for o in orders:
            if o.order_woo_to_odoo_delay == 0:
                o.write({'order_woo_to_odoo_delay': 1})
                Notrun = False
                o.download_orders()
        if Notrun:
            for o in orders:
                o.order_woo_to_odoo_delay = 0

    def run_order_update(self):
        print("inside run_order_update")
        orders = self.env['woocommerce.main'].search([])
        for o in orders:
            o.update_status()


###############API#######################


from requests import request
from json import dumps as jsonencode
from time import time
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
from time import time
from random import randint
from hmac import new as HMAC
from hashlib import sha1, sha256
from base64 import b64encode
from collections import OrderedDict
from urllib.parse import urlencode, quote, unquote, parse_qsl, urlparse


class OAuth(object):
    """ API Class """

    def __init__(self, url, consumer_key, consumer_secret, **kwargs):
        self.url = url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.version = kwargs.get("version", "v3")
        self.method = kwargs.get("method", "GET")
        self.timestamp = kwargs.get("oauth_timestamp", int(time()))

    def get_oauth_url(self):
        """ Returns the URL with OAuth params """
        params = OrderedDict()

        if "?" in self.url:
            url = self.url[:self.url.find("?")]
            for key, value in parse_qsl(urlparse(self.url).query):
                params[key] = value
        else:
            url = self.url

        params["oauth_consumer_key"] = self.consumer_key
        params["oauth_timestamp"] = self.timestamp
        params["oauth_nonce"] = self.generate_nonce()
        params["oauth_signature_method"] = "HMAC-SHA256"
        params["oauth_signature"] = self.generate_oauth_signature(params, url)

        query_string = urlencode(params)

        return f"{url}?{query_string}"

    def generate_oauth_signature(self, params, url):
        """ Generate OAuth Signature """
        if "oauth_signature" in params.keys():
            del params["oauth_signature"]

        base_request_uri = quote(url, "")
        params = self.sorted_params(params)
        params = self.normalize_parameters(params)
        query_params = ["{param_key}%3D{param_value}".format(param_key=key, param_value=value)
                        for key, value in params.items()]

        query_string = "%26".join(query_params)
        string_to_sign = f"{self.method}&{base_request_uri}&{query_string}"

        consumer_secret = str(self.consumer_secret)
        if self.version not in ["v1", "v2"]:
            consumer_secret += "&"

        hash_signature = HMAC(
            consumer_secret.encode(),
            str(string_to_sign).encode(),
            sha256
        ).digest()

        return b64encode(hash_signature).decode("utf-8").replace("\n", "")

    @staticmethod
    def sorted_params(params):
        ordered = OrderedDict()
        base_keys = sorted(set(k.split('[')[0] for k in params.keys()))

        for base in base_keys:
            for key in params.keys():
                if key == base or key.startswith(base + '['):
                    ordered[key] = params[key]

        return ordered

    @staticmethod
    def normalize_parameters(params):
        """ Normalize parameters """
        params = params or {}
        normalized_parameters = OrderedDict()

        def get_value_like_as_php(val):
            """ Prepare value for quote """
            try:
                base = basestring
            except NameError:
                base = (str, bytes)

            if isinstance(val, base):
                return val
            elif isinstance(val, bool):
                return "1" if val else ""
            elif isinstance(val, int):
                return str(val)
            elif isinstance(val, float):
                return str(int(val)) if val % 1 == 0 else str(val)
            else:
                return ""

        for key, value in params.items():
            value = get_value_like_as_php(value)
            key = quote(unquote(str(key))).replace("%", "%25")
            value = quote(unquote(str(value))).replace("%", "%25")
            normalized_parameters[key] = value

        return normalized_parameters

    @staticmethod
    def generate_nonce():
        """ Generate nonce number """
        nonce = ''.join([str(randint(0, 9)) for i in range(8)])
        return HMAC(
            nonce.encode(),
            "secret".encode(),
            sha1
        ).hexdigest()


__title__ = "woocommerce-api"
__version__ = "3.0.0"
__author__ = "Claudio Sanches @ Automattic"
__license__ = "MIT"


class API(object):
    """ API Class """

    def __init__(self, url, consumer_key, consumer_secret, **kwargs):
        self.url = url
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.wp_api = kwargs.get("wp_api", True)
        self.version = kwargs.get("version", "wc/v3")
        self.is_ssl = self.__is_ssl()
        self.timeout = kwargs.get("timeout", 30)
        self.verify_ssl = kwargs.get("verify_ssl", True)
        self.query_string_auth = kwargs.get("query_string_auth", False)
        self.user_agent = kwargs.get("user_agent", f"WooCommerce-Python-REST-API/{__version__}")

    def __is_ssl(self):
        """ Check if url use HTTPS """
        return self.url.startswith("https")

    def __get_url(self, endpoint):
        """ Get URL for requests """
        url = self.url
        api = "wc-api"

        if url.endswith("/") is False:
            url = f"{url}/"

        if self.wp_api:
            api = "wp-json"

        return f"{url}{api}/{self.version}/{endpoint}"

    def __get_oauth_url(self, url, method, **kwargs):
        """ Generate oAuth1.0a URL """
        oauth = OAuth(
            url=url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version=self.version,
            method=method,
            oauth_timestamp=kwargs.get("oauth_timestamp", int(time()))
        )

        return oauth.get_oauth_url()

    def __request(self, method, endpoint, data, params=None, **kwargs):
        """ Do requests """
        if params is None:
            params = {}
        url = self.__get_url(endpoint)
        auth = None
        headers = {
            "user-agent": f"{self.user_agent}",
            "accept": "application/json"
        }

        if self.is_ssl is True and self.query_string_auth is False:
            auth = HTTPBasicAuth(self.consumer_key, self.consumer_secret)
        elif self.is_ssl is True and self.query_string_auth is True:
            params.update({
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret
            })
        else:
            encoded_params = urlencode(params)
            url = f"{url}?{encoded_params}"
            url = self.__get_oauth_url(url, method, **kwargs)

        if data is not None:
            data = jsonencode(data, ensure_ascii=False).encode('utf-8')
            headers["content-type"] = "application/json;charset=utf-8"
        resp = []
        withoutError = True
        error = ""
        try:
            resp = request(
                method=method,
                url=url,
                verify=self.verify_ssl,
                auth=auth,
                params=params,
                data=data,
                timeout=self.timeout,
                headers=headers,
                **kwargs
            )
        except Exception as e:

            withoutError = False
            error = str(e)
        if not withoutError:
            raise UserError(
                "Exception on Woocommerce side. Woocommerce API might be down temporarily. Please try again after few hours.\n\n\n" + str(
                    error))

        return resp

    def get(self, endpoint, **kwargs):
        """ Get requests """
        return self.__request("GET", endpoint, None, **kwargs)

    def post(self, endpoint, data, **kwargs):
        """ POST requests """
        return self.__request("POST", endpoint, data, **kwargs)

    def put(self, endpoint, data, **kwargs):
        """ PUT requests """
        return self.__request("PUT", endpoint, data, **kwargs)

    def delete(self, endpoint, **kwargs):
        """ DELETE requests """
        return self.__request("DELETE", endpoint, None, **kwargs)

    def options(self, endpoint, **kwargs):
        """ OPTIONS requests """
        return self.__request("OPTIONS", endpoint, None, **kwargs)
