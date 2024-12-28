from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for purchase_order in self:
            if purchase_order.picking_ids:
                for picking in purchase_order.picking_ids:
                    if picking.state != 'cancel':
                        attachments = self.env['ir.attachment'].search([
                            ('res_model', '=', 'purchase.order'),
                            ('res_id', '=', purchase_order.id)
                        ])
                        # Copy each attachment to the delivery order
                        for attachment in attachments:
                            attachment.copy({
                                'res_model': 'stock.picking',
                                'res_id': picking.id,
                            })

        return res


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, vals):
        attachment = super(IrAttachment, self).create(vals)

        if vals.get('res_model') == 'purchase.order' and vals.get('res_id'):
            purchase_order = self.env['purchase.order'].browse(vals['res_id'])

            delivery_pickings = purchase_order.picking_ids.filtered(
                lambda p: p.state != 'cancel'
            )

            for picking in delivery_pickings:
                attachment.copy({
                    'res_model': 'stock.picking',
                    'res_id': picking.id,
                })

        return attachment
