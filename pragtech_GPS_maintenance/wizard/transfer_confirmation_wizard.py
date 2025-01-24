from odoo import models, fields, api

class TransferConfirmationWizard(models.TransientModel):
    _name = 'transfer.confirmation.wizard'
    _description = 'Transfer Confirmation Wizard'

    def action_transfer_creation(self):
        active_maintenance_id = self.env.context.get('active_id')
        if active_maintenance_id:
            maintenance = self.env['fleet.vehicle.log.services'].browse(active_maintenance_id)
            if maintenance:
                maintenance.custom_state = 'submitted'
                if maintenance.request_status == 'technical_device_change' or maintenance.request_status == 'technical_sim_change':
                    picking_type = self.env['stock.picking.type'].search([
                        ('code', '=', 'internal'),
                        ('default_location_src_id', '=', maintenance.source_wh.id)
                    ], limit=1)
                    
                    # Create an internal stock picking (transaction)
                    picking = self.env['stock.picking'].create({
                        'picking_type_id': picking_type.id,
                        'location_id': maintenance.source_wh.id,
                        'origin': maintenance.maintenance_id,
                        'location_dest_id': maintenance.destination_wh.id,
                        'move_type': 'direct',
                        'state': 'draft',
                    })
                    
                    # Create the first stock move for the device
                    if maintenance.request_status == 'technical_device_change':
                        device_lot_ids = [(4, maintenance.new_device_imei.id)] if maintenance.new_device_imei else []
                        
                        self.env['stock.move'].create({
                            'name': maintenance.new_device_code.name or 'From Maintenance',
                            'product_id': maintenance.new_device_code.product_variant_id.id,
                            'product_uom': maintenance.new_device_code.product_variant_id.uom_id.id,
                            'product_uom_qty': 1,
                            'picking_id': picking.id,
                            'location_id': maintenance.source_wh.id,
                            'location_dest_id': maintenance.destination_wh.id,
                            'lot_ids': device_lot_ids,
                        })

                    # Create the second stock move for the SIM code
                    if maintenance.request_status == 'technical_sim_change':
                        sim_lot_ids = [(4, maintenance.new_sim_serial_no.id)] if maintenance.new_sim_serial_no else []
                        
                        self.env['stock.move'].create({
                            'name': maintenance.new_sim_code.name or 'From Maintenance',
                            'product_id': maintenance.new_sim_code.product_variant_id.id,
                            'product_uom': maintenance.new_sim_code.product_variant_id.uom_id.id,
                            'product_uom_qty': 1,
                            'picking_id': picking.id,
                            'location_id': maintenance.source_wh.id,
                            'location_dest_id': maintenance.destination_wh.id,
                            'lot_ids': sim_lot_ids,
                        })

                    # Now confirm and assign the picking (processing the moves)
                    picking.action_confirm()
                    picking.button_validate()
                
                return True

    def action_cancel(self):
        """Action to cancel and close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
