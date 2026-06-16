import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { roundPrecision } from "@web/core/utils/numbers";

patch(PosOrder.prototype, {
    setup() {
        super.setup(...arguments);
        this.is_pricelist_update = this.is_pricelist_update ?? false;
        this.sh_payment_amount_snapshot = this.sh_payment_amount_snapshot || [];
    },

    setShSelectedPricelist(pricelist) {
        this.sh_selected_pricelist = pricelist;        
    },
    getShSelectedPricelist() {
        return this.sh_selected_pricelist;
    },

    setIsPricelistUpdate(data) {
        this.is_pricelist_update = data
    },

    get currency(){
        return this.pricelist_id?.currency_id || this.config.currency_id
    },

    addPaymentline(payment_method) {
        const payment_line = super.addPaymentline(...arguments);
        return payment_line;
    },

    setPricelist(pricelist) {
        const oldPricelist = this.pricelist_id || this.config.pricelist_id;
        const oldCurrency = oldPricelist?.currency_id || this.config.currency_id;
        const beforePaymentLines = (this.payment_ids || []).map((line) => ({
            cid: line.cid,
            amount: line.amount,
        }));
        
        super.setPricelist(...arguments);
        
        const newPricelist = this.pricelist_id || this.config.pricelist_id;
        const newCurrency = newPricelist?.currency_id || this.config.currency_id;
        
        if (oldCurrency && newCurrency && oldCurrency.id !== newCurrency.id) {
            const oldRate = parseFloat(oldCurrency.rate);
            const newRate = parseFloat(newCurrency.rate);
            if (oldRate && newRate) {
                // Manually set prices (from numpad) are skipped by default setPricelist behavior.
                // We must artificially multiply them when the currency drops or jumps.
                const linesToSkip = this.lines.filter((line) => line.price_type !== "original");
                for (const line of linesToSkip) {
                    const converted = parseFloat(line.price_unit || 0) * (newRate / oldRate);
                    line.setUnitPrice(roundPrecision(converted, newCurrency.rounding || 0.01));
                }

                // Scale payment lines only while editing an in-progress order.
                // Once finalized, preserve exact cashier-entered amounts for receipt.
                if (!this.finalized) {
                    for (const payment_line of this.payment_ids || []) {
                        const convertedAmount = parseFloat(payment_line.amount || 0) * (newRate / oldRate);
                        // Bypassing setAmount slightly to avoid generic state assertion crashes during receipt generation
                        payment_line.amount = convertedAmount;
                    }
                }
            }
        }
    },

    serializeForORM(opts = {}) {
        const data = super.serializeForORM(opts);
        const orderCurrency = this.currency;
        const companyCurrency = this.config.currency_id;
        
        if (orderCurrency && companyCurrency && orderCurrency.id !== companyCurrency.id) {
            const orderRate = parseFloat(orderCurrency.rate);
            const companyRate = parseFloat(companyCurrency.rate);
            
            if (orderRate && companyRate) {
                const ratio = companyRate / orderRate;
                
                if ('amount_tax' in data) data.amount_tax = data.amount_tax * ratio;
                if ('amount_total' in data) data.amount_total = data.amount_total * ratio;
                if ('amount_paid' in data) data.amount_paid = data.amount_paid * ratio;
                if ('amount_return' in data) data.amount_return = data.amount_return * ratio;
                
                if (data.lines) {
                    data.lines = JSON.parse(JSON.stringify(data.lines));
                    for (const command of data.lines) {
                        if (command[2]) {
                            if ('price_unit' in command[2]) command[2].price_unit = command[2].price_unit * ratio;
                            if ('price_subtotal' in command[2]) command[2].price_subtotal = command[2].price_subtotal * ratio;
                            if ('price_subtotal_incl' in command[2]) command[2].price_subtotal_incl = command[2].price_subtotal_incl * ratio;
                        }
                    }
                }
                
                if (data.payment_ids) {
                    data.payment_ids = JSON.parse(JSON.stringify(data.payment_ids));
                    for (const command of data.payment_ids) {
                        if (command[2] && 'amount' in command[2]) {
                            command[2].amount = command[2].amount * ratio;
                        }
                    }
                }
                
                // Force backend to register this as a base-currency order so it perfectly returns USD variables back to the UI
                data.pricelist_id = this.config.pricelist_id?.id; 
            }
        }
        
        // This field exists in Python pos.order model //
        data.sh_currency_id = this.currency ? this.currency.id : false;
        return data;
    },

    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        // These are UI-only properties for table switching state persistence
        json.sh_selected_pricelist_id = this.sh_selected_pricelist ? this.sh_selected_pricelist.id : false;
        json.is_pricelist_update = this.is_pricelist_update;
        json.sh_payment_amount_snapshot = this.sh_payment_amount_snapshot || [];
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        if (json.sh_selected_pricelist_id) {
            this.sh_selected_pricelist = this.models["product.pricelist"].get(json.sh_selected_pricelist_id);
        }
        if (json.is_pricelist_update !== undefined) {
            this.is_pricelist_update = json.is_pricelist_update;
        }
        if (Array.isArray(json.sh_payment_amount_snapshot)) {
            this.sh_payment_amount_snapshot = json.sh_payment_amount_snapshot;
        }
    }
 
})
