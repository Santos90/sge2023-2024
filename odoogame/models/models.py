# -*- coding: utf-8 -*-
# https://github.com/xxjcaxx

import random
from odoo import models, fields, api
import math
import logging

_logger = logging.getLogger(__name__)
from odoo.exceptions import ValidationError


class server(models.Model):
	_name = 'odoogame.server'
	_description = 'Servidor de juego.'

	name = fields.Char(required=True)
	# Rel 0. Un servidor tiene muchos jugadores
	players = fields.One2many('odoogame.player', 'server', "Jugadores")


class player(models.Model):
	_name = 'odoogame.player'
	_description = 'Usuarios del juego.'

	name = fields.Char(required=True)
	#     value = fields.Integer()
	#     value2 = fields.Float(compute="_value_pc", store=True)
	description = fields.Text()
	icon = fields.Image(max_width=300, max_height=300, string='')

	# Rel 0. Un servidor tiene muchos jugadores
	server = fields.Many2one('odoogame.server', string="Servidor", ondelete='restrict')
	# Rel 3. Un jugador ocupa palnetas
	planetas = fields.One2many('odoogame.planet', 'jugador', 'Planetas', delegate=True)

	hierro_total = fields.Integer(string="Hierro", compute='_recuento_recursos')
	cobre_total = fields.Integer(string="Cobre", compute='_recuento_recursos')
	plata_total = fields.Integer(string="Plata", compute='_recuento_recursos')
	oro_total = fields.Integer(string="Oro", compute='_recuento_recursos')
	deuterio_total = fields.Integer(string="Deuterio", compute='_recuento_recursos')
	fosiles_total = fields.Integer(string="Comb. Fósiles", compute='_recuento_recursos')

	# i sempre es recalcula quan executem un action que el mostra

	@api.depends('planetas')  # El decorador @api.depends() indica que es cridarà a la funció
	# sempre que es modifiquen els camps seats i attendee_ids.
	# Si no el posem, es recalcula sols al recarregar el action.
	def _recuento_recursos(self):
		self.hierro_total = 0
		self.cobre_total = 0
		self.plata_total = 0
		self.oro_total = 0
		self.deuterio_total = 0
		self.fosiles_total = 0

		for player in self:
			player.hierro_total = 0
			player.cobre_total = 0
			player.plata_total = 0
			player.oro_total = 0
			player.deuterio_total = 0
			player.fosiles_total = 0

			for planeta in player.planetas:
				player.hierro_total += planeta.hierro
				player.cobre_total += planeta.cobre
				player.plata_total += planeta.plata
				player.oro_total += planeta.oro
				player.deuterio_total += planeta.deuterio
				player.fosiles_total += planeta.fosiles


class galaxy(models.Model):
	_name = 'odoogame.galaxy'
	_description = 'Servidor de juego.'

	name = fields.Char(required=True, default='G001')
	# Rel 1. Una galaxia tiene muchas estrellas
	estrellas = fields.One2many('odoogame.star', 'galaxy', 'Estrellas')


class star(models.Model):
	_name = 'odoogame.star'
	_description = 'Estrella de una galaxia.'

	name = fields.Char(required=True)

	# Rel 1. Una galaxia tiene muchas estrellas
	galaxy = fields.Many2one('odoogame.galaxy', string='Galaxia', delegate=False, ondelete='restrict')
	# Rel 2. Una estrella tiene muchos planetas
	planets = fields.One2many('odoogame.planet', 'star', 'Planetas')


