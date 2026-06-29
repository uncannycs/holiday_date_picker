from odoo import models, fields

class HolidayDate(models.Model):
    _name = 'holiday.date'
    _description = 'Holiday Dates'

    name = fields.Char(string="Name", required=True)
    date = fields.Date(string="Date", required=True)
