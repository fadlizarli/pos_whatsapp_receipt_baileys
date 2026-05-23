import requests
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class PosWhatsAppReceiptBaileys(http.Controller):

    @http.route('/pos/send_whatsapp_receipt', type='json', auth='user')
    def send_whatsapp_receipt(self, order_id=None, phone_number=None, **kwargs):
        order = request.env['pos.order'].sudo().browse(order_id)
        if not order:
            return {'success': False, 'error': 'Order not found'}

        params = request.env['ir.config_parameter'].sudo()
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

    @http.route('/resit/lihat', type='http', auth='public')
    def view_receipt(self, access_token=None, **kwargs):
        if not access_token:
            return request.not_found()

        order = request.env['pos.order'].sudo().search([
            ('access_token', '=', access_token)
        ], limit=1)

        if not order:
            return request.not_found()

        items_html = ''
        for line in order.lines:
            items_html += f'''
            <div class="item-row">
                <span class="item-name">{line.product_id.name}</span>
                <span class="item-qty">x{int(line.qty)}</span>
                <span class="item-price">Rp {line.price_subtotal_incl:,.0f}</span>
            </div>'''

        payment_html = ''
        for payment in order.payment_ids:
            payment_html += f'''
            <div class="info-row">
                <span class="label">{payment.payment_method_id.name}</span>
                <span class="value">Rp {payment.amount:,.0f}</span>
            </div>'''

        change = order.amount_return
        change_html = f'''
        <div class="info-row" style="color:#e74c3c;">
            <span class="label">Kembalian</span>
            <span class="value" style="color:#e74c3c;">Rp {change:,.0f}</span>
        </div>''' if change > 0 else ''

        company = order.company_id
        logo_html = ''
        if company.logo:
            logo_b64 = company.logo.decode('utf-8') if isinstance(company.logo, bytes) else company.logo
            logo_html = f'<img src="data:image/png;base64,{logo_b64}" style="max-height:60px; margin-bottom:8px;"/>'

        phone_html = f'<p>{company.phone}</p>' if company.phone else ''
        email_html = f'<p>{company.email}</p>' if company.email else ''

        html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Struk Pembayaran</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: Arial, sans-serif; background: #f0f0f0; padding: 16px; }}
        .receipt {{ max-width: 480px; width: 100%; margin: 0 auto; background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px dashed #ddd; padding-bottom: 16px; margin-bottom: 16px; }}
        .header h2 {{ font-size: 20px; color: #222; margin-bottom: 4px; }}
        .header p {{ font-size: 13px; color: #888; margin-top: 2px; }}
        .info-row {{ display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 15px; }}
        .label {{ color: #888; }}
        .value {{ font-weight: bold; color: #333; text-align: right; }}
        .items {{ border-top: 1px dashed #ddd; border-bottom: 1px dashed #ddd; padding: 14px 0; margin: 16px 0; }}
        .item-row {{ display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 8px; gap: 8px; }}
        .item-name {{ flex: 1; color: #333; }}
        .item-qty {{ color: #888; white-space: nowrap; }}
        .item-price {{ font-weight: bold; white-space: nowrap; }}
        .total-row {{ display: flex; justify-content: space-between; font-size: 18px; font-weight: bold; color: #222; padding: 12px 0; border-top: 2px solid #222; border-bottom: 1px dashed #ddd; margin-bottom: 12px; }}
        .payment-section {{ margin-bottom: 12px; }}
        .tax-row {{ display: flex; justify-content: space-between; font-size: 13px; color: #aaa; margin-bottom: 4px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #aaa; font-size: 12px; border-top: 1px dashed #ddd; padding-top: 12px; }}
    </style>
</head>
<body>
    <div class="receipt">
        <div class="header">
            {logo_html}
            <h2>{company.name}</h2>
            {phone_html}
            {email_html}
        </div>
        <div class="info-row">
            <span class="label">No. Order</span>
            <span class="value">{order.name}</span>
        </div>
        <div class="info-row">
            <span class="label">Kasir</span>
            <span class="value">{order.user_id.name}</span>
        </div>
        <div class="info-row">
            <span class="label">Tanggal</span>
            <span class="value">{order.date_order.strftime('%d/%m/%Y %H:%M')}</span>
        </div>
        <div class="items">{items_html}</div>
        <div class="total-row">
            <span>Total</span>
            <span>Rp {order.amount_total:,.0f}</span>
        </div>
        <div class="payment-section">
            {payment_html}
            {change_html}
        </div>
        <div class="tax-row">
            <span>Pajak (0%)</span>
            <span>Rp {order.amount_tax:,.0f}</span>
        </div>
        <div class="footer">
            <p>Terima kasih atas kunjungan Anda!</p>
            <p style="margin-top:4px;">{order.date_order.strftime('%d/%m/%Y %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>'''

        return Response(html, content_type='text/html;charset=utf-8')