class planet(models.Model):
	_name = 'odoogame.planet'
	_description = 'Planeta que orbita una estrella.'

	name = fields.Char(required=True)
	level = fields.Integer(default=1)
	# Rel 2. Una estrella tiene muchos planetas
	star = fields.Many2one('odoogame.star', string='Estrella', delegate=False, ondelete='restrict')
	# Rel 3. Un jugador ocupa palnetas
	jugador = fields.Many2one('odoogame.player', string='Propietario', delegate=False, ondelete='restrict')
	# Related. En quina galaxia está el planeta
	galaxy = fields.Many2one('odoogame.galaxy', string='Galaxia', related='star.galaxy', store=True, readonly=True)

	# Rel 4
	edificios = fields.One2many('odoogame.constructed_building', 'planeta', string="Edificios construidos")
	naves = fields.One2many('odoogame.constructed_starship', 'ubicacion', string="Naves estacionadas")

	hierro = fields.Integer(string='Hierro')
	cobre = fields.Integer(string='Cobre')
	plata = fields.Integer(string='Plata')
	oro = fields.Integer(string='Oro')
	deuterio = fields.Integer(string='Deuterio')
	fosiles = fields.Integer(string='Comb. fósiles')

	ataques = fields.One2many('odoogame.battle', 'atacante', string='Batallas iniciadas')
	defensas = fields.One2many('odoogame.battle', 'atacante', string='Ataques recibidos')

	def update_level(self):
		for p in self:
			if p.hierro >= 100 and p.cobre >= 50:
				p.hierro -= 100
				p.cobre -= 50
				p.level += 1

	def crear_edificio(self):
		for p in self:
			building_types = self.env['odoogame.building_type'].search([]).ids
			random.shuffle(building_types)
			edificio = p.edificios.create({
				"estado": "1",
				"planeta": p.id,
				"type": building_types[0],
				"vida_actual": self.env['odoogame.building_type'].browse(building_types[0]).vida_inicial
			})

			if p.hierro >= edificio.type.coste_hierro and p.cobre >= edificio.type.coste_cobre and p.plata >= edificio.type.coste_plata and p.oro >= edificio.type.coste_oro:
				p.hierro -= edificio.type.coste_hierro
				p.cobre -= edificio.type.coste_cobre
				p.plata -= edificio.type.coste_plata
				p.oro -= edificio.type.coste_oro

	# Recolecta los recursos que almacenan todos los edificios del planeta
	def recolectar_recursos(self):
		for planeta in self:
			for edificio in planeta.edificios:
				planeta.hierro += edificio.alm_hierro
				planeta.cobre += edificio.alm_cobre
				planeta.plata += edificio.alm_plata
				planeta.oro += edificio.alm_oro
				planeta.deuterio += edificio.alm_deuterio
				planeta.fosiles += edificio.alm_fosiles

				edificio.alm_hierro = 0
				edificio.alm_cobre = 0
				edificio.alm_plata = 0
				edificio.alm_oro = 0
				edificio.alm_deuterio = 0
				edificio.alm_fosiles = 0


