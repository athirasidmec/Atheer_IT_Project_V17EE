{
    'name': 'Employee Promotion',
    'version': '17.0.0.0',
    "summary": "Employee Promotion Module for implementing a promotion system",
    'category': 'hr',
    'author': 'Athira',
    'website': '',
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/hr_promotion.xml'
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
