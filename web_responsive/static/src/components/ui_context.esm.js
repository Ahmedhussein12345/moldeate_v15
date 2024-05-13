/** @odoo-module **/
/* Copyright 2021 ITerra - Sergey Shebanin
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

import {registry} from "@web/core/registry";
import {debounce} from "@web/core/utils/timing";
import config from "web.config";
import core from "web.core";
import { WebClient } from "@web/webclient/webclient";
import {patch} from "@web/core/utils/patch";

const {Context} = owl;

patch(WebClient.prototype, "Customize Title", {
    setup() {
        const title = 'BTQ HR';
        this._super();
        this.title.setParts({ zopenerp: title });
    }
});

// Legacy variant
// TODO: remove when legacy code will dropped from odoo
// TODO: then move context definition inside service start function
export const deviceContext = new Context({
    isSmall: config.device.isMobile,
    size: config.device.size_class,
    SIZES: config.device.SIZES,
});

// New wowl variant
// TODO: use default odoo device context when it will be realized
const uiContextService = {
    dependencies: ["ui"],
    start(env, {ui}) {
        window.addEventListener(
            "resize",
            debounce(() => {
                const state = deviceContext.state;
                if (state.size !== ui.size) {
                    state.size = ui.size;
                }
                if (state.isSmall !== ui.isSmall) {
                    state.isSmall = ui.isSmall;
                    config.device.isMobile = state.isSmall;
                    config.device.size_class = state.size;
                    core.bus.trigger("UI_CONTEXT:IS_SMALL_CHANGED");
                }
            }, 150) // UIService debounce for this event is 100
        );

        return deviceContext;
    },
};

registry.category("services").add("ui_context", uiContextService);
