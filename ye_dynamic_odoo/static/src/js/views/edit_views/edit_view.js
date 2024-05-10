/** @odoo-module alias=ye_dynamic_odoo.EditView**/
//
// odoo.define('ye_dynamic_odoo.EditView', function (require) {
// "use strict";
//

import {registry} from "@web/core/registry";
import core from "web.core";

var FormViewEdit = require("ye_dynamic_odoo.FormViewEdit");
var CalendarEdit = require("ye_dynamic_odoo.CalendarViewEdit");
var PivotViewEdit = require("ye_dynamic_odoo.PivotViewEdit");
var ListViewEdit = require("ye_dynamic_odoo.ListViewEdit");
var GraphViewEdit = require("ye_dynamic_odoo.GraphViewEdit");
var KanBanViewEdit = require("ye_dynamic_odoo.KanbanViewEdit");
// var ReportKanBan = require("ye_dynamic_odoo.ReportKanBan");
var ReportEdit = require("ye_dynamic_odoo.ReportEdit");
// var ListView = require("web.ListView");
var AutomationContent = require("ye_dynamic_odoo.AutomationContent");

import BasicModel from 'web.BasicModel';

import mixins from 'web.mixins';
import BasicView from 'web.BasicView';
// var ActionManager = require('web.ActionManager');
const serviceRegistry = registry.category("services");
// const ActionManager = serviceRegistry.get('action').start();
import {useService} from "@web/core/utils/hooks";
import {ComponentAdapter} from "web.OwlCompatibility";

var rootWidget = require('root.widget');

const actionRegistry = registry.category("actions");
import {session} from "@web/session";
// var session = require('web.session');
// import {session} from "@web/session";

var QWeb = core.qweb;
import Widget from "web.Widget";
// import PivotController from "../../../../../../../../odoo/addons/web/static/src/legacy/js/views/pivot/pivot_controller";
const {generateID} = require('web.utils');

var EditBasicView = BasicView.extend({
    init: function (parent, viewInfo, params) {
        if (viewInfo) {
            this.viewType = params.viewType;
            this._super(viewInfo, params);
        }
        this.rpc = useService("rpc");
    },
    _processArch(arch, fv) {
        if (fv.arch.tag == "form") {
            fv.fieldIdsToNames = {}; // maps field ids (identifying <field> nodes) to field names
        }
        return this._super(...arguments);
    },
    _processNode(node, fv) {
        if (fv.arch.tag == "form") {
            if (node.tag === 'field') {
                const name = node.attrs.name;
                let uid = node.attrs.id;
                if (!uid) {
                    uid = name in fv.fieldIdsToNames ? `${name}__${generateID()}__` : name;
                    node.attrs.id = uid;
                }
                fv.fieldIdsToNames[uid] = name;
            }
        }
        return this._super(...arguments);
    },
});

var EditViewModel = BasicModel.extend({
    init: function (parent) {
        this._super(parent);
        this.rpc = useService("rpc");
    },
    createNewView: function (data) {
        // const rpc = this.getParent().env.services.rpc;
        return this.rpc(`/web/dataset/call_kw/odo.studio`, {
            model: "odo.studio",
            method: 'create_new_view',
            args: [data],
            kwargs: {},
        });
    },
    onActionView: function (data, save = true) {
        // const rpc = this.getParent().env.services.rpc;
        this.rpc(`/web/dataset/call_kw/${data.model}`, {
            model: data.model,
            method: save ? 'store_view' : 'undo_view',
            args: [data.data],
            kwargs: {},
        }).then(function (result) {
            alert("Successfully");
            location.reload();
        });
    },
    getFieldsData: function (modelName) {
        // const rpc = this.getParent().env.services.rpc;
        return this.rpc(`/web/dataset/call_kw/${data.model}`, {
            model: "odo.studio",
            method: 'get_fields',
            args: [modelName],
            kwargs: {},
        });
    },
    onStoreView: function (data) {
        this.onActionView(data);
    },
    onUndoView: function (data) {
        this.onActionView(data, false);
    }
});


