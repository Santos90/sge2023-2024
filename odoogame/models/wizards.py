# -*- coding: utf-8 -*-

import sys
from odoo import models, fields, api

class constructed_defense_wizard(models.TransientModel):
	_name = 'odoogame.constructed_defense_wizard'
	_description = 'Wizard que ayuda al usuario a crear estructuras defensivas'

	def _get_default_planet(self):
		return self._context.get('planet_context')

	type = fields.Many2one('odoogame.defense_type', string="Tipo de defensa")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")
	planeta = fields.Many2one('odoogame.planet', string='Planeta', default=_get_default_planet, readonly=True)
	cantidad = fields.Integer(string='Unidades', default=0)#, readonly=True)
