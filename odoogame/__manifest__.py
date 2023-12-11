# -*- coding: utf-8 -*-
{
    'name': "odoogame",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'controllers/cron.xml',

        'views/building_type.xml',
        'views/defense_type.xml',
        'views/starship_type.xml',
        'views/planet.xml',
        'views/constructed_building.xml',
        'views/constructed_starship.xml',
        'views/constructed_defense.xml',
        'views/player.xml',
        'views/battle.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/hangar_tail_defense.xml',
        'views/hangar_tail_starship.xml',
        'views/flota.xml',

        'data/data_building_type.xml',
        'data/data_starship_type.xml',
        'data/data_defense_type.xml',
        'data/planets_img_data.xml'

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',



    ],
}
