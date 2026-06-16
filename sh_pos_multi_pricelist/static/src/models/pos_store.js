import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import { roundPrecision } from "@web/core/utils/numbers";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ActionScreen } from "@point_of_sale/app/screens/action_screen";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";

patch(PosStore.prototype, {
    async setup() {
        await super.setup(...arguments);
        this.sh_pre_sync_order_state = new Map();
    },
    convertCurrency(currency, from_currency, amount) {
        const toRate = parseFloat(currency.rate);
        const fromRate = parseFloat(from_currency.rate);
        if (!toRate || !fromRate) {
            return roundPrecision(parseFloat(amount) || 0, this.currency.rounding);
        }
        amount = parseFloat(amount) * (toRate / fromRate);
        return roundPrecision(amount, this.currency.rounding);
    },
    async selectPricelist(pricelist) {
        await super.selectPricelist(...arguments);
        this.getOrder().setShSelectedPricelist(pricelist)
    },


    async onClickBackButton() {
        super.onClickBackButton();
        if (this.mobile_pane == "left" || [PaymentScreen, ActionScreen].includes(this.mainScreen.component))
        {
            this.mobile_pane = this.mainScreen.component === PaymentScreen ? "left" : "right";
            this.is_payment_screen_open = false;
            const condition = (this.config && this.config.pricelist_id && this.getOrder().getShSelectedPricelist() && this.config.pricelist_id.id != this.getOrder().getShSelectedPricelist().id) || ( !this.config.sh_enable_payment_in_pricelist);
            if (condition) {
                this.getOrder().setPricelist(this.getOrder().getShSelectedPricelist() || this.getOrder().pricelist_id)
            }
            this.navigate("ProductScreen");
        }
    },

    async pay(){
        if(!this.config.sh_enable_payment_in_pricelist){
            this.getOrder().setPricelist(this.config.pricelist_id)
        }
        super.pay(...arguments);
    },

    async preSyncAllOrders(orders) {
        await super.preSyncAllOrders(...arguments);
        for (const order of orders || []) {
            this.sh_pre_sync_order_state.set(order.uuid, {
                sh_selected_pricelist_id: order.getShSelectedPricelist?.()?.id || false,
                is_pricelist_update: !!order.is_pricelist_update,
                sh_payment_amount_snapshot: (order.payment_ids || []).map((line) =>
                    parseFloat(line.amount || 0)
                ),
            });
        }
    },

    postSyncAllOrders(orders) {
        super.postSyncAllOrders(...arguments);
        for (const order of orders || []) {
            const state = this.sh_pre_sync_order_state.get(order.uuid);
            if (!state) {
                continue;
            }

            const shPricelist = state.sh_selected_pricelist_id
                ? this.models["product.pricelist"].get(state.sh_selected_pricelist_id)
                : false;

            order.sh_payment_amount_snapshot = state.sh_payment_amount_snapshot || [];
            order.setIsPricelistUpdate?.(state.is_pricelist_update);
            if (shPricelist) {
                order.setShSelectedPricelist?.(shPricelist);
            }

            if (state.is_pricelist_update && shPricelist) {
                order.setPricelist(shPricelist);
                const paymentLines = order.payment_ids || [];
                for (let i = 0; i < paymentLines.length; i++) {
                    if (state.sh_payment_amount_snapshot[i] !== undefined) {
                        paymentLines[i].amount = state.sh_payment_amount_snapshot[i];
                    }
                }
            }

            this.sh_pre_sync_order_state.delete(order.uuid);
        }
    },
})
