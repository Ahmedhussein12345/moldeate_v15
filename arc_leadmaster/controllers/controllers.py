# -*- coding: utf-8 -*-

from odoo.http import request, route, _logger
from odoo.addons.ks_curved_backend_theme.controllers.controllers import KsCurvedBackendTheme


class KsLmCurvedBackendTheme(KsCurvedBackendTheme):

    # Method inherit for make list density default. Code by Manmohan Singh
    @route(['/ks_list_renderer/attachments'], type='json', auth='user')
    def ks_list_render(self, **kw):
        """
        Fetches the details of attachments of all renderd records in List View.
        :param kw: {res_ids, model}
        :return: values {rec_id:[{att_id, att_name, att_mime}]}
        """
        res = super(KsLmCurvedBackendTheme, self).ks_list_render(**kw)
        global_obj = request.env.ref('ks_curved_backend_theme.ks_global_config_single_rec')

        if global_obj.scope_ks_list_density == 'Global':
            res[1] = {'ks_list_density': global_obj.ks_list_density}
        return res
