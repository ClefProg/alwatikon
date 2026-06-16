import { contextualUtilsService } from "@point_of_sale/app/services/contextual_utils_service";
import { patch } from "@web/core/utils/patch";
import { formatCurrency as webFormatCurrency } from "@web/core/currency";

patch(contextualUtilsService, {
    start(env, { pos, localization }) {
        const superRes = super.start(...arguments);
            const formatCurrency = (value, hasSymbol = true) => {
                const currency =
                    pos.sh_receipt_currency ||
                    pos.getOrder()?.pricelist_id?.currency_id ||
                    pos.currency;
                const result = webFormatCurrency(value, currency?.id, {
                    noSymbol: !hasSymbol,
                });
                return result
            };
            env.utils['formatCurrency'] = formatCurrency
            console.log("superRes", superRes);
            
        return superRes;

    }
})
