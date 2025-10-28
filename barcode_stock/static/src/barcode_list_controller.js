/** @odoo-module **/

import { ListController } from "@web/views/list/list_controller";
import { useBus, useService } from "@web/core/utils/hooks";
import { patch } from "@web/core/utils/patch";

let lastScanTime = 0;
let lastBarcode = "";

patch(ListController.prototype, {
    setup() {
        super.setup();

        // Solo activar en vistas de stock.move.line
        if (this.props.resModel === "stock.move.line") {
            const barcodeService = useService("barcode");
            const orm = useService("orm");

            useBus(barcodeService.bus, "barcode_scanned", async (event) => {
                const { barcode } = event.detail;
                const currentTime = Date.now();

                // Evitar procesamiento duplicado (mismo código en menos de 200ms)
                if (barcode === lastBarcode && (currentTime - lastScanTime) < 200) {
                    return;
                }

                lastBarcode = barcode;
                lastScanTime = currentTime;

                //console.log("Código escaneado en tree:", barcode);

                try {
                    // Obtener todos los IDs de los registros visibles
                    const records = this.model.root.records;
                    if (records && records.length > 0) {
                        // Obtener los IDs de todos los registros
                        const recordIds = records.map(r => r.resId).filter(id => id);

                        if (recordIds.length > 0) {
                            // Llamar al método on_barcode_scanned de stock.move.line
                            // pasando todos los IDs (el método manejará cuál actualizar)
                            await orm.call(
                                "stock.move.line",
                                "process_barcode_from_tree",
                                [recordIds, barcode]
                            );

                            // Recargar la lista para mostrar cambios
                            await this.model.root.load();
                            this.model.notify();

                            //console.log("✓ Código procesado correctamente");
                        }
                    }
                } catch (error) {
                    //console.error("Error procesando código de barras:", error);

                    // Obtener el mensaje de error de UserError de Odoo
                    let errorMessage = "Error procesando código de barras";

                    if (error.data && error.data.message) {
                        // Error de Odoo (UserError, ValidationError, etc.)
                        errorMessage = error.data.message;
                    } else if (error.message) {
                        // Error JavaScript estándar
                        errorMessage = error.message;
                    }

                    // Mostrar notificación de error al usuario
                    const notificationService = this.env.services.notification;
                    if (notificationService) {
                        notificationService.add(errorMessage, {
                            type: "danger",
                            title: "Error de escaneo",
                        });
                    }
                }
            });
        }
    },
});
