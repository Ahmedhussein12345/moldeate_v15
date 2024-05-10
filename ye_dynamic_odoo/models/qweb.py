import json
import ast
from odoo import models, api, fields
import collections
from lxml import etree, html

from odoo.addons.base.models.qweb import QWeb
from textwrap import dedent, indent as _indent
from lxml import etree

compile_node = QWeb._compile_node
compile_directive_field = QWeb._compile_directive_field
compile_directive_content = QWeb._compile_directive_content
compile_directive_esc = QWeb._compile_directive_esc
render_supper = QWeb._render
compile_dynamic_attributes = QWeb._compile_dynamic_attributes
compile_directive_set = QWeb._compile_directive_set
compile_directive_foreach = QWeb._compile_directive_foreach
compile_directive_options = QWeb._compile_directive_options
is_static_node = QWeb._is_static_node


def _is_static_node(self, el, options):
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            if options.get("EditReport", False):
                return False
    return is_static_node(self, el, options)

def _render(self, template, values=None, **options):
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            self.clear_caches()
            options["EditReport"] = True
            return render_supper(self.with_context(inherit_branding=from_odo_studio), template, values=values, **options)
        return render_supper(self, template, values=values, **options)
    return render_supper(self, template, values=values, **options)


def get_field_chain(self, attribute, first=True):
    root_param = []
    if isinstance(attribute, ast.Attribute):
        root_param.append(attribute.attr)
        root_param += self.get_field_chain(attribute.value, False)
    elif isinstance(attribute, ast.Call):
        root_param.append(attribute.args[0].s)
    if first:
        root_param.reverse()
    return root_param


def _compile_directive_set(self, el, options, indent):
    from_odo_studio = False
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
    if from_odo_studio:
        value_edit = False
        var_name = el.get('t-set')
        if 't-value' in el.attrib:
            value_edit = el.get('t-value')
    result = compile_directive_set(self, el, options, indent)
    if from_odo_studio:
        if value_edit:
            result.append(self._indent(f"{var_name}_edit = values[{repr(var_name)}]", indent))
    return result


def _compile_directive_foreach(self, el, options, indent):
    from_odo_studio = False
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            var_name = el.get('t-as').replace('.', '_')
            value_edit = el.get('t-foreach')
    result = compile_directive_foreach(self, el, options, indent)
    if from_odo_studio and value_edit:
        return [self._indent(f"{var_name}_edit = {self._compile_expr(value_edit)} or []", indent)] + result
        # return [self._indent(f"{var_name}_edit = {value_edit}", indent)] + result
        # return [ast.Assign(
        #     targets=[self._values_var(ast.Str(var_name + "_edit"), ctx=ast.Store())],
        #     value=ast.Str(value_edit)
        # )] + result
    return result


def _compile_directive_options(self, el, options, indent):
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            _options = el.get("t-options")
            if _options:
                el.set("options-values", _options)
    return compile_directive_options(self, el, options, indent)


def _compile_dynamic_attributes(self, el, options, indent):
    from_odo_studio = False
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
    code = compile_dynamic_attributes(self, el, options, indent)
    if from_odo_studio:
        for name, value in el.attrib.items():
            if name == "options-values":
                try:
                    code.append(
                        self._indent(
                            dedent(f"attrs['options-values'] = self.get_options_values({eval(value)})").strip(),
                            indent))
                except Exception:
                    pass
                finally:
                    pass
        code.append(self._indent(dedent(f"attrs['data-values'] = self.prepare_data_values(values)").strip(), indent))
    return code


def prepare_data_values(self, values):
    result = {}
    for key, val in values.items():
        type_data = type(val).__name__
        if type_data not in ["dict", "bool", "function", "method", "int", "str", "list", "module"] and hasattr(val,
                                                                                                               "_table"):
            type_data = {'model': getattr(val, "_name")}
        result[key] = type_data
    return json.dumps(result)


def get_options_values(self, option_value):
    for name, value in option_value.items():
        if type(value) is bool:
            option_value[name] = str(value).lower()
    return json.dumps(option_value)


def _compile_node(self, el, options, indent):
    from_odo_studio = False
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            path = options['root'].getpath(el)
            el.set("path-xpath", path)
            if not options.get("data-oe-xpath"):
                pass
            if options.get("oe_model") and not options.get("data-oe-model"):
                el.set("data-oe-model", options.get("oe_model"))

            if options.get("oe_id") and not options.get("data-oe-id"):
                el.set("data-oe-id", options.get("oe_id"))

    return compile_node(self, el, options, indent)


def _compile_directive_content(self, el, options, indent):
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio and el.getchildren():
            indexes = collections.defaultdict(lambda: 0)
            for item in el:
                indexes[item.tag] += 1
                if isinstance(item, etree._Comment):
                    continue
                if el.get("data-oe-model") and el.get("data-oe-id"):
                    data_model = el.get("data-oe-model")
                    data_id = el.get("data-oe-id")
                    options["oe_model"] = data_model
                    options["oe_id"] = data_id
    return compile_directive_content(self, el, options, indent)


def _compile_directive_field(self, el, options, indent):
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            el.set('field-ok', el.get('t-field'))
    res = compile_directive_field(self, el, options, indent)
    return res


def _compile_directive_esc(self, el, options, indent):
    if hasattr(self, "env"):
        from_odo_studio = self.env.context.get("from_odo_studio", False)
        if from_odo_studio:
            el.set("esc-ok", el.get("t-esc"))
    return compile_directive_esc(self, el, options, indent)


QWeb.get_field_chain = get_field_chain
QWeb.prepare_data_values = prepare_data_values
QWeb.get_options_values = get_options_values
QWeb._render = _render
QWeb._compile_dynamic_attributes = _compile_dynamic_attributes
QWeb._compile_directive_set = _compile_directive_set
QWeb._compile_directive_foreach = _compile_directive_foreach
QWeb._compile_directive_options = _compile_directive_options
QWeb._is_static_node = _is_static_node
#
QWeb._compile_node = _compile_node
QWeb._compile_directive_field = _compile_directive_field
QWeb._compile_directive_content = _compile_directive_content
QWeb._compile_directive_esc = _compile_directive_esc
