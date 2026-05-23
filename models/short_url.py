import random
import string
from odoo import models, fields

class ShortUrl(models.Model):
    _name = 'pos.short.url'
    _description = 'Short URL'

    code = fields.Char(string='Code', required=True, index=True)
    url = fields.Char(string='Original URL', required=True)

    @staticmethod
    def generate_code():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