class building_type(models.Model):
	_name = 'odoogame.building_type'
	_description = 'Tipos de edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
	name = fields.Char(required=True)
	icon = fields.Image(max_width=300, max_height=300, string='')

	gen_hierro = fields.Integer(string='Producción de hierro')
	gen_cobre = fields.Integer(string='Producción de Cobre')
	gen_plata = fields.Integer(string='Producción de Plata')
	gen_oro = fields.Integer(string='Producción de Oro')
	gen_deuterio = fields.Integer(string='Producción de Deuterio')
	gen_fosiles = fields.Integer(string='Producción de Comb. fósiles')
	gen_energia = fields.Integer(strings='Produccion de W/s')

	vida_inicial = fields.Float(string='Vida inicial edificio',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')
	tipo_energia = fields.Selection([('1', 'Comb. Fósiles'), ('2', 'Electricidad'), ('3', 'Deuterio')])
	energia_funcionamiento = fields.Integer(string='Energia de funcionamiento')

	# Costes de construcción
	coste_hierro = fields.Integer(string='Coste de hierro')
	coste_cobre = fields.Integer(string='Coste de Cobre')
	coste_plata = fields.Integer(string='Coste de Plata')
	coste_oro = fields.Integer(string='Coste de Oro')
	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


class constructed_building(models.Model):
	_name = 'odoogame.constructed_building'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'

	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string='')
	type = fields.Many2one('odoogame.building_type', string="Tipo de edificio")

	vida_inicial = fields.Float(string='Vida inicial edificio',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar',
	                            related='type.vida_inicial')
	tipo_energia = fields.Selection([('1', 'Comb. Fósiles'), ('2', 'Electricidad'), ('3', 'Deuterio')],
	                                related='type.tipo_energia')

	# Rel 4
	planeta = fields.Many2one('odoogame.planet', 'Planeta')

	estado = fields.Selection(
		[('1', 'En construcción'), ('2', 'Activo'), ('3', 'Inactivo'), ('4', 'En reparación'), ('5', 'Destruido')])
	vida_actual = fields.Float(string='Vida actual')

	nivel_produccion = fields.Integer(default=1)
	nivel_almacen = fields.Integer(default=1)

	alm_hierro = fields.Integer(string='Almacén de hierro')
	alm_cobre = fields.Integer(string='Almacén de Cobre')
	alm_plata = fields.Integer(string='Almacén de Plata')
	alm_oro = fields.Integer(string='Almacén de Oro')
	alm_deuterio = fields.Integer(string='Almacén de Deuterio')
	alm_fosiles = fields.Integer(string='Almacén de Comb. fósiles')

	# <------------   Computed segun nivel?  ------------------------->>

	# Máximo almacenamiento
	alm_hierro_max = fields.Integer(string='Almacén de hierro máximo', compute='_calculo_por_nivel_almacen')
	alm_cobre_max = fields.Integer(string='Almacén de Cobre máximo', compute='_calculo_por_nivel_almacen')
	alm_plata_max = fields.Integer(string='Almacén de Plata máximo', compute='_calculo_por_nivel_almacen')
	alm_oro_max = fields.Integer(string='Almacén de Oro máximo', compute='_calculo_por_nivel_almacen')
	alm_deuterio_max = fields.Integer(string='Almacén de Deuterio máximo', compute='_calculo_por_nivel_almacen')
	alm_fosiles_max = fields.Integer(string='Almacén de Comb. fósiles máximo', compute='_calculo_por_nivel_almacen')

	# Generación recursos
	gen_hierro = fields.Integer(string='Producción de hierro', compute='_calculo_por_nivel_produccion')
	gen_cobre = fields.Integer(string='Producción de Cobre', compute='_calculo_por_nivel_produccion')
	gen_plata = fields.Integer(string='Producción de Plata', compute='_calculo_por_nivel_produccion')
	gen_oro = fields.Integer(string='Producción de Oro', compute='_calculo_por_nivel_produccion')
	gen_deuterio = fields.Integer(string='Producción de Deuterio', compute='_calculo_por_nivel_produccion')
	gen_fosiles = fields.Integer(string='Producción de Comb. fósiles', compute='_calculo_por_nivel_produccion')
	gen_energia = fields.Integer(string='Produccion de W/s', compute='_calculo_por_nivel_produccion')
	energia_funcionamiento = fields.Integer(string='Energia de funcionamiento', compute='_calculo_por_nivel_produccion')

	# Costes de construcción
	coste_hierro = fields.Integer(string='Coste de hierro', compute='_calculo_por_nivel_produccion')
	coste_cobre = fields.Integer(string='Coste de Cobre', compute='_calculo_por_nivel_produccion')
	coste_plata = fields.Integer(string='Coste de Plata', compute='_calculo_por_nivel_produccion')
	coste_oro = fields.Integer(string='Coste de Oro', compute='_calculo_por_nivel_produccion')
	tiempo_construccion = fields.Integer(string='Tiempo construcción', compute='_calculo_por_nivel_produccion',
	                                     stored='true')
	tiempo_construccion_restante = fields.Integer(default= 0)
	hierro_vs_hierromax = fields.Char(string='Cantidad', compute='_compute_qty_display')

	@api.depends('alm_hierro', 'alm_hierro_max')
	def _compute_qty_display(self):
		for record in self:
			record.hierro_vs_hierromax = f'{record.alm_hierro}/{record.alm_hierro_max}'

	@api.depends('nivel_produccion')
	def _calculo_por_nivel_produccion(self):
		for e in self:
			e.gen_hierro = e.type.gen_hierro + e.type.gen_hierro * math.log(e.nivel_produccion)
			e.gen_cobre = e.type.gen_cobre + e.type.gen_cobre * math.log(e.nivel_produccion)
			e.gen_plata = e.type.gen_plata + e.type.gen_plata * math.log(e.nivel_produccion)
			e.gen_oro = e.type.gen_oro + e.type.gen_oro * math.log(e.nivel_produccion)
			e.gen_deuterio = e.type.gen_deuterio + e.type.gen_deuterio * math.log(e.nivel_produccion)
			e.gen_fosiles = e.type.gen_deuterio + e.type.gen_fosiles * math.log(e.nivel_produccion)
			e.gen_energia = e.type.gen_energia + e.type.gen_energia * math.log(e.nivel_produccion)

			e.coste_hierro = e.type.coste_hierro + e.type.coste_hierro * math.log(e.nivel_produccion)
			e.coste_cobre = e.type.coste_cobre + e.type.coste_cobre * math.log(e.nivel_produccion)
			e.coste_plata = e.type.coste_plata + e.type.coste_plata * math.log(e.nivel_produccion)
			e.coste_oro = e.type.coste_plata + e.type.coste_oro * math.log(e.nivel_produccion)

			e.tiempo_construccion = e.type.tiempo_construccion + e.type.tiempo_construccion * math.log(e.nivel_produccion)
			e.energia_funcionamiento = e.type.energia_funcionamiento + e.type.energia_funcionamiento * math.log(e.nivel_produccion)

	@api.depends('nivel_almacen')
	def _calculo_por_nivel_almacen(self):
		for e in self:
			e.alm_hierro_max = (e.type.gen_hierro + e.type.gen_hierro * math.log(e.nivel_almacen)) * 1440
			e.alm_cobre_max = (e.type.gen_cobre + e.type.gen_cobre * math.log(e.nivel_almacen)) * 1440
			e.alm_plata_max = (e.type.gen_plata + e.type.gen_plata * math.log(e.nivel_almacen)) * 1440
			e.alm_oro_max = (e.type.gen_oro + e.type.gen_oro * math.log(e.nivel_almacen)) * 1440
			e.alm_deuterio_max = (e.type.gen_deuterio + e.type.gen_deuterio * math.log(e.nivel_almacen)) * 1440
			e.alm_fosiles_max = (e.type.gen_deuterio + e.type.gen_fosiles * math.log(e.nivel_almacen)) * 1440

	def recolectar_recursos(self):

		for edificio in self:
			edificio.planeta.hierro += edificio.alm_hierro
			edificio.planeta.cobre += edificio.alm_cobre
			edificio.planeta.plata += edificio.alm_plata
			edificio.planeta.oro += edificio.alm_oro
			edificio.planeta.deuterio += edificio.alm_deuterio
			edificio.planeta.fosiles += edificio.alm_fosiles

			edificio.alm_hierro = 0
			edificio.alm_cobre = 0
			edificio.alm_plata = 0
			edificio.alm_oro = 0
			edificio.alm_deuterio = 0
			edificio.alm_fosiles = 0

	@api.model
	def cron_update_resources(self):
		for b in self.search([]):
			# Updates
			if b.estado == '1':

				b.tiempo_construccion_restante += 1
				print("resta minutos", b.tiempo_construccion_restante)

				if b.tiempo_construccion_restante == b.tiempo_construccion:
					b.nivel_produccion += 1
					b.estado = '2'
					print("Edificio ${b.id} activo", b.estado)


			# Generación recursos
			elif b.estado == '2':
				if b.alm_hierro < b.alm_hierro_max:
					b.alm_hierro += b.gen_hierro
				if b.alm_cobre < b.alm_cobre_max:
					b.alm_cobre += b.gen_cobre
				if b.alm_plata < b.alm_plata_max:
					b.alm_plata += b.gen_plata
				if b.alm_oro < b.alm_oro_max:
					b.alm_oro += b.gen_oro
				if b.alm_deuterio < b.alm_deuterio_max:
					b.alm_deuterio += b.gen_deuterio
				print('Suma recursos')


