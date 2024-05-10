odoo.define('ye_dynamic_odoo.list_renderer', function(require) {

    var ListView = require('web.ListView');
    var FormView = require('web.FormView');
    var ListRenderer = require('web.ListRenderer');
    var relational_fields = require('web.relational_fields');
    var FieldMany2One = require('web.relational_fields').FieldMany2One;
    var Widget = require('web.Widget');
    var BasicModel = require('web.BasicModel');
    var widget = new Widget();
    var model = new BasicModel(widget);

    var ListController = require('web.ListController');
    // var QWeb = core.qweb;


    ListController.include({
        // custom_events: _.extend({}, ListController.prototype.custom_events, {
        //     stOpenRecord: 'stOpenRecord',
        // }),
        init: function (parent, model, renderer, params) {
            this._super(parent, model, renderer, params);
            // this.fromStudio = params.fromStudio;
            if (parent.searchview) {
                parent.searchview.listViewRender = renderer;
            }
        },
        // stOpenRecord: function (ev) {
        //     ev.stopPropagation();
        //     var record = this.model.get(ev.data.id, {raw: true});
        // },

        // _onOpenRecord: function (ev) {
        //     if (this.fromStudio) {
        //         alert("ok");
        //     }else {
        //         this._super(ev);
        //     }
        //     // ev.stopPropagation();
        //     // var record = this.model.get(ev.data.id, {raw: true});
        //     // this.trigger_up('switch_view', {
        //     //     view_type: 'form',
        //     //     res_id: record.res_id,
        //     //     mode: ev.data.mode || 'readonly',
        //     //     model: this.modelName,
        //     // });
        // },
    });

    ListRenderer.include({
        init: function (parent, state, params) {
            this._super(parent, state, params);
            this.viewInfo = params.viewInfo;
            this.search_domain = {};
            // this.fromStudio = params.fromStudio;
            this.parent = parent;
            this.showSearchAdvance = false;
            this.showSticky = false;
            if (this.arch ) {
                let search_advance = this.arch.attrs.search_advance;
                let sticky = this.arch.attrs.sticky;
                let serial = this.arch.attrs.serial;
                this.showSearchAdvance = [true, "true", "1", 1, "True"].includes(search_advance) ? true : false;
                this.showSticky = [true, "true", "1", 1, "True"].includes(sticky) ? true : false;
                this.serial = [true, "true", "1", 1, "True"].includes(serial) ? true : false;
            }
            this.fieldRender = {char: {render: this.renderFieldInput.bind(this)}, float: {render: this.renderFieldInput.bind(this)},
                                int: {render: this.renderFieldInput.bind(this)}, many2one: {render: this.renderFieldMany2one.bind(this)},
                                date: {render: this.renderFieldDate.bind(this)}, datetime: {render: this.renderFieldDate.bind(this)},
                                selection: {render: this.renderFieldSelection.bind(this)}
                }
        },
        // _onRowClicked: function (ev) {
        //     if (this.fromStudio) {
        //         if (!ev.target.closest('.o_list_record_selector') && !$(ev.target).prop('special_click')) {
        //             var id = $(ev.currentTarget).data('id');
        //             if (id) {
        //                 // alert("ok");
        //                 this.trigger_up('stOpenRecord', { id: id, target: ev.target });
        //             }
        //         }
        //         return true;
        //     }
        //     this._super(ev);
        // },
        // _renderHeaderCell: function (node) {
        //     let res = this._super(node);
        //     if (node.tag == "serial") {
        //         res.text(node.attrs.string);
        //     }
        //     return res;
        // },
        // _renderBodyCell: function (record, node, colIndex, options) {
        //     if (node.tag == "serial") {
        //         return $('<td>', {class: "td_serial"});
        //     }
        //     return this._super(record, node, colIndex, options);
        // },
        // _renderRows: function () {
        //     let self = this;
        //     if (this.serial) {
        //         return this.state.data.map((record, idx) => {
        //             let row = self._renderRow.bind(this)(record);
        //             row.find(".td_serial").text(idx + 1);
        //             return row
        //         });
        //     }
        //     return this._super();
        // },
        // _renderGroup: function (group, groupLevel) {
        //     let res = this._super(group, groupLevel);
        //     if (this.serial && !group.groupedBy.length && res.length) {
        //         $(res[0]).find("tr").each((idx, el) => {
        //             $(el).find(".td_serial").text(idx + 1);
        //         });
        //     }
        //     return res;
        // },
        // _renderRow: function (record) {
        //     let res = this._super(record);
        //     if (this.serial) {
        //         let serial = $('<td>', {class: "td_serial text-center"});
        //         res.find("td:first-child").before(serial);
        //     }
        //     return res;
        // },
        // _renderFooter: function () {
        //     let res = this._super();
        //     if (this.serial) {
        //         let serial = $('<td>', {class: "td_serial"});
        //         res.find("td:first-child").before(serial);
        //     }
        //     return res;
        // },
        // _renderGroupRow: function (group, groupLevel) {
        //     let res = this._super(group, groupLevel);
        //     if (this.serial) {
        //         let group = res.find(".o_group_name");
        //         res.find(".o_group_name").attr({colspan: parseInt(group.attr("colspan")) + 1});
        //     }
        //     return res;
        // },
        // renderSticky: function () {
        //     if (this.showSticky) {
        //         var $self = this;
        //         var o_content_area = $(".table-responsive")[0];
        //         function sticky() {
        //             $self.$el.find("table.o_list_table").each(function () {
        //                 $(this).stickyTableHeaders({scrollableArea: o_content_area, fixedOffset: 0.1});
        //             });
        //             let ab = $self.$el.find(".tableFloatingHeaderOriginal");
        //             if (ab.length) {
        //                 let top = ab.offset().top;
        //                 $self.$el.find(".o_optional_columns_dropdown_toggle").css({
        //                     zIndex: 100,
        //                     position: "fixed",
        //                     top: top + "px"
        //                 });
        //             }
        //         }
        //         function fix_body(position) {
        //             $("body").css({
        //                 'position': position,
        //             });
        //         }
        //         if (this.$el.parents('.o_field_one2many').length === 0) {
        //             sticky();
        //             fix_body("fixed");
        //             // $(window).unbind('resize', sticky).bind('resize', sticky);
        //             this.$el.css("overflow-x", "visible");
        //         }
        //         else {
        //             fix_body("relative");
        //         }
        //         $("div[class='o_sub_menu']").css("z-index", 4);
        //     }
        // },
        // _onResize: function () {
        //     this._super();
        //     // this.renderSticky();
        // },
        // _freezeColumnWidths: function () {
        //     if (!this.columnWidths && this.el.offsetParent === null) {
        //         // there is no record nor widths to restore or the list is not visible
        //         // -> don't force column's widths w.r.t. their label
        //         return;
        //     }
        //     const thElements = [...this.el.querySelectorAll('table thead:not(.tableFloatingHeaderOriginal) th')];
        //     if (!thElements.length) {
        //         return;
        //     }
        //     const table = this.el.getElementsByTagName('table')[0];
        //     let columnWidths = this.columnWidths;
        //
        //     if (!columnWidths) { // no column widths to restore
        //         // Set table layout auto and remove inline style to make sure that css
        //         // rules apply (e.g. fixed width of record selector)
        //         table.style.tableLayout = 'auto';
        //         thElements.forEach(th => {
        //             th.style.width = null;
        //             th.style.maxWidth = null;
        //         });
        //
        //         // Resets the default widths computation now that the table is visible.
        //         this._computeDefaultWidths();
        //
        //         // Squeeze the table by applying a max-width on largest columns to
        //         // ensure that it doesn't overflow
        //         columnWidths = this._squeezeTable();
        //     }
        //
        //     thElements.forEach((th, index) => {
        //         // Width already set by default relative width computation
        //         if (!th.style.width) {
        //             th.style.width = `${columnWidths[index]}px`;
        //         }
        //     });
        //
        //     // Set the table layout to fixed
        //     table.style.tableLayout = 'fixed';
        // },
        _prepareSearchDomains: function () {
            let result = [], fields = this.state.fields;
            Object.keys(this.search_domain).map((d, idx) =>{
                let field = fields[d], val = this.search_domain[d];
                if (field.type == 'datetime'){
                    val = val.split(" - ");
                    let formatClient = "DD/MM/YYYY", formatServer = "YYYY/MM/DD",
                        from = (moment(val[0], formatClient)).format(formatServer),
                        to = (moment(val[1] || val[0], formatClient)).format(formatServer);
                    result.push([d, '>=', `${from} 00:00:00`]);
                    result.push([d, '<=', `${to} 23:59:59`]);
                }else if (field.type == 'date') {
                    result.push([d, '=', val]);
                }else if (['int', 'float'].indexOf(field.type) >= 0) {
                    result.push([d, '=', parseFloat(val)]);
                }else {
                    result.push([d, 'ilike', val]);
                }
            });
            return result
        },
        searchRenderData: function () {
            let searchView = this.getParent()._controlPanel,
                search = searchView.getSearchQuery();
            searchView.trigger_up('search', search);
        },
        _hasContent: function () {
            let result = this._super();
            if (Object.keys(this.search_domain).length > 0) {
                return true;
            }
            return result;
        },
        renderFieldMany2one: function (field, container) {
            let self = this;
            const {name} = field;
            var many2one = new FieldMany2One(self, name, {...this.state, domain: [], getContext: () => {return []}, getDomain: () => {return []}}, {
                mode: 'edit',
                viewType: this.viewType,
            });
            many2one.appendTo(container).then(function () {
                many2one.$el.find("input").val(self.search_domain[name] || null);
            });
            const _setValue = function (value, options) {
                if (this.lastSetValue === value || (this.value === false && value === '')) {
                    return $.when();
                }
                this.lastSetValue = value;
                value = this._parseValue(value);
                this.$input.val(value.display_name);
                value ? (self.search_domain[name] = value.display_name) : (delete self.search_domain[name]);
                self.searchRenderData();
                var def = $.Deferred();
                return def;
            }

            many2one._setValue = _setValue.bind(many2one);
        },
        renderFieldInput: function (field, container) {
            let self = this, view = $('<input>'), {name} = field;
            view.keyup(function (e) {
                const value = $(e.currentTarget).val();
                value ? (self.search_domain[name] = value) : (delete self.search_domain[name]);
                if (e.keyCode == 13) {
                    self.searchRenderData();
                }
            });
            view.val(this.search_domain[name] || null);
            container.append(view);
        },
        renderFieldDate: function (field, container) {
            let self = this, {name} = field, view = $('<input name='+name+'>'), format = "DD/MM/YYYY",
                options = {autoUpdateInput: false, locale: {cancelLabel: 'Clear', format: format}};
            view.daterangepicker(options);
            view.change((ev) => {
                let value = ev.target.value;
                if (!value) {
                    delete self.search_domain[name];
                    self.searchRenderData();
                }
            });
            view.on('apply.daterangepicker', (ev, picker) => {
                const {startDate, endDate} = picker, val = startDate.format(format) + ' - ' + endDate.format(format);
                val ? (self.search_domain[name] = val) : (delete self.search_domain[name]);
                self.searchRenderData();
            });
            view.on('cancel.daterangepicker', () => {
                delete self.search_domain[name];
                self.searchRenderData();
            });
            view.val(this.search_domain[name] || null);
            container.append(view);
        },
        renderFieldSelection: function (field, container) {
            let self = this, {name} = field,
                view = $('<select><option></option></select>');
            field.selection.map((option) => {
                const [value, name] = option;
                view.append($('<option value='+value+'>'+name+'</option>'));
            });
            view.change(function () {
                let val = view.val();
                val ? (self.search_domain[name] = val) : (delete self.search_domain[name]);
                self.searchRenderData();
            });
            view.val(this.search_domain[name] || null);
            container.append(view);
        },
        renderSearch: function (node) {
            let name = node.attrs.name, $th = $('<th>'),
                field = {...this.state.fields[name], name: name};
            if (!field || !(field.type in this.fieldRender)) {
                return $th;
            }
            this.fieldRender[field.type].render(field, $th);
            return $th;
        },
        _renderHeader: function (isGrouped) {
            let res = this._super(isGrouped);
            if (this.showSearchAdvance && !res.find(".searchAdvance").length) {
                let $tr = $('<tr class="searchAdvance">').append(
                    _.map(this.columns, this.renderSearch.bind(this)));
                if (this.hasSelectors) {
                    $tr.prepend($('<th>'));
                }
                res.append($tr);
            }
            if (this.serial) {
                let serial = $('<th>', {class: "text-center th_serial"});
                serial.text("S.No");
                res.find("th:first-child").before(serial);
                res.find(".searchAdvance .th_serial").text("");
            }
            return res;
        },
    });
});
