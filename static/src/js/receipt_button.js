/** @odoo-module */

import { Component, useState, useRef, onMounted } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

class WhatsAppDialog extends Component {
    static components = { Dialog };
    static template = "pos_whatsapp_receipt_baileys.WhatsAppDialog";
    static props = {
        title: { type: String, optional: true },
        phone: { type: String, optional: true },
        close: Function,
    };

    setup() {
        this.state = useState({ phone: this.props.phone || "" });
        this.phoneInput = useRef("phoneInput");
        onMounted(() => this.phoneInput.el?.focus());
    }

    onConfirm() {
        this.props.close(this.state.phone.trim());
    }

    onCancel() {
        this.props.close(null);
    }
}

patch(ReceiptScreen, {
    setup() {
        super.setup();
        this.dialog = useService("dialog");
        this.orm = useService("orm");
        this.notification = useService("notification");
    },

    async onClickSendWhatsApp() {
        const order = this.currentOrder;
        const partner = order.get_partner();
        const defaultPhone = partner ? (partner.mobile || partner.phone || "") : "";

        const phone = await new Promise((resolve) => {
            this.dialog.add(WhatsAppDialog, {
                title: _t("Kirim Struk via WhatsApp"),
                phone: defaultPhone,
                close: resolve,
            });
        });

        if (!phone) return;

        try {
            const result = await this.orm.call(
                "pos.order",
                "send_whatsapp_receipt",
                [],
                { order_id: order.backendId, phone_number: phone }
            );
            if (result.success) {
                this.notification.add(_t("Struk berhasil dikirim via WhatsApp!"), {
                    type: "success",
                    sticky: false,
                });
            } else {
                this.notification.add(_t("Gagal kirim: ") + result.error, { type: "danger" });
            }
        } catch (e) {
            this.notification.add(_t("Error: ") + e.message, { type: "danger" });
        }
    },
});