class starship_type(models.Model):
	_name = 'odoogame.starship_type'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
	name = fields.Char(required=True)
	icon = fields.Image(max_width=300, max_height=300, string='')

	vida_inicial = fields.Float(string='Vida inicial de la nave',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')
	tipo_energia = fields.Selection([('1', 'Comb. Fósiles'), ('2', 'Deuterio')])
	energia_funcionamiento = fields.Float(string='Energia')

	ataque = fields.Float(string='Ataque de la unidad')
	defensa = fields.Float(string='Defensa de la unidad')

	coste_hierro = fields.Integer(string='Coste de hierro')
	coste_cobre = fields.Integer(string='Coste de Cobre')
	coste_plata = fields.Integer(string='Coste de Plata')
	coste_oro = fields.Integer(string='Coste de Oro')

	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


class constructed_starship(models.Model):
	_name = 'odoogame.constructed_starship'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
	type = fields.Many2one('odoogame.starship_type', string="Tipo de nave")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string='')

	# Rel 4
	player = fields.Many2one('odoogame.player', 'Jugador')
	ubicacion = fields.Many2one('odoogame.planet', 'Planeta')

	estado = fields.Selection([('1', 'En construcción'), ('2', 'Activo'), ('3', 'En reparación'), ('4', 'Destruido')],
	                          default='1', string='Estado')
	vida_actual = fields.Float(string='Vida actual')
	nivel_almacen = fields.Integer(default=1)

	atacando_en_batalla = fields.Many2one('odoogame.battle', string='En ataque')


# tiempo_reparacion = fields.datetime(compute=)

class flota(models.Model):
	_name = 'odoogame.flota'
	_description = 'Flota de un jugador en un planeta'

	planeta = fields.Many2one('odoogame.planet', string='Planeta')
	naves = fields.One2many('odoogame.constructed_starship', 'atacando_en_batalla', string='Naves atacantes')


class battle(models.Model):
	_name = 'odoogame.battle'
	_description = 'Ataque iniciado desde un planeta a otro. Contiene una flota atacante'

	start = fields.Datetime(string='Inicio')
	duration = fields.Integer(default=8, string='Fin (horas)')

	atacante = fields.Many2one('odoogame.planet', string='Atacante')
	defensor = fields.Many2one('odoogame.planet', string='Defensor')

	flotas_atacantes = fields.One2many('odoogame.flota', 'id', string='Flotas atacantes')


"""""
    @api.constraint('atacante', 'defensor')
    def _comprobar_combatientes(self):
        for b in self:
            if b.atacante == b.defensor:
"""""
"""""
ps aux | grep /usr/bin/odoo
ps aux | grep odoo/usr/bin/odoo

"""""
