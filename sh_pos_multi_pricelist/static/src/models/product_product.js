/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductProduct } from "@point_of_sale/app/models/product_product";

patch(ProductProduct.prototype, {
    getPrice(pricelist, quantity, price_extra = 0, recurring = false, variant = false) {
        const tmpl = this.product_tmpl_id;
        const price = tmpl?.getPrice
            ? tmpl.getPrice(pricelist, quantity, price_extra, recurring, this)
            : (this.lst_price || 0) + (price_extra || 0);

        console.log("[sh_pos_multi_pricelist] product getPrice", {
            product_id: this.id,
            pricelist_id: pricelist?.id,
            pricelist_currency: pricelist?.currency_id?.name,
            qty: quantity,
            base_price: price,
        });

        return price;
    },
});
