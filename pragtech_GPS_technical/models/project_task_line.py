from odoo import models, fields

class ProjectTaskLine(models.Model):
    _name = 'project.task.line'
    _description = 'Task Line for Products'

    task_id = fields.Many2one('project.task', string="Task", ondelete='cascade', readonly=True)
    s_no = fields.Integer(string="S.No.", readonly=True)
    item_code = fields.Char(string="Item Code", readonly=True)
    qty = fields.Float(string="Quantity", readonly=True)
    product_id = fields.Many2one('product.product', string="Product", readonly=True)
