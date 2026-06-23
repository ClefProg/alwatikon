/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { ask } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { _t } from "@web/core/l10n/translation";

patch(PosStore.prototype, {
    async setup() {
        super.setup(...arguments);
        this.data.connectWebSocket('POS_PRICELIST_UPDATE', this._onPricelistUpdate.bind(this));
    },

    async _onPricelistUpdate(payload) {
        const confirmed = await ask(this.env.services.dialog, {
            title: _t('Prices Updated'),
            body: _t('The product prices have been updated by the backend. Do you want to load the new prices now?'),
            confirmLabel: _t('Reload'),
            cancelLabel: _t('Later'),
        });

        if (confirmed) {
            const pricelistIds = this.models["product.pricelist"].getAll().map(p => p.id);
            if (pricelistIds.length > 0) {
                const productIds = this.models["product.product"].getAll().map(p => p.id);
                const productTmplIds = this.models["product.template"].getAll().map(p => p.id);
                const categIds = this.models["pos.category"].getAll().map(p => p.id);

                const domain = [
                    ["pricelist_id", "in", pricelistIds],
                    "|", ["product_tmpl_id", "=", false], ["product_tmpl_id", "in", productTmplIds],
                    "|", ["product_id", "=", false], ["product_id", "in", productIds],
                    "|", ["categ_id", "=", false], ["categ_id", "in", categIds]
                ];

                const items = await this.env.services.orm.searchRead(
                    "product.pricelist.item",
                    domain,
                    this.data.fields["product.pricelist.item"],
                    { load: false }
                );
                
                if (items) {
                    this.models.loadConnectedData({
                        "product.pricelist.item": items
                    });
                    
                    const order = this.getOpenOrders()[0];
                    if (order && order.pricelist_id) {
                        order.setPricelist(this.models["product.pricelist"].get(order.pricelist_id.id));
                    }
                }
            }
        }
    }
});
