from odoo import models, api, fields
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class Base(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if 'holiday.field.config' not in self.env or self._name not in self.env[
            'holiday.field.config']._get_configured_models():
            return res
        if self.env.context.get('skip_holiday_check'):
            return res

        holiday_config = self.env['holiday.field.config'].sudo().search([('model_id.model', '=', self._name)])
        if not holiday_config:
            return res

        holidays = self.env['holiday.date'].sudo().search([]).mapped('date')
        if not holidays:
            return res

        for config in holiday_config:
            field_name = config.field_id.name
            if field_name in res and res[field_name]:
                val = res[field_name]
                date_obj = self._parse_date(val)
                if not date_obj:
                    continue

                new_date = self._adjust_to_next_working_day(date_obj, holidays)
                if new_date != date_obj:
                    res[field_name] = self._format_date_like(res[field_name], new_date)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        if 'holiday.field.config' not in self.env or self._name not in self.env[
            'holiday.field.config']._get_configured_models():
            return records
        if not self.env.context.get('skip_holiday_check'):
            records.sudo()._check_and_adjust_holidays()
        return records

    def write(self, vals):
        res = super().write(vals)
        if 'holiday.field.config' not in self.env or self._name not in self.env[
            'holiday.field.config']._get_configured_models():
            return res
        if not self.env.context.get('skip_holiday_check'):
            self.sudo()._check_and_adjust_holidays()
        return res

    def _check_and_adjust_holidays(self):
        if not self:
            return

        if 'holiday.field.config' not in self.env or self._name not in self.env[
            'holiday.field.config']._get_configured_models():
            return

        holiday_config = self.env['holiday.field.config'].search([('model_id.model', '=', self._name)])
        if not holiday_config:
            return

        holidays = self.env['holiday.date'].search([]).mapped('date')
        if not holidays:
            return

        field_names = holiday_config.mapped('field_id.name')

        for record in self:
            vals_to_write = {}
            for field_name in field_names:
                if field_name not in record._fields:
                    continue

                val = record[field_name]
                if not val:
                    continue

                date_obj = self._parse_date(val)
                if not date_obj:
                    continue

                new_date = self._adjust_to_next_working_day(date_obj, holidays)
                if new_date != date_obj:
                    _logger.info("DEBUG: Adjusting holiday date in %s (%s) from %s to %s", self._name, field_name,
                                 date_obj, new_date)
                    vals_to_write[field_name] = self._format_date_like(val, new_date)

            if vals_to_write:
                record.with_context(skip_holiday_check=True).write(vals_to_write)

    def _parse_date(self, val):
        if isinstance(val, (fields.Date, fields.Datetime)):
            return val.date() if hasattr(val, 'date') else val
        if isinstance(val, str):
            if len(val) > 10:
                try:
                    return fields.Datetime.to_datetime(val).date()
                except:
                    return None
            try:
                return fields.Date.to_date(val)
            except:
                return None
        if hasattr(val, 'year'):  # date-like
            return val.date() if hasattr(val, 'date') else val
        return None

    def _format_date_like(self, original_val, new_date):
        if isinstance(original_val, str):
            if len(original_val) > 10:
                dt = fields.Datetime.to_datetime(original_val)
                return fields.Datetime.to_string(dt.replace(year=new_date.year, month=new_date.month, day=new_date.day))
            return fields.Date.to_string(new_date)
        if isinstance(original_val, fields.Datetime) or hasattr(original_val, 'hour'):
            return original_val.replace(year=new_date.year, month=new_date.month, day=new_date.day)
        return new_date

    def _adjust_to_next_working_day(self, date_obj, holidays):
        while date_obj in holidays:
            date_obj += timedelta(days=1)
        return date_obj
