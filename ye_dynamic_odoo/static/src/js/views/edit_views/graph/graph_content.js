/** @odoo-module alias=ye_dynamic_odoo.GraphViewContent**/

// import {GraphView} from "@web/views/graph/graph_view";
import {ViewContainer} from 'ye_dynamic_odoo.ViewContainer';
import Base from 'ye_dynamic_odoo.BaseEdit';
import {View} from "@web/views/view";

const {mount} = owl;


var GraphViewContent = Base.ContentBase.extend({
    template: 'GraphViewEdit.Content',
    init: function (parent, params) {
        this._super(parent, params);
        this.parent = parent;
    },
    start: function () {
        const {action} = this.props;
        this.action = action;
    },
    bindAction: function () {},
    renderView: async function () {
        var self = this;
        const {context, res_model} = this.action, {rootViewType} = this.props;
        const props = {
            resModel: res_model,
            type: rootViewType,
            context: context,
            display: {
                controlPanel: false,
            }
        }
        const info = {
            Component: View,
            componentProps: props
        }
        const env = odoo.rootStudio.env;
        await mount(ViewContainer, {
            env,
            props: {info: info},
            target: self.$el[0],
            position: "first-child"
        });

        // const GraphView = viewRegistry.get("graph");
        // const graphView = new GraphView(viewInfo, params);
        // const graphController = await graphView.getController(this);
        // await graphController.appendTo(document.createDocumentFragment());
    },
});

export default GraphViewContent;

