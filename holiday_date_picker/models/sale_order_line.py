from odoo import models, fields

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    x_delivery_date = fields.Datetime(string="Delivery Date")