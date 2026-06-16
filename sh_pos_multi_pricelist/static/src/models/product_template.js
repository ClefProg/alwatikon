import { patch } from "@web/core/utils/patch";
import { roundPrecision } from "@web/core/utils/numbers";
import { ProductTemplate } from "@point_of_sale/app/models/product_template";

patch(ProductTemplate.prototype, {
    getPrice(pricelist, quantity, price_extra = 0, recurring = false, variant = false) {
        const price = super.getPrice(pricelist, quantity, price_extra, recurring, variant);

        if (!pricelist || !pricelist.currency_id) {
            return price;
        }

        const product = variant || this.product_variant_id;
        const tmplRules = (this.backLink?.("<-product.pricelist.item.product_tmpl_id") || [])
            .filter((rule) => rule.pricelist_id?.id === pricelist?.id && !rule.product_id)
            .sort((a, b) => b.min_quantity - a.min_quantity);
        const productRules = (product?.backLink?.("<-product.pricelist.item.product_id") || [])
            .filter((rule) => rule.pricelist_id?.id === pricelist?.id)
            .sort((a, b) => b.min_quantity - a.min_quantity);

        const tmplRulesSet = new Set(tmplRules.map((rule) => rule.id));
        const productRulesSet = new Set(productRules.map((rule) => rule.id));
        const generalRulesIds = pricelist?.getGeneralRulesIdsByCategories?.(this.parentCategories) || [];
        const rules = this.models?.["product.pricelist.item"]
            ?.readMany?.([...productRulesSet, ...tmplRulesSet, ...generalRulesIds])
            ?.filter((rule) => rule.min_quantity <= quantity) || [];
        const appliedRule = rules.length ? rules[0] : false;

        // Only convert when the selected pricelist is based on another pricelist
        // with a different currency. Other rule types should use core price as-is.
        if (appliedRule?.base === "pricelist" && appliedRule.base_pricelist_id) {
            const baseId = appliedRule.base_pricelist_id?.id || appliedRule.base_pricelist_id;
            const basePricelist = this.models?.["product.pricelist"]?.get?.(baseId);
            const fromCur = basePricelist?.currency_id;
            const toCur = pricelist.currency_id;
            if (fromCur && toCur && fromCur.id !== toCur.id) {
                const fromRate = parseFloat(fromCur.rate);
                const toRate = parseFloat(toCur.rate);
                if (fromRate && toRate) {
                    return roundPrecision(parseFloat(price || 0) * (toRate / fromRate), toCur.rounding || 0.01);
                }
            }
        }

        return price;
    }
});
