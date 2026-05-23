from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    baileys_url = fields.Char(
        string='Baileys Server URL',
        help='URL server Baileys, contoh: http://localhost:3000',
        config_parameter='pos_whatsapp_receipt_baileys.baileys_url'
    )
    baileys_api_key = fields.Char(
        string='Baileys API Key',
        help='API key yang dikonfigurasi di Baileys server (.env)',
        config_parameter='pos_whatsapp_receipt_baileys.baileys_api_key'
    )
    baileys_message_template = fields.Char(
        string='Template Pesan WhatsApp',
        help='Gunakan {total}, {date}, {receipt_url} sebagai variabel',
        config_parameter='pos_whatsapp_receipt_baileys.baileys_message_template',
        default="""Terima kasih telah berbelanja!

Total: {total}
Tanggal: {date}

Lihat resit lengkap:
{receipt_url}"""
    )
    yourls_url = fields.Char(
        string='YOURLS URL',
        help='URL server YOURLS, contoh: https://s.domain.com',
        config_parameter='pos_whatsapp_receipt_baileys.yourls_url'
    )
    yourls_signature = fields.Char(
        string='YOURLS Signature Token',
        help='Signature token dari YOURLS (Tools > Secure passwordless API call)',
        config_parameter='pos_whatsapp_receipt_baileys.yourls_signature'
    )
