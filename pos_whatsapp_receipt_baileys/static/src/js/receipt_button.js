/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";

patch(ReceiptScreen.prototype, {
    setup() {
        super.setup();
        const partner = this.currentOrder.get_partner();
        if (!this.orderUiState.waPhone && partner?.phone) {
            this.orderUiState.waPhone = partner.phone;
        }
    },

    async sendWhatsApp() {
        const phone = this.orderUiState.waPhone;
        if (!phone) {
            this.orderUiState.waSending = false;
            this.orderUiState.waStatus = _t('Masukkan nomor WhatsApp');
            this.orderUiState.waSuccess = false;
            return;
        }

        this.orderUiState.waSending = true;
        this.orderUiState.waStatus = '';

        try {
            const result = await jsonrpc('/pos/send_whatsapp_receipt', {
                order_id: this.currentOrder.server_id,
                phone_number: phone,
            });
            if (result.success) {
                this.orderUiState.waStatus = _t('✓ Resit berhasil dikirim!');
                this.orderUiState.waSuccess = true;
            } else {
                this.orderUiState.waStatus = _t('✗ Gagal: ') + result.error;
                this.orderUiState.waSuccess = false;
            }
        } catch (e) {
            this.orderUiState.waStatus = _t('✗ Terjadi kesalahan');
            this.orderUiState.waSuccess = false;
        } finally {
            this.orderUiState.waSending = false;
        }
    }
});
