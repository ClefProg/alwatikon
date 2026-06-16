import { _t } from "@web/core/l10n/translation";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/hooks/pos_hook";
import { Dialog } from "@web/core/dialog/dialog";


export class UpdateRatePopup extends Component {
    static template = "sh_pos__multi_pricelist.UpdateRatePopup";
    static components = { Dialog };
    setup() {
        super.setup()
        this.pos = usePos()
        const currency = this.pos.getOrder().pricelist_id.currency_id
        const rate = parseFloat(currency.rate) || 0;
        this.state = useState({ cur_rate: rate });
    }
    getPayload() {
        return this.state.cur_rate;
    }
    close() {
        this.props.close();
    }
    confirm() {
        this.props.getPayload(this.state.cur_rate);
        this.props.close();
    }

}
