/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { session } from "@web/session";
import { DateTimeField } from "@web/views/fields/datetime/datetime_field";
import { DateTimePicker } from "@web/core/datetime/datetime_picker";
import { onMounted, onWillStart, useRef } from "@odoo/owl";
import { rpc } from "@web/core/network/rpc";

// 1. Tag the inputs with their model name and field name when the field is mounted.
patch(DateTimeField.prototype, {
    setup() {
        super.setup(...arguments);
        this.rootRef = useRef("root");

        onMounted(() => {
            const rootEl = this.rootRef.el;
            if (rootEl) {
                const inputs = rootEl.querySelectorAll('input');
                inputs.forEach(input => {
                    input.dataset.resModel = this.props.record?.resModel;
                    input.dataset.fieldName = this.props.name;
                });
            }
        });
    }
});

// 2. Patch DateTimePicker's rendering flow to inject disabled state directly
// into the calculated `this.items` array elements before it draws the HTML.
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
                // Trigger a re-render if needed, though onWillStart should be enough
                this.render();
            }
        } catch (error) {
            console.error("Failed to fetch holiday data:", error);
        }
    },

    onWillRender() {
        super.onWillRender(...arguments);

        const activeInput = document.querySelector(".o_input.text-primary");
        if (!activeInput) return;

        const modelName = activeInput.dataset.resModel;
        const fieldName = activeInput.dataset.fieldName;

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
