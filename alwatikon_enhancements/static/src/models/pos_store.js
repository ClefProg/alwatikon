import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/services/pos_store";

patch(PosStore.prototype, {
    async setup() {
        this.sh_pre_sync_order_state = new Map();
        await super.setup(...arguments);
    },
});
