import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { onWillUnmount } from "@odoo/owl";

patch(ReceiptScreen.prototype, {
  setup() {
        super.setup();
        this.pos.is_payment_screen_open = false;
        if (this.pos.config.sh_enable_payment_in_pricelist) {
            const shPricelist = this.currentOrder.getShSelectedPricelist?.();
            const targetPricelist = this.currentOrder.is_pricelist_update
                ? shPricelist
                : this.pos.config.pricelist_id;
            if (targetPricelist && this.currentOrder.pricelist_id?.id !== targetPricelist.id) {
                this.currentOrder.setPricelist(targetPricelist);
            }
            this.pos.sh_receipt_currency = targetPricelist?.currency_id || this.currentOrder.pricelist_id?.currency_id;
        } else if (this.currentOrder.getShSelectedPricelist?.()) {
            this.currentOrder.setPricelist(this.currentOrder.getShSelectedPricelist());
            this.pos.sh_receipt_currency = this.currentOrder.pricelist_id?.currency_id;
        }

        // Ensure receipt payment lines keep the exact cashier-entered values
        // captured at validation time (prevents conversion drift on receipt).
        const snapshot =
            this.pos.sh_last_payment_snapshot?.amounts?.length
                ? this.pos.sh_last_payment_snapshot.amounts
                : this.currentOrder.sh_payment_amount_snapshot;
        if (
            this.currentOrder.is_pricelist_update &&
            Array.isArray(snapshot) &&
            snapshot.length
        ) {
            const paymentLines = this.currentOrder.payment_ids || [];
            for (let i = 0; i < paymentLines.length; i++) {
                if (snapshot[i] !== undefined) {
                    paymentLines[i].amount = snapshot[i];
                }
            }
        }
        // Final safety net: if receipt is in pricelist currency but payment lines are
        // still in backend/base scale, normalize them to the visible receipt total.
        if (this.currentOrder.is_pricelist_update) {
            const paymentLines = this.currentOrder.payment_ids || [];
            const paidSum = paymentLines.reduce((sum, line) => sum + (parseFloat(line.amount) || 0), 0);
            const totalDue = parseFloat(this.currentOrder.get_total_with_tax?.() || 0);
            if (paidSum > 0 && totalDue > 0) {
                const ratio = totalDue / paidSum;
                // Apply only when there is a clear scale mismatch.
                if (ratio > 10 || ratio < 0.1) {
                    for (const line of paymentLines) {
                        line.amount = (parseFloat(line.amount) || 0) * ratio;
                    }
                }
            }
        }

        onWillUnmount(() => {
            this.pos.sh_receipt_currency = null;
            this.pos.sh_last_payment_snapshot = null;
        });
    },

})
