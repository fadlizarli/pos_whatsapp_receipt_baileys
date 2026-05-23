import requests
import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def send_whatsapp_receipt(self, order_id=None, phone_number=None):
        order = self.sudo().browse(order_id)
        if not order:
            return {'success': False, 'error': 'Order not found'}

        params = self.env['ir.config_parameter'].sudo()
        baileys_url = params.get_param('pos_whatsapp_receipt_baileys.baileys_url')
        api_key = params.get_param('pos_whatsapp_receipt_baileys.baileys_api_key')
        template = params.get_param('pos_whatsapp_receipt_baileys.baileys_message_template')

        if not baileys_url or not api_key:
            return {'success': False, 'error': 'Baileys belum dikonfigurasi (URL dan API Key wajib diisi)'}

        web_base_url = params.get_param('web.base.url')
        long_url = f"{web_base_url}/resit/lihat?access_token={order.access_token}"

        yourls_url = params.get_param('pos_whatsapp_receipt_baileys.yourls_url')
        yourls_signature = params.get_param('pos_whatsapp_receipt_baileys.yourls_signature')
        receipt_url = long_url
        if yourls_url and yourls_signature:
            try:
                r = requests.post(
                    f"{yourls_url.rstrip('/')}/yourls-api.php",
                    data={'signature': yourls_signature, 'action': 'shorturl', 'url': long_url, 'format': 'json'},
                    timeout=5
                )
                data = r.json()
                if data.get('status') == 'success' and data.get('shorturl'):
                    receipt_url = data['shorturl']
            except Exception as e:
                _logger.warning("YOURLS shortening failed: %s", str(e))

        message = template.format(
            total=f"Rp {order.amount_total:,.0f}",
            date=order.date_order.strftime('%d/%m/%Y %H:%M'),
            receipt_url=receipt_url
        )

        phone = phone_number.strip().replace('+', '').replace('-', '').replace(' ', '')
        if phone.startswith('0'):
            phone = '62' + phone[1:]

        try:
            response = requests.post(
                f"{baileys_url.rstrip('/')}/send-message",
                headers={'x-api-key': api_key, 'Content-Type': 'application/json'},
                json={'phone': phone, 'message': message},
                timeout=15
            )
            if response.status_code in (200, 201):
                return {'success': True}
            else:
                result = response.json() if response.content else {}
                error_msg = result.get('error') or f"HTTP {response.status_code}"
                _logger.error("Baileys error: %s", result)
                return {'success': False, 'error': error_msg}
        except Exception as e:
            return {'success': False, 'error': str(e)}
