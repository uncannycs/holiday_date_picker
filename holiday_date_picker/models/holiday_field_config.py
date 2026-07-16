from odoo import models, fields, api, tools

class HolidayFieldConfig(models.Model):
    _name = 'holiday.field.config'
    _description = 'Holiday Restricted Fields'

    model_id = fields.Many2one('ir.model', string="Model", required=True, ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', string="Field", required=True, ondelete='cascade',
                               domain="[('model_id', '=', model_id), ('ttype', 'in', ['date', 'datetime'])]")

    @api.model
    @tools.ormcache()
    def _get_configured_models(self):
        self.env.cr.execute("SELECT m.model FROM holiday_field_config c JOIN ir_model m ON c.model_id = m.id")
        return [r[0] for r in self.env.cr.fetchall()]

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        self.env.registry.clear_cache()
        return res

    def write(self, vals):
        res = super().write(vals)
        self.env.registry.clear_cache()
        return res

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res

    @api.model
    def get_holiday_data(self):
        configured_fields = self.sudo().search([])
        holiday_fields = {}
        for config in configured_fields:
            model_name = config.model_id.model
            field_name = config.field_id.name
            if model_name not in holiday_fields:
                holiday_fields[model_name] = []
            holiday_fields[model_name].append(field_name)

        holidays_records = self.env['holiday.date'].sudo().search([])
        holidays = [record.date.strftime('%Y-%m-%d') for record in holidays_records]

        return {
            'holiday_fields': holiday_fields,
            'holidays': holidays
        }
