/** @odoo-module alias=ye_dynamic_odoo.PivotViewContent**/

import {PivotView} from "@web/views/pivot/pivot_view";
import Base from 'ye_dynamic_odoo.BaseEdit';
import {ViewContainer} from 'ye_dynamic_odoo.ViewContainer';
import {View} from "@web/views/view";

const {mount} = owl;


var PivotEditContent = Base.ContentBase.extend({
    template: 'PivotViewEdit.Content',
    init: function (parent, params) {
        this._super(parent, params);
        this.parent = parent;
    },
    start: function () {
        const {action} = this.props;
        this.action = action;
    },
    bindAction: function () {
    },
    renderView: async function () {
        let self = this;
        const {context, res_model} = this.action, {rootViewType} = this.props;
        const props = {
            resModel: res_model,
            type: rootViewType,
            context: context,
            display: {
                controlPanel: false,
            }
        }
        // const info = {
        //     Component: View,
        //     componentProps: props
        // }
        // const env = odoo.rootStudio.env;
        // await mount(ViewContainer, {
        //     env,
        //     props: {info: info},
        //     target: self.$el[0],
        //     position: "first-child"
        // });

        // const info = {
        //     Component: View,
        //     componentProps: props
        // }
        const env = odoo.rootStudio.env;
        await mount(View, {
            env,
            props: props,
            target: self.$el[0],
            position: "first-child"
        });
    },
});

export default PivotEditContent;

// });
