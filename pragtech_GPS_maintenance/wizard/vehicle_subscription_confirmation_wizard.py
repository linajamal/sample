from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class VehicleSubscriptionConfirmationWizard(models.TransientModel):
    _name = 'vehicle.subscription.confirmation.wizard'
    _description = 'Vehicle Subscription Confirmation Wizard'

    def action_update_vehicle_subscription(self):
        active_subscription_id = self.env.context.get('active_id')
        if active_subscription_id:
            subscription = self.env['sale.subscription'].browse(active_subscription_id)
            if subscription:
                if not any(line.is_create_so for line in subscription.line_ids):
                    raise ValidationError("There is no Vehicle selected to create a Subscription.")
                
                if not subscription.is_single_so:
                    expiration_dates = set(line.subscription_expiration_date for line in subscription.line_ids if line.is_create_so)
                    
                    if len(expiration_dates) > 1:
                        raise ValidationError("The selected lines have different subscription expiration dates. Please ensure all selected lines have the same expiration date.")
    
                line_without_plan = next((line for line in subscription.line_ids if line.is_create_so and not line.new_subscription_plan), None)

                if line_without_plan:
                    raise ValidationError(f"Line no:{line_without_plan.s_no} does not have a New Subscription to update.")
                
                line_count = sum(1 for line in subscription.line_ids if line.is_create_so and line.new_subscription_plan)
                vehicle_ids = [line.vehicle_id.id for line in subscription.line_ids if line.is_create_so and line.vehicle_id]
                SaleOrder = self.env['sale.order']
                if subscription.is_single_so:
                    days = subscription.max_subscription_plan.payment_term_id.line_ids and subscription.max_subscription_plan.payment_term_id.line_ids[0].nb_days or 0
                    order = SaleOrder.create({
                        'partner_id': subscription.customer_id.id,
                        'commercial_id': subscription.customer_id.commercial_id,
                        'customer_group_id': subscription.customer_id.customer_group_id.id,
                        'sales_type': 'subscription',
                        'source': subscription.subscription_id,
                        'vehicle_expiration_date': subscription.vehicle_expiration_date,
                        'subscription_expiration_date': subscription.vehicle_expiration_date + timedelta(days=days),
                        'last_subscription_plan': subscription.max_subscription_plan.id,
                        'vehicle_ids': [(6, 0, vehicle_ids)],
                        'payment_term_id': subscription.max_subscription_plan.payment_term_id.id,
                        'order_line': [(0, 0, {
                            'product_id': subscription.max_subscription_plan.id,
                            'name': subscription.max_subscription_plan.name,
                            'product_uom_qty': line_count,
                            'price_unit': subscription.max_subscription_plan.list_price,
                        })]
                    })
                    order.action_confirm()
                else:
                    expiration_dates = subscription.line_ids.mapped('subscription_expiration_date')
                    filtered_dates = [date for date in expiration_dates if date]
                    max_expiration_date = max(filtered_dates) if filtered_dates else None
                    plan_groups = {}
                    for line in subscription.line_ids:
                        if line.is_create_so:
                            plan_key = line.new_subscription_plan.id
                            if plan_key not in plan_groups:
                                plan_groups[plan_key] = {
                                    'lines': [],
                                    'total_qty': 0,
                                    # 'max_expiration_date': line.subscription_expiration_date,
                                }
                            plan_groups[plan_key]['lines'].append(line)
                            plan_groups[plan_key]['total_qty'] += 1
                            # Update max expiration date
                            # if line.subscription_expiration_date > plan_groups[plan_key]['max_expiration_date']:
                                # plan_groups[plan_key]['max_expiration_date'] = line.subscription_expiration_date

                    # Create SOs for each group
                    for plan_id, group_data in plan_groups.items():
                        first_line = group_data['lines'][0]
                        days = first_line.new_subscription_plan.payment_term_id.line_ids and first_line.new_subscription_plan.payment_term_id.line_ids[0].nb_days or 0
                        if first_line.new_subscription_plan.default_code == 'GNRLSUB':
                                order = SaleOrder.create({
                                'partner_id': subscription.customer_id.id,
                                'commercial_id': subscription.customer_id.commercial_id,
                                'customer_group_id': subscription.customer_id.customer_group_id.id,
                                'sales_type': 'subscription',
                                'source': subscription.subscription_id,
                                'vehicle_expiration_date': max_expiration_date,
                                'subscription_expiration_date': max_expiration_date,
                                'last_subscription_plan': first_line.new_subscription_plan.id,
                                'vehicle_ids': [(6, 0, [first_line.vehicle_id.id])],
                                'payment_term_id': first_line.new_subscription_plan.payment_term_id.id,
                                'GNRLSUB': True,
                                'order_line': [(0, 0, {
                                    'product_id': first_line.new_subscription_plan.id,
                                    'name': first_line.new_subscription_plan.name,
                                    'product_uom_qty': group_data['total_qty'],
                                    'price_unit': first_line.new_subscription_plan.list_price,
                                })]
                            })
                        else:
                            same_date = all(line.subscription_expiration_date == max_expiration_date for line in subscription.line_ids)
                            same_plan = all(line.new_subscription_plan.id == first_line.new_subscription_plan.id for line in subscription.line_ids)
                            if same_date and same_plan:
                                vehicle_ids_data = [(6, 0, vehicle_ids)]
                            else:
                                vehicle_ids_data = [(6, 0, [first_line.vehicle_id.id])]
                            order = SaleOrder.create({
                                'partner_id': subscription.customer_id.id,
                                'commercial_id': subscription.customer_id.commercial_id,
                                'customer_group_id': subscription.customer_id.customer_group_id.id,
                                'sales_type': 'subscription',
                                'source': subscription.subscription_id,
                                # 'vehicle_expiration_date': group_data['max_expiration_date'],
                                'vehicle_expiration_date': max_expiration_date,
                                'subscription_expiration_date': max_expiration_date + timedelta(days=days),
                                'last_subscription_plan': first_line.new_subscription_plan.id,
                                'vehicle_ids': vehicle_ids_data,
                                'payment_term_id': first_line.new_subscription_plan.payment_term_id.id,
                                'order_line': [(0, 0, {
                                    'product_id': first_line.new_subscription_plan.id,
                                    'name': first_line.new_subscription_plan.name,
                                    'product_uom_qty': group_data['total_qty'],
                                    'price_unit': first_line.new_subscription_plan.list_price,
                                })]
                            })
                        order.action_confirm()
                subscription.line_ids.write({'state': 'submitted'})
                subscription.state = 'submitted'
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
