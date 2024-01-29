# -*- coding: utf-8 -*-

import sys
from odoo import models, fields, api


import math

from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
import logging


class add_defense_wizard(models.TransientModel):
	_name = 'odoogame.add_defense_wizard'
	_description = 'Wizard que ayuda al usuario a crear estructuras defensivas'

	def _get_default_planet(self):
		return self._context.get('planet_context')


	type = fields.Many2one('odoogame.defense_type', string="Tipo de defensa")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")
	planeta = fields.Many2one('odoogame.planet', string='Planeta', default=_get_default_planet, readonly=True)
	cantidad = fields.Integer(string='Unidades', default=0)  # , readonly=True)

	def create_defenses_wizard(self):
		self.env['odoogame.hangar_tail_defense'].create({
			"defensa": self.env['odoogame.constructed_defense'].create({
				"type": self.type.id
			}).id,
			"planeta": self.planeta.id,
			"cantidad": self.cantidad
		})

class add_battle_wizard(models.TransientModel):
	_name = 'odoogame.add_battle_wizard'
class add_mission_wizard(models.TransientModel):
	_name = 'odoogame.add_mission_wizard'
	_description = 'Wizard que ayuda al usuario a iniciar batallas'

	def _get_default_planet(self):
		return self._context.get('planet_context')

	state = fields.Selection([
		('planets', "Selección de destino"),
		('units', "Selección de naves"),
		('dates', "Selección de fecha"),
	], default='planets')

	jugador = fields.Many2one('res.partner', 'Jugador')

	origen = fields.Many2one('odoogame.planet', string='Origen', domain="[('jugador', '=', jugador)]", default=_get_default_planet)
	destino = fields.Many2one('odoogame.planet', string='Destino')

	fecha_salida = fields.Datetime(string='Inicio', default=lambda self: fields.Datetime.now())
	fecha_llegada = fields.Datetime(string='Llegada', compute='compute_dates')
	fecha_retorno = fields.Datetime(string='Retorno', compute='compute_dates')

	type = fields.Selection([('1', 'Transporte'), ('2', 'Despliegue'), ('3', 'Espiar'),
					 ('4', 'Atacar'), ('5', 'Colonizar'), ('6', 'Mantener posición')],
					default='1', string='Misión')
	flota = fields.Many2many('odoogame.transient_subflota', string='Flota misión')

	def create_mission_wizard(self):
		print(self)

	def action_previous(self):
		if (self.state == 'units'):
			self.state = 'planets'
		elif (self.state == 'dates'):
			self.state = 'units'
		return {
			'type': 'ir.actions.act_window',
			'name': 'Launch battle wizard',
			'res_model': self._name,
			'view_mode': 'form',
			'target': 'new',
			'res_id': self.id,
			'context': self._context
		}

	def action_next(self):
		if (self.state == 'planets'):
			self.state = 'units'
		elif (self.state == 'units'):
			self.state = 'dates'
		return {
			'type': 'ir.actions.act_window',
			'name': 'Launch battle wizard',
			'res_model': self._name,
			'view_mode': 'form',
			'target': 'new',
			'res_id': self.id,
			'context': self._context
		}

	@api.depends('fecha_salida')
	def compute_dates(self):
		for f in self:
			_logger = logging.getLogger('odoogame.mission')
			tiempo_desplazamiento = 3

			salida = fields.Datetime.from_string(f.fecha_salida)
			f.fecha_llegada = fields.Datetime.to_string(salida + timedelta(minutes=tiempo_desplazamiento))
			f.fecha_retorno = fields.Datetime.to_string(salida + timedelta(minutes=tiempo_desplazamiento * 2))


class transient_subflota(models.TransientModel):
	_name = 'odoogame.transient_subflota'
	_description = 'Form para mision'

	cant = fields.Integer(readonly=False)
	disp = fields.Integer(default=0)
	type = fields.Many2one('odoogame.constructed_starship')

