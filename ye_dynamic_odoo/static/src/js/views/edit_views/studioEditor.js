/** @odoo-module ye_dynamic_odoo.StudioEditor**/

import StudioNavBar from "ye_dynamic_odoo.StudioNavBar";
import {useBus, useEffect, useService} from "@web/core/utils/hooks";
import {useTooltip} from "@web/core/tooltip/tooltip_hook";
import {registry} from "@web/core/registry";
import {DebugMenu} from "@web/core/debug/debug_menu";
import {localization} from "@web/core/l10n/localization";
import EditView from "ye_dynamic_odoo.EditView";
import {ComponentAdapter} from "web.OwlCompatibility";
import rootWidget from 'root.widget';
import {browser} from "@web/core/browser/browser";

const {Component} = owl;

export default class StudioEditor extends Component {
    setup() {
        this.actionService = useService("action");
        this.menuService = useService("menu");
        this.title = useService("title");
        this.user = useService("user");
        useService("legacy_service_provider");
    }

    mounted() {
        odoo.studio = {state: $.bbq.getState()};
        const newView = new EditView(rootWidget, {modelName: this.modelName});
        const self = this, superFnc = this.menuService.selectMenu.bind(this.menuService);
        this.menuService.selectMenu = async (menu) => {
            await superFnc(menu);
            const action = self.env.services.action.currentController.action;
            odoo.studio.state = {
                model: action.res_model,
                menu_id: menu.id,
                view_type: action.views[0][1],
                action: action.id
            };
            newView.reload();
        }
        odoo.rootStudio = this;
        newView.renderElement();
        $(this.el).append(newView.$el);
    }
}
StudioEditor.components = {
    StudioNavBar,
};
StudioEditor.template = "studio.StudioEditor";