const EditView = Widget.extend(mixins.EventDispatcherMixin, {
    template: 'EditView',
    events: {
        'click ._headEdit .fa-close': 'onClose',
        'click ._headEdit .fa-minus': 'onMinus',
        'click ._headEdit .fa-expand': 'onExpand',
        'click ._aSave': 'onSaveView',
        'click ._aUndo': 'onRemoveView',
        'click ._aRemove': 'onRemoveNode',
        'click ._aStore': '_onStoreToDatabase',
    },
    init: function (parent, params) {
        this._super(parent);
        this.parent = parent;
        this.props = params;
        // this.controller = parent;
        this.action_manager = useService("action");

        this.vm = useService("view");
        this.start();
        // console.log(serviceRegistry)
    },
    start: function () {
        this.ref = {};
        this.viewParent = this;
        this.appState = odoo.studio.state;
        const {view_type} = this.appState;
        this.basicView = new EditBasicView(this, false, {viewType: view_type});
        this.model = new EditViewModel(this);
        this._processFieldsView = this.basicView._processFieldsView.bind(this.basicView);
        this.viewsInfo = {
            form: {
                widget: FormViewEdit,
                label: "FormView",
                icon: "fa-wpforms",
                subView: {form: {widget: FormViewEdit}, list: {widget: ListViewEdit}}
            },
            list: {widget: ListViewEdit, label: "ListView", icon: "fa-list-ul"},
            kanban: {widget: KanBanViewEdit, label: "Kanban", icon: "fa-th-large"},
            calendar: {widget: CalendarEdit, label: "Calendar", icon: "fa-calendar"},
            pivot: {widget: PivotViewEdit, label: "Pivot", icon: "fa-th"},
            graph: {widget: GraphViewEdit, label: "KanBan", icon: "fa-bar-chart"},
        };
        this.editType = {
            views: {label: "Views", classes: "viewEdit", render: this.renderViewViews.bind(this)},
            reports: {label: "Report", classes: "reportEdit", render: this.renderViewReport.bind(this)},
            automation: {
                label: 'Automations',
                model: "base.automation",
                title: "Automated Actions",
                classes: "accessEdit",
                render: this.renderViewAccess.bind(this)
            },
            access_control: {
                label: 'Access Controls',
                model: "ir.model.access",
                title: "Access Control Lists",
                classes: "accessEdit",
                render: this.renderViewAccess.bind(this)
            },
            filter_rules: {
                label: "Filter Rules",
                model: "ir.filters",
                title: "Filter Rules",
                classes: "accessEdit",
                render: this.renderViewAccess.bind(this)
            }
        };
        const viewType = this.appState.view_type;
        this.state = {viewType: viewType in this.viewsInfo ? viewType : "list", typeEdit: "views"};

        // const adapter = new ComponentAdapter(null, { Component: owl.Component });
        // // adapter.env = legacyEnv;
        // const W = Widget.extend({ do_push_state() {} });
        // const widget = new W(adapter);
        // this.parentWidget = widget;
    },
    setState: function (params) {
        Object.keys(params).map((key) => {
            this.state[key] = params[key];
        });
    },
    _makeDefaultRecord: function (modelName, params) {
        const {res_model} = this.action;
        return this.model._makeDefaultRecord(modelName || res_model, params);
    },
    onClose: function () {
        delete odoo.studio;
        window.location.reload();
        // this.$el.remove();
        // this.editToBase();
        // this.trigger_up("reset_edit_instance");
    },
    onMinus: function () {
        if (this.$el.hasClass("minus")) {
            this.$el.removeClass("minus");
            this.baseToEdit();
        } else {
            this.$el.addClass("minus");
            this.editToBase();
        }
    },
    onExpand: function () {
        this.$el.hasClass("expand") ? this.$el.removeClass("expand") : this.$el.addClass("expand");
    },
    onSaveView: function () {
        this.model.onStoreView(this.getViewData());
    },
    onRemoveView: function () {
        const {typeEdit} = this.state;
        this.model.onUndoView(typeEdit == "views" ? this.getViewData() : this.getReportData());
    },
    onClickView: function (viewType) {
        this.setState({viewType: viewType});
        this.switchView();
    },
    onClickTypeEdit: function (type) {
        this.setState({typeEdit: type});
        this.renderElement();
    },
    onRemoveNode: function (e) {
        e.stopPropagation();
        this.ref.view.onRemoveNode();
    },
    createNewView: function () {
        return this.model.createNewView(this.prepareNewView());
    },
    getViewState: function (viewId) {
        return this.model.get(viewId)
    },
    getViewData: function () {
        const params = {};
        if (this.ref.subView) {
            const {viewInfo, nodeId} = this.ref.subView, type = viewInfo.type;
            params.model = "odo.studio.sub_view";
            params.data = this.ref.view.getSubViewData(nodeId, type);
            if (type == "form") {
                params.data.model_name = viewInfo.model;
                params.data.new_fields = this.ref.subView.prepareNewField();
            }
        } else {
            params.model = "odo.studio";
            params.data = this.ref.view.getData();
        }
        return params;
    },
    getReportData: function () {
        const params = {};
        params.model = "odo.studio.report";
        params.data = this.ref.view.getReportId();
        return params;
    },
    getViewInfo: function () {
        let self = this;
        const {viewType} = this.state;
        if (viewType in self.fieldsViews) {
            let viewInfo = this._processFieldsView(self.fieldsViews[viewType], viewType);
            this.basicView = new EditBasicView(this.viewParent, viewInfo, {viewType: viewType});
            this._processFieldsView = this.basicView._processFieldsView.bind(this.basicView);
            return {...viewInfo, arch_xml: self.fieldsViews[viewType].arch, fields: {...viewInfo.fields}};
        }
    },
    prepareNewView: function () {
        let {res_model} = this.action, {viewType} = this.state,
            viewInfo = {view_mode: viewType, action_id: this.action.id}, data = {}, params = {};
        if (viewType == "calendar" && this.fieldsGet) {
            let fieldsDate = Object.keys(this.fieldsGet).filter((fieldName) => {
                let field = this.fieldsGet[fieldName];
                return ["date", "datetime"].includes(field.type)
            });
            if (fieldsDate.length) {
                params.name = fieldsDate[0];
            }
        }
        let viewTemplate = `ViewEdit.${viewType.charAt(0).toUpperCase() + viewType.slice(1)}Default`;
        data.arch = ["calendar"].includes(viewType) ? QWeb.render(viewTemplate, params) : QWeb.templates[viewTemplate].innerHTML;
        data.name = `${res_model}.${viewType}`;
        data.model = res_model;
        viewInfo.data = data;

        return viewInfo;
    },
    reloadProperty: function () {
        this.$el.find('._editProperty ._cCeP').empty().append(this.ref.view.ref.property.$el);
    },
    showSubView: function (node, viewInfo) {
        const {viewType} = this.state, subView = this.viewsInfo[viewType].subView;
        if (viewInfo.type in subView) {
            let basicView = new EditBasicView(this.viewParent, viewInfo, {viewType: viewInfo.type});
            let View = new subView[viewInfo.type].widget(this, {
                viewInfo: viewInfo, _processFieldsView: basicView._processFieldsView.bind(basicView),
                action: this.action, editView: this, rootViewType: viewType, basicView: basicView,
                nodeId: node.nodeId, parent_view_id: this.getViewInfo().view_id || false
            });
            this.ref.subView = View;
            this.ref.view.disableSort();
            this.$el.addClass("_showSubView");
            this.$el.find('._editView ._wSubView').addClass("show").append(View._renderContent());
            this.$el.find('._editProperty ._cCeP').empty().append(View._renderProperty());
        }
    },
    closeSubView: function (e) {
        e.stopPropagation();
        e.stopImmediatePropagation();
        const nodeId = this.ref.subView.nodeId, subViewType = this.ref.subView.viewInfo.type;
        $(e.currentTarget).empty().removeClass("show");
        this.$el.removeClass("_showSubView");
        delete this.ref.subView;
        this.ref.view.onCloseSubView(nodeId, subViewType);
        this.ref.view._renderProperty(true);
        this.ref.view.enableSort();
        if (nodeId) {
            this.ref.view.ref.content.reloadNode(nodeId);
        }
    },
    switchView: async function () {
        const self = this, {viewType} = this.state;
        if (viewType in self.fieldsViews) {
            const viewInfo = this.getViewInfo();
            if (!this.fieldsGet) {
                this.fieldsGet = viewInfo.fieldsGet;
            }
            this.ref.view = new this.viewsInfo[viewType].widget(rootWidget,
                {
                    editView: this,
                    action: this.action,
                    _processFieldsView: this._processFieldsView,
                    rootViewType: viewType,
                    reloadProperty: this.reloadProperty.bind(this),
                    viewInfo: viewInfo,
                    basicView: this.basicView,
                    // controller: this.controller,
                    showSubView: this.showSubView.bind(this)
                });
            this.$el.find('._editView ._wMainView').empty().append(this.ref.view._renderContent());
            this.$el.find('._editProperty ._cCeP').empty().append(this.ref.view._renderProperty());
            this.$el.attr({'view-type': viewType});
        } else {
            if (window.confirm("Do you really want to active view ?")) {
                await this.createNewView();
                self.renderElement();
            }
        }
    },
    editToBase: function () {
        $('.o_web_client').removeClass("editMode");
        $('.o_menu_systray').removeClass("hide");
        $('.edit_menu_top').remove();
    },
    baseToEdit: function () {
        $(".edit_menu_top").remove();
        let menuTop = $(QWeb.render("Edit.MenuTop", {}));
        menuTop.find("li").click(this.onClose.bind(this));
        $('.o_main_navbar').append(menuTop);
        $(".o_content").addClass("_overHide");
        $(".o_web_client").addClass("editMode");
        $(".o_menu_systray").addClass("hide");
    },
    bindStyle: function () {
        $("._wIBi, ._editProperty").removeClass("hide");
    },
    bindAction: function () {
        this.$el.find("._wSubView").click(this.closeSubView.bind(this));
        this.$el.find("._aRemove").click(this.onRemoveNode.bind(this));
    },
    renderMenuView: function () {
        const {viewType} = this.state;
        let wrap = this.$el.find('._hEView'), wrapUl = $(QWeb.render("EditView.menu", {}))
        Object.keys(this.viewsInfo).map((type) => {
            let view = this.viewsInfo[type], item = $(QWeb.render("EditView.menuItem", {...view}));
            if (type == viewType) {
                item.addClass("active");
            }
            if (!(type in this.fieldsViews)) {
                item.addClass("notAvailable")
            }
            item.click((e) => {
                // e.stopPropagation();
                // e.stopImmediatePropagation();
                wrapUl.find("li.active").removeClass("active");
                item.addClass("active");
                this.onClickView(type);
            });
            wrapUl.append(item);
        });
        wrap.append(wrapUl);
    },
    renderMenu: function () {
        const {typeEdit} = this.state, wrap = this.$el.find('._hEView'),
            wrapUl = $(QWeb.render("EditView.menu", {}));
        wrapUl.addClass("_wrapEditType");
        Object.keys(this.editType).map((type) => {
            let typeInfo = this.editType[type], item = $(QWeb.render("EditView.menuItem", {...typeInfo}));
            if (type == typeEdit) {
                item.addClass("active");
            }
            item.click(() => {
                wrapUl.find("li.active").removeClass("active");
                item.addClass("active");
                this.onClickTypeEdit(type);
            });
            wrapUl.append(item);
        });
        wrap.append(wrapUl);
    },
    renderViewAccess: function () {
        const self = this, {typeEdit} = this.state, {model, title} = this.editType[typeEdit],
            container = self.$el.find("._wMainView").empty();

        const params = {
            resModel: model,
            views: [[false, 'list'], [false, 'form']],
            context: session.user_context,
        };
        const options = {
            // actionId: this.action.id,
            // loadActionMenus: true,
            // loadIrFilters: true,
        };
        // this.vm.loadViews(params, options)
        this.vm.loadViews(params, options).then((viewInfo) => {
            const automationContent = new AutomationContent(this.viewParent, {
                modelName: model, viewInfo: viewInfo,
                title: title, domain: [['model_name', '=', this.action.res_model]]
            });
            automationContent.renderElement();
            container.append(automationContent.$el);
        });
    },
    renderViewReport: async function () {
        const self = this, domain = self.action.domain || [];
        const reportAction = await this.action_manager.loadAction("base.ir_action_report");
        reportAction.resModel = reportAction.res_model;
        this.vm.loadViews(reportAction, {}).then((fieldsViews) => {
            const viewInfo = self._processFieldsView(fieldsViews["kanban"], "kanban");
            let reportEdit = new ReportEdit(self.viewParent,
                {
                    action: reportAction,
                    domain: domain,
                    action_manager: this.action_manager,
                    reloadProperty: self.reloadProperty.bind(self),
                    viewInfo: {...viewInfo, fields: {...viewInfo.fields}}
                });
            reportEdit.attachTo(self.$el.find('._editView')).then(function () {
                self.$el.find('._editView ._wMainView').empty().append(reportEdit._renderContent());
                self.$el.find('._editProperty ._cCeP').empty().append(reportEdit._renderProperty());
            });
            self.ref.view = reportEdit;
        });
    },
    renderViewViews: async function () {
        const self = this;
        // , state = $.bbq.getState(true);
        // this.action_manager = new ActionManager(this.viewParent, session.user_context);
        // this.action_manager.isInDOM = true;
        // actionRegistry.content[state.action] = 'Ok';
        // this.action_manager.doAction = function (action, options) {
        //     alert("ok")
        //     const props = {
        //         from_odo_studio: Math.random(),
        //         active_id: options.additional_context.active_id,
        //         active_ids: options.additional_context.active_ids,
        //         active_model: options.additional_context.active_model,
        //     }
        //     return self.action_manager.loadAction(action, props);
        //     // .then(function (action) {
        //     //     self.action_manager._preprocessAction(action, options);
        //     //     return action;
        //     // });
        // };
        // await self.action_manager.loadAction(action, props);
        odoo.rootStudio.env.bus.trigger("CLEAR-CACHES");
        this.action = await this.action_manager.loadAction(this.appState.action);
        const params = {
            resModel: this.action.res_model,
            views: this.action.views,
            context: this.action.context,
        };
        const options = {
            actionId: this.action.id,
            loadActionMenus: true,
            loadIrFilters: true,
            studioKey: Math.random(),
        };
        this.vm.loadViews(params, options).then((fieldsViews) => {
            self.fieldsViews = fieldsViews;
            self.renderMenuView();
            self.switchView();
            self.bindStyle();
            self.bindAction();
        });
        // this.action_manager.loadState(state).then(function (action) {
        //     self.action = action;
        //     self.action.context = {...action.context, from_odo_studio: Math.random()}
        //     self.view_service.loadViews(action).then((fieldsViews) => {
        //         self.fieldsViews = fieldsViews;
        //         self.renderMenuView();
        //         self.switchView();
        //         self.bindStyle();
        //         self.bindAction();
        //     });
        // });
    },
    renderView: function () {
        const {typeEdit} = this.state, {classes, render} = this.editType[typeEdit];
        this.$el.find('._hEView ._ulView').remove();
        this.$el.removeClass().addClass(`wrapEdit ${classes}`);
        this.renderMenu();
        render();
        this.baseToEdit();
    },
    reload: function () {
        const state = odoo.studio.state;
        this.appState = state;
        // console.log(state);
        // this.viewParent = parent;
        // this.editToBase();
        // const state = odoo.studio.state;
        this.setState({viewType: state.view_type in this.viewsInfo ? state.view_type : "list"});
        // this.basicView = new EditBasicView(this.viewParent, false, {viewType: state.view_type});
        // this.model = new EditViewModel(this.viewParent);
        this.renderElement();
    },
    renderElement: function () {
        this._super();
        this.renderView();
    }
});

export default EditView;
