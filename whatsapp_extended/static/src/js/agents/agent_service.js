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
        this.AgentListState = undefined;
        this.AgentList = [];
    },
});

patch(MessageModel.prototype, {
    setup() {
        super.setup();
        /** @type {string} */
        this.pinnedAt = undefined;
    },
    update(data) {
        super.update(data);
        const { pinned_at: pinnedAt } = data;
        if (
            this.originThread?.model === "discuss.channel" &&
            (pinnedAt !== undefined || this.isEmpty)
        ) {
            if (pinnedAt && !this.isEmpty) {
                this.originThread.AgentList.add(this);
                this.pinnedAt = pinnedAt;
            } else {
                this.pinnedAt = undefined;
                this.originThread.AgentList.delete(this);
            }
        }
    },
});

export class AgentList {
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



    getPinnedAt(messageId) {
        const pinnedAt = this.store.Message.get(messageId)?.pinnedAt;
        return pinnedAt ? luxon.DateTime.fromISO(new Date(pinnedAt).toISOString()) : null;
    }


    getAgentList(channel) {
        return [...channel.AgentList].sort((a, b) => {
            if (a.pinnedAt === b.pinnedAt) {
                return b.id - a.id;
            }
            return a.pinnedAt < b.pinnedAt ? 1 : -1;
        });
    }


    hasAgentList(channel) {
        return this.getAgentList(channel).length > 0;
    }


    pin(message) {
        const thread = message.originThread;
        this.dialogService.add(MessageConfirmDialog, {
            confirmText: _t("Yeah, pin it!"),
            message: message,
            messageComponent: Message,
            prompt: _t("You sure want this message pinned to %(conversation)s forever and ever?", {
                conversation: thread.prefix + thread.displayName,
            }),
            size: "md",
            title: _t("Pin It"),
            onConfirm: () => this.setPin(message, true),
        });
    }


    setPin(message, pinned) {
        this.ormService.call("discuss.channel", "set_message_pin", [message.originThread.id], {
            message_id: message.id,
            pinned,
        });
    }


    unpin(message) {
        this.dialogService.add(MessageConfirmDialog, {
            confirmColor: "btn-danger",
            confirmText: _t("Yes, remove it please"),
            message: message,
            messageComponent: Message,
            prompt: _t(
                "Well, nothing lasts forever, but are you sure you want to unpin this message?"
            ),
            size: "md",
            title: _t("Unpin Message"),
            onConfirm: () => this.setPin(message, false),
        });
    }
}

export const messageAgentService = {
    dependencies: ["bus_service", "dialog", "mail.store", "orm"],//"rpc"

    start(env, services) {
        const agentList = reactive(new AgentList(env, services));
        return agentList;
    },
};

registry.category("services").add("discuss.AgentListPanel", messageAgentService);
