/** @odoo-module **/

import { UserMenu } from "@web/webclient/user_menu/user_menu";
import { routeToUrl } from "@web/core/browser/router_service";
import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { session } from "@web/session";
import { Dialog } from "@web/core/dialog/dialog";
import { _lt } from "@web/core/l10n/translation";

const userMenuRegistry = registry.category("user_menuitems");

patch(UserMenu.prototype, "app_odoo_customize.UserMenu", {
    setup() {
        this._super.apply(this, arguments);
        userMenuRegistry.remove("debug");
        userMenuRegistry.remove("asset_asset");
        userMenuRegistry.remove("leave_debug");
        userMenuRegistry.remove("separator0");


        userMenuRegistry.remove("documentation");
        userMenuRegistry.remove("support");
        userMenuRegistry.remove("odoo_account");
        userMenuRegistry.remove("shortcuts");
        userMenuRegistry.add("debug", debugItem)
            .add("asset_asset", activateAssetsDebugging)
            .add("leave_debug", leaveDebugMode)
            .add("separator0", separator8)
            .add("documentation", documentationItem)
            .add("support", supportItem)
            .add("shortcuts", shortCutsItem)
            .add("odoo_account", odooAccountItem);
    },
    // getElements() {
    //     var ret = this._super.apply(this, arguments);
    //     return ret;
    // },
});

function debugItem(env) {
    console.log("inside debugging item >>>>",window.location.href)
    const url_debug = $.param.querystring(window.location.href, 'debug=1');
    console.log("url_debug >>>>",url_debug)
    return {
        type: "item",
        id: "debug",
        description: env._t("Activate the developer mode"),
        href: url_debug,
        callback: () => {
            browser.open(url_debug, "_self");
        },
        sequence: 5,
    };
}

function activateAssetsDebugging(env) {
    return {
        type: "item",
        description: env._t("Activate Assets Debugging"),
        callback: () => {
            browser.location.search = "?debug=assets";
        },
        sequence: 6,
    };
}

function leaveDebugMode(env) {
    return {
        type: "item",
        description: env._t("Leave the Developer Tools"),
        callback: () => {
            const route = env.services.router.current;
            route.search.debug = "";
            browser.location.href = browser.location.origin + routeToUrl(route);
        },
        sequence: 7,
    };
}

function separator8() {
    return {
        type: "separator",
        sequence: 8,
    };
}
function documentationItem(env) {
    const documentationURL = session.app_documentation_url;
    const app_show_documentation = session.app_show_documentation;
    if (app_show_documentation == 'True'){
        return {
            type: "item",
            id: "documentation",
            description: env._t("Documentation"),
            href: documentationURL,
            callback: () => {
                browser.open(documentationURL, "_blank");
            },
            sequence: 10,
        }
    }
    else {
        return{}
    }
}

function supportItem(env) {
    const url = session.app_support_url;
    const app_show_support = session.app_show_support;
    if (app_show_support == 'True'){
        return {
        type: "item",
        id: "support",
        description: env._t("Support"),
        href: url,
        callback: () => {
            browser.open(url, "_blank");
        },
        sequence: 20,
    };
    }
    else {
        return {}
    }
}

class ShortCutsDialog extends Dialog {}
ShortCutsDialog.bodyTemplate = "web.UserMenu.shortcutsTable";
ShortCutsDialog.title = _lt("Shortcuts");

function shortCutsItem(env) {
    const app_show_shortcuts = session.app_show_shortcuts;
    console.log('app_show_shortcuts',app_show_shortcuts)
    if (app_show_shortcuts == 'True'){
        return {
            type: "item",
            id: "shortcuts",
            hide: env.isSmall,
            description: env._t("Shortcuts"),
            callback: () => {
                env.services.dialog.add(ShortCutsDialog);
            },
            sequence: 30,
        }
    }
    else {
        return {}
    }
}

function odooAccountItem(env) {
    const app_account_title = session.app_account_title;
    const app_account_url = session.app_account_url;
    const app_show_account = session.app_show_account;
    if (app_show_account == 'True'){
        return {
        type: "item",
        id: "account",
        description: env._t(app_account_title),
        href: app_account_url,
        callback: () => {
            browser.open(app_account_url, "_blank");
        },
        sequence: 60,
    };
    }
    else {
        return {}
    }


}
