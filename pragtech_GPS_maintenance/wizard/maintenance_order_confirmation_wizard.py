from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MaintenanceOrderConfirmationWizard(models.TransientModel):
    _name = 'maintenance.order.confirmation.wizard'
    _description = 'Maintenance Order Confirmation Wizard'

    def action_create_maintenance_record(self):
        active_maintenance_id = self.env.context.get('active_id')
        if active_maintenance_id:
            maintenance = self.env['fleet.vehicle.log.services'].browse(active_maintenance_id)
            if maintenance:
                SaleOrder = self.env['sale.order']
                if maintenance.request_status in ['non_technical_invoiced', 'technical_invoiced']:    
                    order = SaleOrder.create({
                            'partner_id': maintenance.customer_id.id,
                            'commercial_id': maintenance.customer_id.commercial_id,
                            'customer_group_id': maintenance.customer_id.customer_group_id.id,
                            'sales_type': 'maintenance',
                            'source': 'Maintenance',
                            'maintenance_id': maintenance.maintenance_id,
                            'order_line': [(0, 0, {
                                'product_id': maintenance.invoice_item.id,
                                'name': maintenance.invoice_item.name,
                                'product_uom_qty': 1,
                                'product_uom': maintenance.invoice_item.uom_id.id,
                                'price_unit': maintenance.invoice_item.list_price,
                            })]
                        })
                    order.action_confirm()
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'sale.order',
                        'view_mode': 'form',
                        'res_id': order.id,
                        'target': 'current',
                    }
                else:
                    order = SaleOrder.create({
                            'partner_id': maintenance.customer_id.id,
                            'commercial_id': maintenance.customer_id.commercial_id,
                            'customer_group_id': maintenance.customer_id.customer_group_id.id,
                            'sales_type': 'maintenance',
                            'source': 'Maintenance',
                            'maintenance_id': maintenance.maintenance_id,
                            'order_line': [(0, 0, {
                                'product_id': maintenance.new_device_code.id,
                                'name': maintenance.new_device_code.name,
                                'product_uom_qty': 1,
                                'product_uom': maintenance.new_device_code.uom_id.id,
                                'price_unit': maintenance.new_device_code.list_price,
                            })]
                        })
                    order.action_confirm()
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'sale.order',
                        'view_mode': 'form',
                        'res_id': order.id,
                        'target': 'current',
                    }

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
