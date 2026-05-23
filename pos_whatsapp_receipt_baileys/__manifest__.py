{
    'name': 'POS WhatsApp Receipt (Baileys)',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Kirim resit POS via WhatsApp menggunakan Baileys (tanpa Chromium)',
    'depends': ['point_of_sale', 'web'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/receipt_template.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_whatsapp_receipt_baileys/static/src/xml/receipt_button.xml',
            'pos_whatsapp_receipt_baileys/static/src/js/receipt_button.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
