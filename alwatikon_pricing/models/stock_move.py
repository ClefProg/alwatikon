# -*- coding: utf-8 -*-

from odoo import models

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        # We need to capture the existing quantities before _action_done updates them
        # However, _action_done might process multiple moves, so we must be careful.
        # A simpler approach is to get the quantity before calling super, then calculate after.
        
        # Identify incoming moves linked to USD purchase lines
        usd_incoming_moves = self.filtered(
            lambda m: m.location_id.usage == 'supplier' 
                      and m.location_dest_id.usage == 'internal'
                      and hasattr(m, 'purchase_line_id')
                      and m.purchase_line_id
                      and m.purchase_line_id.currency_id.name == 'USD'
        )
        
        # Store existing quantities before validation
        existing_qtys = {}
        for move in usd_incoming_moves:
            if move.product_id.id not in existing_qtys:
                existing_qtys[move.product_id.id] = move.product_id.with_company(move.company_id).qty_available

        res = super()._action_done(cancel_backorder=cancel_backorder)

        # Calculate new average cost for each USD product received
        for move in usd_incoming_moves.filtered(lambda m: m.state == 'done'):
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
                
            # Determine price unit in USD, per base UoM
            pol = move.purchase_line_id
            price_unit_usd = pol.product_uom_id._compute_price(pol.price_unit, product.uom_id)
            
            existing_qty = existing_qtys.get(product.id, 0.0)
            existing_usd_cost = product.current_usd_cost or 0.0
            
            # Calculate new average cost
            total_qty = existing_qty + qty_received
            if total_qty > 0:
                new_usd_cost = ((existing_qty * existing_usd_cost) + (qty_received * price_unit_usd)) / total_qty
            else:
                new_usd_cost = price_unit_usd
                
            product.sudo().current_usd_cost = new_usd_cost
            
            # Update the existing qty for any subsequent moves of the same product in the same transaction
            existing_qtys[product.id] = total_qty

        return res
