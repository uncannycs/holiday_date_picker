from odoo import models

class Http(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        result = super().session_info()
        
        # Get all configured fields grouped by model
        configured_fields = self.env['holiday.field.config'].sudo().search([])
        holiday_fields = {}
        for config in configured_fields:
            model_name = config.model_id.model
            field_name = config.field_id.name
            if model_name not in holiday_fields:
                holiday_fields[model_name] = []
            holiday_fields[model_name].append(field_name)

        # Get all holiday dates globally
        holidays_records = self.env['holiday.date'].sudo().search([])
        holidays = [record.date.strftime('%Y-%m-%d') for record in holidays_records]

        result['holiday_fields'] = holiday_fields
        result['holidays'] = holidays
        
        return result
