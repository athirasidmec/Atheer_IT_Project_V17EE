from odoo import models, fields, api
from datetime import datetime

class HrPromotion(models.Model):
    _name = 'hr.promotion'
    _description = "HR Promotion"
    _rec_name = 'name'

    name = fields.Char(string="Order Name", required=True, copy=False, readonly=True, default='New')
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    effective_date = fields.Date("Effective Date", default=fields.Date.today)
    current_salary = fields.Monetary("Current Salary", compute="_compute_current_salary")
    promoted_salary = fields.Monetary("Promoted Salary")
    currency_id = fields.Many2one(
        'res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id
    )
    grade = fields.Many2one("hr.payroll.structure.type", "Grade", compute="_compute_current_salary", store=True)
    promoted_grade = fields.Many2one("hr.payroll.structure.type", "Promoted Grade")
    promotion_line_ids = fields.One2many("hr.promotion.line", "promotion_id")
    state = fields.Selection(
        [('draft', 'Draft'),('hr', 'HR'),('confirmed', 'Confirmed'),('cancelled', 'Cancelled')
        ],tring="Status",readonly=True,default='draft')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            current_year = datetime.now().year
            sequence_number = self.env['ir.sequence'].next_by_code('hr.promotion') or '0000'
            vals['name'] = f"HR/PRO/{current_year}/{sequence_number}"
        return super(HrPromotion, self).create(vals)

    def action_submit(self):
        self.write({'state': 'hr'})

    def action_approve(self):
        if self.state == 'hr':
            self.write({'state': 'confirmed'})

    def action_create_invoice(self):
        print("Invoice creation is not done due unavailable field values to be mapped to the invoice line")

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    @api.depends('employee_id')
    def _compute_current_salary(self):
        for rec in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract:
                rec.current_salary = contract.wage
                rec.grade = contract.structure_type_id
            else:
                rec.current_salary = 0.0
                rec.grade = False


class HrPromotionLines(models.Model):
    _name = 'hr.promotion.line'
    _description = "HR Promotion Lines"

    promotion_id = fields.Many2one('hr.promotion', string="Promotion", required=True, ondelete='cascade')

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.company.currency_id.id)

    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Salary Rule',
        domain=[('category_id.name', '=', 'Allowance')],
        required=True,

    )
    current_amount = fields.Monetary(string='Current Amount', compute='_compute_current_amount', store=True)
    new_amount = fields.Monetary(string='New Amount')

    @api.depends('salary_rule_id', 'promotion_id.employee_id')
    def _compute_current_amount(self):
        for line in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', line.promotion_id.employee_id.id), ('state', '=', 'open')], limit=1)
            if contract and line.salary_rule_id:
                line.current_amount = contract.wage * line.salary_rule_id.amount_percentage / 100
            else:
                line.current_amount = 0.0
