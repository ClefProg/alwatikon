# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        # We need to capture the existing quantities before _action_done updates them
        # However, _action_done might process multiple moves, so we must be careful.
        # A simpler approach is to get the quantity before calling super, then calculate after.
        
        # Identify incoming moves linked to purchase lines
        purchase_incoming_moves = self.filtered(
            lambda m: m.location_id.usage == 'supplier' 
                      and m.location_dest_id.usage == 'internal'
                      and hasattr(m, 'purchase_line_id')
                      and m.purchase_line_id
        )
        
        # Store existing quantities before validation
        existing_qtys = {}
        for move in purchase_incoming_moves:
            if move.product_id.id not in existing_qtys:
                existing_qtys[move.product_id.id] = move.product_id.with_company(move.company_id).qty_available

        res = super()._action_done(cancel_backorder=cancel_backorder)

        if not purchase_incoming_moves:
            return res

        usd_currency = self.env.ref('base.USD', raise_if_not_found=False)
        if not usd_currency:
            return res

        # Calculate new average cost for each product received
        for move in purchase_incoming_moves.filtered(lambda m: m.state == 'done'):
            product = move.product_id.with_company(move.company_id)
            
            # Determine received quantity in base UoM
            if hasattr(move, 'quantity'):
                qty_received = move.product_uom._compute_quantity(move.quantity, product.uom_id)
            elif hasattr(move, 'quantity_done'):
                qty_received = move.product_uom._compute_quantity(move.quantity_done, product.uom_id)
            else:
                qty_received = move.product_uom._compute_quantity(move.product_qty, product.uom_id)

            if qty_received <= 0:
                continue
                
            # Determine price unit in purchase currency, per base UoM
            pol = move.purchase_line_id
            price_unit_pol_currency = pol.product_uom_id._compute_price(pol.price_unit, product.uom_id)
            
            # Convert price to USD
            if pol.currency_id != usd_currency:
                date = move.date or fields.Date.context_today(move)
                price_unit_usd = pol.currency_id._convert(
                    price_unit_pol_currency,
                    usd_currency,
                    move.company_id,
                    date
                )
            else:
                price_unit_usd = price_unit_pol_currency
            
            existing_qty = existing_qtys.get(product.id, 0.0)
            existing_usd_cost = product.current_usd_cost or 0.0
            
            # Calculate new average cost
            total_qty = existing_qty + qty_received
            if total_qty > 0:
                new_usd_cost = ((existing_qty * existing_usd_cost) + (qty_received * price_unit_usd)) / total_qty
            else:
                new_usd_cost = price_unit_usd

            product.sudo().current_usd_cost = new_usd_cost
            self.env['usd.cost.log'].sudo().create({
                'product_id': product.id,
                'company_id': move.company_id.id,
                'type': 'purchase',
                'old_cost': existing_usd_cost,
                'new_cost': new_usd_cost,
                'old_qty': existing_qty,
                'new_qty': total_qty,
                'reference': pol.order_id.name,
                'partner_id': pol.order_id.partner_id.id
            })
            # Update the existing qty for any subsequent moves of the same product in the same transaction
            existing_qtys[product.id] = total_qty

        return res
