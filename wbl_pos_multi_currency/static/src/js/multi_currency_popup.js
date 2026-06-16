import { Dialog } from "@web/core/dialog/dialog";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { Component } from "@odoo/owl";

export class MultiCurrencyPopup extends Component {
    static template = "wbl_pos_multi_currency.MultiCurrencyPopupNew";
    static components = { Dialog };
    static props = ["close", "addPaymentLine"];

    setup() {
    this.pos = usePos();
    this.orm = useService("orm");

    this.state = useState({
        currentRate: "",
        enteredAmount: "",
        orderAmount: this.pos.getOrder().priceIncl || 0,
        convertedOrderAmount: "",
        currencies: [],
    });

    this.loadMulticurrency();
}

    async loadMulticurrency() {
        const config_id = this.pos.config.id;
        const multiCurrencyIds = await this.pos.data.call(
            "res.currency",
            "get_config_currencies",
            [config_id]
        );
        this.state.currencies = multiCurrencyIds.map(currency => ({
            code: currency.id,
            name: currency.name,
            symbol: currency.symbol,
            rate: currency.rate || 1,
        }));
    }

    get currencyOptions() {
        try {
            return this.state.currencies.map(currency => ({
                value: currency.code,
                label: currency.name,
            }));
        } catch (error) {
            console.error("Error generating currency options:", error);
            return [];
        }
    }

    onCurrencyChange(event) {
        try {

            const selectedCurrencyCode = event.target.value;
            const selectedCurrency = this.state.currencies.find(
                currency => currency.code === parseInt(selectedCurrencyCode)
            );
            if (selectedCurrency) {
                this.state.currentRate = selectedCurrency.rate;
                this.calculateConvertedOrderAmount();
            } else {
                this.state.currentRate = "";
                this.state.convertedOrderAmount = "";
            }
        } catch (error) {
            console.error("Error during currency change:", error);
        }
    }

    calculateConvertedOrderAmount() {
        try {
            const rate = parseFloat(this.state.currentRate) || 0;
            const orderAmount = parseFloat(this.state.orderAmount) || 0;
            this.state.convertedOrderAmount = (rate * orderAmount).toFixed(2);
        } catch (error) {
            console.error("Error calculating converted order amount:", error);
            this.state.convertedOrderAmount = "";
        }
    }
}
