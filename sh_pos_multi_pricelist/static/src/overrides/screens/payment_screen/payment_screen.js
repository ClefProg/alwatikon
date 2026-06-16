import { _t } from "@web/core/l10n/translation";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { UpdateRatePopup } from "../../../apps/popups/update_rate_popup";
import { makeAwaitable } from "@point_of_sale/app/utils/make_awaitable_dialog";
import { useService } from "@web/core/utils/hooks";
import { onWillUnmount} from "@odoo/owl";
import { useState } from "@odoo/owl";


patch(PaymentScreen.prototype, {
    setup() {
        super.setup();
        this.pos = usePos();
        this.dialog = useService("dialog");
        this.state = useState({ is_payment_pricelist: false });

        // Per the module index: Always start the payment screen in the default (company) currency.
        if (this.currentOrder.pricelist_id?.id !== this.pos.config.pricelist_id?.id) {
            this.currentOrder.setPricelist(this.pos.config.pricelist_id);
        }
        // Persist the selected payment currency mode on the order for receipt rendering.
        this.currentOrder.setIsPricelistUpdate(false);

        onWillUnmount(() => {
            // Restore chosen pricelist if they go back to the cart.
            // Do NOT restore it if the order successfully generated a Receipt in the default USD currency
            if (!this.state.is_payment_pricelist && !this.currentOrder.finalized) {
                const shPricelist = this.currentOrder.getShSelectedPricelist();
                if (shPricelist && this.currentOrder.pricelist_id.id !== shPricelist.id) {
                    this.currentOrder.setPricelist(shPricelist);
                }
            }
        });
    },
    changeCheckbox() {
        const nextState = !this.state.is_payment_pricelist;
        if (nextState) {
            this.currentOrder.setPricelist(this.currentOrder.getShSelectedPricelist());
        } else {
            this.currentOrder.setPricelist(this.pos.config.pricelist_id);
        }
        this.state.is_payment_pricelist = nextState;
        this.currentOrder.setIsPricelistUpdate(nextState);
    },
    async updateRate() {
        const cur_rate = await makeAwaitable(this.dialog, UpdateRatePopup, {
            title: _t(" Update Currency Rate "),
        });
        if (cur_rate) {
            this.pos.getOrder().pricelist_id.currency_id.rate = Number.parseFloat(cur_rate);
            this.pos.getOrder().setPricelist(this.pos.getOrder().pricelist_id);
        }

    },
    async validateOrder(isForceValidate) {
        const order = this.currentOrder;
        order.setIsPricelistUpdate(this.state.is_payment_pricelist);
        order.sh_payment_amount_snapshot = (order.payment_ids || []).map((line) => parseFloat(line.amount || 0));
        this.pos.sh_last_payment_snapshot = {
            order_name: order.name,
            currency_id: order.pricelist_id?.currency_id?.id,
            is_pricelist_update: this.state.is_payment_pricelist,
            amounts: [...order.sh_payment_amount_snapshot],
            payment_line_count: (order.payment_ids || []).length,
            captured_at: Date.now(),
        };
        await super.validateOrder(isForceValidate);
    },
});
