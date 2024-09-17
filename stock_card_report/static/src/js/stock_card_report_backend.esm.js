/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class StockCardReportBackend extends Component {
    setup() {
    this.props()
        this.state = useState({
            reportHtml: "",
            isLoading: true,
        });

        this.orm = useService("orm");
        this.actionService = useService("action");
        this.actionManager = this.props.actionManager;

        // Cargar datos cuando el componente se inicia
        onWillStart(async () => {
            await this.loadReport();
        });
    }

    async loadReport() {
        const result = await this.orm.call('report.stock.card.report', "print_report", ["qweb-html"]);
        this.actionService.doAction(result);
    }

    async printReport() {
        const result = await this.orm.call('report.stock.card.report', "print_report", ["qweb-pdf"]);
        this.actionService.doAction(result);
    }

    async exportReport() {
        const result = await this.orm.call('report.stock.card.report', "print_report", ["xlsx"]);
        this.actionService.doAction(result);
    }

    updateControlPanel() {
        const breadcrumbs = this.actionManager.get_breadcrumbs();
        const status = {
            breadcrumbs,
            cp_content: {
                $buttons: this.$buttons,
            },
        };
        this.update_control_panel(status);
    }

    renderReport() {
        if (this.report_widget) {
            this.report_widget.$el.html(this.state.reportHtml);
        }
    }
}

StockCardReportBackend.template = "StockCardReportBackend"

// Registrar el componente en el action_registry
registry.category("actions").add("stock_card_report_backend", StockCardReportBackend);
export default StockCardReportBackend;
