/* @odoo-module */

import { Message } from "@mail/core/common/message";
import { MessageConfirmDialog } from "@mail/core/common/message_confirm_dialog";
import { Message as MessageModel } from "@mail/core/common/message_model";
import { Thread } from "@mail/core/common/thread_model";

import { reactive } from "@odoo/owl";

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";

export const OTHER_LONG_TYPING = 60000;

patch(Thread.prototype, {
    setup() {
        super.setup();
        this.templateListState = undefined;
        this.TemplateListState = undefined;
        this.AgentList = [];
        this.TemplateList = [];
    },
});
export class TemplateList {
    busService;
    store;


    constructor(env, services) {
        this.env = env;
        this.busService = services.bus_service;
        this.dialogService = services.dialog;
        this.ormService = services.orm;
//        this.rpcService = services.rpc;
        this.store = services["mail.store"];
    }
}

export const messageTemplateService = {
    dependencies: ["bus_service", "dialog", "mail.store", "orm"],//"rpc"

    start(env, services) {
        const templateList = reactive(new TemplateList(env, services));
        return templateList;
    },
};
registry.category("services").add("discuss.TemplateListPanel", messageTemplateService);
