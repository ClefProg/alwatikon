/** @odoo-module */

import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
import { patch } from "@web/core/utils/patch";

patch(Navbar.prototype, {
    async closeSession() {
        if (this.pos && this.pos.config.currency_id) {
            this.pos.currency = this.pos.config.currency_id
        }
        super.closeSession()
    }
});
