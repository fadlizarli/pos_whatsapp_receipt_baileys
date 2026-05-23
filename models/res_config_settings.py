from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    openwa_base_url = fields.Char(
        string='OpenWA Base URL',
        help='URL server OpenWA, contoh: http://localhost:2785',
        config_parameter='pos_whatsapp_receipt.openwa_base_url'
    )
    openwa_api_key = fields.Char(
        string='OpenWA API Key',
        help='API key dari OpenWA (buat di menu Auth > API Keys)',
        config_parameter='pos_whatsapp_receipt.openwa_api_key'
    )
    openwa_session_id = fields.Char(
        string='Session ID',
        help='UUID sesi WhatsApp di OpenWA',
        config_parameter='pos_whatsapp_receipt.openwa_session_id',
        default='default'
    )
    openwa_message_template = fields.Char(
        string='Template Pesan WhatsApp',
        help='Gunakan {total}, {date}, {receipt_url} sebagai variabel',
        config_parameter='pos_whatsapp_receipt.openwa_message_template',
        default="""Terima kasih telah berbelanja!

Total: {total}
Tanggal: {date}

Lihat resit lengkap:
{receipt_url}"""
    )
    yourls_url = fields.Char(
        string='YOURLS URL',
        help='URL server YOURLS, contoh: https://s.domain.com',
        config_parameter='pos_whatsapp_receipt.yourls_url'
    )
    yourls_signature = fields.Char(
        string='YOURLS Signature Token',
        help='Signature token dari YOURLS (Tools > Secure passwordless API call)',
        config_parameter='pos_whatsapp_receipt.yourls_signature'
    )
