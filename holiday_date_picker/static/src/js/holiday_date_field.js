/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { onWillStart } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

// 1. Wrap this.openPicker to set the active field context synchronously
//    before the picker opens. this.openPicker is assigned by useDateTimePicker()
//    inside super.setup(), so wrapping it here is guaranteed to work for ALL
//    fields — including custom x_ fields — regardless of DOM structure.
patch(DateTimeField.prototype, {
    setup() {
        super.setup(...arguments);

        const _originalOpen = this.openPicker.bind(this);
        this.openPicker = (...args) => {
            window._activeDatePickerContext = {
                modelName: this.props.record?.resModel,
                fieldName: this.props.name,
            };
            return _originalOpen(...args);
        };
    }
});

// 2. Patch DateTimePicker to disable holiday dates when the active field is restricted.
patch(DateTimePicker.prototype, {
    setup() {
        super.setup(...arguments);
        this.holidays = session.holidays || [];
        this.holidayFields = session.holiday_fields || {};

        onWillStart(async () => {
            await this.fetchHolidayData();
        });
    },

    async fetchHolidayData() {
        try {
            const data = await rpc("/web/dataset/call_kw/holiday.field.config/get_holiday_data", {
                model: "holiday.field.config",
                method: "get_holiday_data",
                args: [],
                kwargs: {},
            });
            if (data) {
                this.holidays = data.holidays || [];
                this.holidayFields = data.holiday_fields || {};
            }
        } catch (error) {
            console.error("Failed to fetch holiday data:", error);
        }
    },

    onWillRender() {
        super.onWillRender(...arguments);

        const context = window._activeDatePickerContext;
        if (!context) return;

        const { modelName, fieldName } = context;

        // If this field is not restricted, skip
        if (!modelName || !fieldName || !this.holidayFields[modelName] || !this.holidayFields[modelName].includes(fieldName)) {
            return;
        }

        if (this.state.precision === 'days') {
            for (const item of this.items) {
                if (item.weeks) {
                    for (const week of item.weeks) {
                        for (const day of week.days) {
                            if (this.holidays.includes(day.id)) {
                                day.isValid = false;
                                day.extraClass = (day.extraClass || '') + ' bg-light text-muted pe-none text-decoration-line-through text-danger';
                            }
                        }
                    }
                }
            }
        }
    }
});
