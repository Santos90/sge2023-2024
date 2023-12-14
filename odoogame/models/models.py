# -*- coding: utf-8 -*-
# https://github.com/xxjcaxx

import random
import sys

from odoo import models, fields, api
import math

from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class server(models.Model):
	_name = 'odoogame.server'
	_description = 'Servidor de juego.'

	name = fields.Char(required=True)
	# Rel 0. Un servidor tiene muchos jugadores
	players = fields.One2many('odoogame.player', 'server', "Jugadores", delegate=True)


class player(models.Model):
	_name = 'odoogame.player'
	_description = 'Usuarios del juego.'
	
	name = fields.Char(required=True, size=24)
	# Rel 0. Un servidor tiene muchos jugadores
	server = fields.Many2one('odoogame.server', string="Servidor", ondelete='restrict')
	incorporacion_al_servidor = fields.Date(readonly=True)  # create
	red_social = fields.Html()
	description = fields.Text(string="Descripción")
	icon = fields.Image(max_width=300, max_height=300, string=" ")
	
	# Rel 3. Un jugador ocupa palnetas
	planetas = fields.One2many('odoogame.planet', 'jugador', 'Planetas', delegate=True)
	flotas = fields.One2many('odoogame.flota', 'jugador',  delegate=True)
	misiones = fields.One2many('odoogame.mision', 'jugador',  delegate=True)

	hierro_total = fields.Float(string="Hierro", compute='_recuento_recursos')
	cobre_total = fields.Float(string="Cobre", compute='_recuento_recursos')
	plata_total = fields.Float(string="Plata", compute='_recuento_recursos')
	oro_total = fields.Float(string="Oro", compute='_recuento_recursos')
	deuterio_total = fields.Float(string="Deuterio", compute='_recuento_recursos')
	fosiles_total = fields.Float(string="Comb. Fósiles", compute='_recuento_recursos')
	
	puntos_honor_batalla = fields.Float(string="PH batalla")
	
	
	
	@api.model
	@api.model
	def create(self, values):
		new_player = super(player, self).create(values)
		new_player.generate_planet()
		new_player.incorporacion_al_servidor = datetime.now().date()
		return new_player

	def generate_planet(self):  # descubrir planeta
		for p in self:
			planet_img = self.env['odoogame.planet_img'].search([]).ids
			random.shuffle(planet_img)
			stars = self.env['odoogame.star'].search([]).ids
			random.shuffle(stars)

			planeta = p.planetas.create({
				"name": "Colonia " + str(p.id),
				"icon": self.env['odoogame.planet_img'].browse(planet_img[0]).image,
				"jugador": p.id,
				"star": stars[0]
			})
			
			flota = self.env['odoogame.flota'].create({
				"jugador": planeta.jugador.id,
				'ubi_actual': planeta.id
			})

			tipos_naves = self.env['odoogame.starship_type'].search([])
			for n in tipos_naves:
				print("creando nave: ", n.name)
				nave = flota.naves.create({
					"type": n.id,
					"flota": flota.id
				})

			tipos_defensas = self.env['odoogame.defense_type'].search([])
			for d in tipos_defensas:
				defensa = planeta.defensas.create({
					"type": d.id,
					"planeta": planeta.id,
				})

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
	estrellas = fields.One2many('odoogame.star', 'galaxy', 'Estrellas', delegate=True)


class star(models.Model):
	_name = 'odoogame.star'
	_description = 'Estrella de una galaxia.'

	name = fields.Char(required=True)

	# Rel 1. Una galaxia tiene muchas estrellas
	galaxy = fields.Many2one('odoogame.galaxy', string='Galaxia', delegate=False, ondelete='restrict')
	# Rel 2. Una estrella tiene muchos planetas
	planets = fields.One2many('odoogame.planet', 'star', 'Planetas', delegate=True)


class planet(models.Model):
	_name = 'odoogame.planet'
	_description = 'Planeta que orbita una estrella.'

	name = fields.Char(required=True)
	icon = fields.Image(max_width=300, max_height=300, string=" ")

	# Rel 2. Una estrella tiene muchos planetas
	star = fields.Many2one('odoogame.star', string='Estrella', delegate=False)
	# Rel 3. Un jugador ocupa palnetas
	jugador = fields.Many2one('odoogame.player', string='Propietario', delegate=False)
	# Related. En quina galaxia está el planeta
	galaxy = fields.Many2one('odoogame.galaxy', string='Galaxia', related='star.galaxy', store=True, readonly=True)

	# Rel 4
	edificios = fields.One2many('odoogame.constructed_building', 'planeta', string="Edificios construidos", delegate=True)
	flotas = fields.One2many('odoogame.flota', 'ubi_actual', string="Flotas en órbita", delegate=True )
	naves = fields.Many2many('odoogame.constructed_starship', compute='_get_naves_planeta')

	defensas = fields.One2many('odoogame.constructed_defense', 'planeta', string="Defensas construidas", delegate=True )
	cola_defensas = fields.One2many('odoogame.hangar_tail_defense', 'planeta', string="Defensas en construcción", delegate=True )
	
	hierro = fields.Float(string='Hierro')
	cobre = fields.Float(string='Cobre')
	plata = fields.Float(string='Plata')
	oro = fields.Float(string='Oro')
	deuterio = fields.Float(string='Deuterio')
	fosiles = fields.Float(string='Comb. fósiles')

	def _get_naves_planeta(self):
		for planet in self:
			self.naves = self.env['odoogame.constructed_starship']\
				.search([('flota.ubi_actual.id', '=', planet.id)])

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
	icon = fields.Image(max_width=300, max_height=300, string=" ")

	gen_hierro = fields.Float(string='Producción de hierro')
	gen_cobre = fields.Float(string='Producción de Cobre')
	gen_plata = fields.Float(string='Producción de Plata')
	gen_oro = fields.Float(string='Producción de Oro')
	gen_deuterio = fields.Float(string='Producción de Deuterio')
	gen_fosiles = fields.Float(string='Producción de Comb. fósiles')
	gen_energia = fields.Float(strings='Produccion de W/s')

	vida_inicial = fields.Float(string='Vida inicial edificio',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')
	tipo_energia = fields.Selection([('1', 'Comb. Fósiles'), ('2', 'Electricidad'), ('3', 'Deuterio')])
	energia_funcionamiento = fields.Float(string='Energia de funcionamiento')

	# Costes de construcción
	coste_hierro = fields.Float(string='Coste de hierro')
	coste_cobre = fields.Float(string='Coste de Cobre')
	coste_plata = fields.Float(string='Coste de Plata')
	coste_oro = fields.Float(string='Coste de Oro')
	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


class constructed_building(models.Model):
	_name = 'odoogame.constructed_building'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'

	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")
	type = fields.Many2one('odoogame.building_type', string="Tipo de edificio")

	vida_inicial = fields.Float(string='Vida inicial edificio',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar',
	                            related='type.vida_inicial')
	tipo_energia = fields.Selection(related='type.tipo_energia')

	# Rel 4
	planeta = fields.Many2one('odoogame.planet', 'Planeta')

	estado = fields.Selection([('1', 'En construcción'), ('2', 'Activo'), ('3', 'Inactivo'),
	                           ('4', 'En reparación'), ('5', 'Destruido'),
	                           ('6', 'Nivel de producción'), ('7', 'Nivel de almacén')])
	vida_actual = fields.Float(string='Vida actual')

	nivel_produccion = fields.Integer(default=1)
	nivel_almacen = fields.Integer(default=1)

	alm_hierro = fields.Float(string='Almacén de hierro')
	alm_cobre = fields.Float(string='Almacén de Cobre')
	alm_plata = fields.Float(string='Almacén de Plata')
	alm_oro = fields.Float(string='Almacén de Oro')
	alm_deuterio = fields.Float(string='Almacén de Deuterio')
	alm_fosiles = fields.Float(string='Almacén de Comb. fósiles')

	# <------------   Computed segun nivel?  ------------------------->>

	# Máximo almacenamiento
	alm_hierro_max = fields.Float(string='Almacén de hierro máximo', compute='_calculo_por_nivel_almacen')
	alm_cobre_max = fields.Float(string='Almacén de Cobre máximo', compute='_calculo_por_nivel_almacen')
	alm_plata_max = fields.Float(string='Almacén de Plata máximo', compute='_calculo_por_nivel_almacen')
	alm_oro_max = fields.Float(string='Almacén de Oro máximo', compute='_calculo_por_nivel_almacen')
	alm_deuterio_max = fields.Float(string='Almacén de Deuterio máximo', compute='_calculo_por_nivel_almacen')
	alm_fosiles_max = fields.Float(string='Almacén de Comb. fósiles máximo', compute='_calculo_por_nivel_almacen')

	# Generación recursos
	gen_hierro = fields.Float(string='Gen hierro', compute='_calculo_por_nivel_produccion')
	gen_cobre = fields.Float(string='Gen Cobre', compute='_calculo_por_nivel_produccion')
	gen_plata = fields.Float(string='Gen Plata', compute='_calculo_por_nivel_produccion')
	gen_oro = fields.Float(string='Gen Oro', compute='_calculo_por_nivel_produccion')
	gen_deuterio = fields.Float(string='Gen Deuterio', compute='_calculo_por_nivel_produccion')
	gen_fosiles = fields.Float(string='Gen Comb. fósiles', compute='_calculo_por_nivel_produccion')
	gen_energia = fields.Float(string='Gen W/s', compute='_calculo_por_nivel_produccion')

	energia_funcionamiento = fields.Float(string='Energia de funcionamiento', compute='_calculo_por_nivel_produccion')

	# Costes de construcción
	coste_hierro = fields.Float(string='Coste de hierro', compute='_calculo_por_nivel_produccion')
	coste_cobre = fields.Float(string='Coste de Cobre', compute='_calculo_por_nivel_produccion')
	coste_plata = fields.Float(string='Coste de Plata', compute='_calculo_por_nivel_produccion')
	coste_oro = fields.Float(string='Coste de Oro', compute='_calculo_por_nivel_produccion')

	coste_hierro_alm = fields.Float(string='Coste de hierro', compute='_calculo_por_nivel_almacen')
	coste_cobre_alm = fields.Float(string='Coste de Cobre', compute='_calculo_por_nivel_almacen')
	coste_plata_alm = fields.Float(string='Coste de Plata', compute='_calculo_por_nivel_almacen')
	coste_oro_alm = fields.Float(string='Coste de Oro', compute='_calculo_por_nivel_almacen')

	tiempo_construccion = fields.Integer(related='type.tiempo_construccion')
	time_update_gen = fields.Integer(string='↑ Nivel de producción (min)', compute='_calculo_por_nivel_produccion',
	                                 stored='true')
	time_update_alm = fields.Integer(string='↑ Nivel de almacén (min)', compute='_calculo_por_nivel_almacen',
	                                 stored='true')
	tiempo_transcurrido = fields.Integer(default=0)  # variable que segun el caso, nos servirá para contar el tiempo restante

	hierro_vs_max = fields.Char(string='Hierro', compute='_compute_qty_display')
	cobre_vs_max = fields.Char(string='Cobre', compute='_compute_qty_display')
	plata_vs_max = fields.Char(string='Plata', compute='_compute_qty_display')
	oro_vs_max = fields.Char(string='Oro', compute='_compute_qty_display')
	deuterio_vs_max = fields.Char(string='Deuterio', compute='_compute_qty_display')
	fosiles_vs_max = fields.Char(string='Fósiles', compute='_compute_qty_display')
	tiempo_vs_max = fields.Char(string='Tiempo restante', compute='_compute_qty_display')


	def _pago_recursos(self):
		for f in self:
			f._constrain_recursos_necesarios()
			if f.estado == 1 or f.estado == 6:
				f.planeta.hierro -= f.coste_hierro
				f.planeta.cobre -= f.coste_cobre
				f.planeta.plata -= f.coste_plata
				f.planeta.oro -= f.coste_oro
			elif f.estado == 7:
				f.planeta.hierro -= f.coste_hierro_alm
				f.planeta.cobre -= f.coste_cobre_alm
				f.planeta.plata -= f.coste_plata_alm
				f.planeta.oro -= f.coste_oro_alm

	def create(self, values):
		new_id = super(constructed_building, self).create(values)

		self._pago_recursos

		return new_id
	@api.depends('alm_hierro', 'alm_hierro_max', 'alm_cobre', 'alm_cobre_max', 'alm_plata', 'alm_plata_max', 'alm_oro',
	             'alm_oro_max', 'alm_deuterio', 'alm_deuterio_max', 'alm_fosiles', 'alm_fosiles_max', 'tiempo_transcurrido',
	             'time_update_alm', 'time_update_gen')
	def _compute_qty_display(self):
		for record in self:
			record.hierro_vs_max = f'{record.alm_hierro}/{record.alm_hierro_max}'
			record.cobre_vs_max = f'{record.alm_cobre}/{record.alm_cobre_max}'
			record.plata_vs_max = f'{record.alm_plata}/{record.alm_plata_max}'
			record.oro_vs_max = f'{record.alm_oro}/{record.alm_oro_max}'
			record.deuterio_vs_max = f'{record.alm_deuterio}/{record.alm_deuterio_max}'
			record.fosiles_vs_max = f'{record.alm_fosiles}/{record.alm_fosiles_max}'

			if record.estado == '2': record.tiempo_vs_max = '0/0'
			elif record.estado == '1':
				record.tiempo_vs_max = f'{record.tiempo_transcurrido}/{record.tiempo_construccion} minutos'
			elif record.estado == '6':
				record.tiempo_vs_max = f'{record.tiempo_transcurrido}/{record.time_update_gen} minutos'
			elif record.estado == '7':
				record.tiempo_vs_max = f'{record.tiempo_transcurrido}/{record.time_update_alm} minutos'

			print("Hierro: ", record.hierro_vs_max)
			print("Cobre: ", record.cobre_vs_max)
			print("Plata: ", record.plata_vs_max)
			print("Oro: ", record.oro_vs_max)

	@api.constrains('cantidad')
	def _constrain_recursos_necesarios(self):
		for f in self:
			if f.coste_hierro > f.planeta.hierro:
				raise ValidationError("No tienes suficientes recursos (hierro)")
			if f.coste_cobre > f.planeta.cobre:
				raise ValidationError("No tienes suficientes recursos (cobre)")
			if f.coste_plata > f.planeta.plata:
				raise ValidationError("No tienes suficientes recursos (plata)")
			if f.coste_oro > f.planeta.oro:
				raise ValidationError("No tienes suficientes recursos (oro)")

	@api.depends('nivel_produccion')
	def _calculo_por_nivel_produccion(self):
		for e in self:
			e.gen_hierro = e.type.gen_hierro + e.type.gen_hierro * math.log(e.nivel_produccion)
			e.gen_cobre = e.type.gen_cobre + e.type.gen_cobre * math.log(e.nivel_produccion)
			e.gen_plata = e.type.gen_plata + e.type.gen_plata * math.log(e.nivel_produccion)
			e.gen_oro = e.type.gen_oro + e.type.gen_oro * math.log(e.nivel_produccion)
			e.gen_deuterio = e.type.gen_deuterio + e.type.gen_deuterio * math.log(e.nivel_produccion)
			e.gen_fosiles = e.type.gen_fosiles + e.type.gen_fosiles * math.log(e.nivel_produccion)
			e.gen_energia = e.type.gen_energia + e.type.gen_energia * math.log(e.nivel_produccion)

			e.coste_hierro = e.type.coste_hierro + e.type.coste_hierro * math.log(e.nivel_produccion)
			e.coste_cobre = e.type.coste_cobre + e.type.coste_cobre * math.log(e.nivel_produccion)
			e.coste_plata = e.type.coste_plata + e.type.coste_plata * math.log(e.nivel_produccion)
			e.coste_oro = e.type.coste_oro + e.type.coste_oro * math.log(e.nivel_produccion)

			e.time_update_gen = (e.type.tiempo_construccion
			                     + e.type.tiempo_construccion
			                     * math.log(e.nivel_produccion))
			e.energia_funcionamiento = (e.type.energia_funcionamiento
			                            + e.type.energia_funcionamiento
			                            * math.log(e.nivel_produccion))


	@api.depends('nivel_almacen')
	def _calculo_por_nivel_almacen(self):
		for e in self:
			e.coste_hierro_alm = e.type.coste_hierro + e.type.coste_hierro * math.log(e.nivel_almacen)
			e.coste_cobre_alm = e.type.coste_cobre + e.type.coste_cobre * math.log(e.nivel_almacen)
			e.coste_plata_alm = e.type.coste_plata + e.type.coste_plata * math.log(e.nivel_almacen)
			e.coste_oro_alm = e.type.coste_oro + e.type.coste_oro * math.log(e.nivel_almacen)

			e.alm_hierro_max = (e.type.gen_hierro + e.type.gen_hierro * math.log(e.nivel_almacen)) * 1440
			e.alm_cobre_max = (e.type.gen_cobre + e.type.gen_cobre * math.log(e.nivel_almacen)) * 1440
			e.alm_plata_max = (e.type.gen_plata + e.type.gen_plata * math.log(e.nivel_almacen)) * 1440
			e.alm_oro_max = (e.type.gen_oro + e.type.gen_oro * math.log(e.nivel_almacen)) * 1440
			e.alm_deuterio_max = (e.type.gen_deuterio + e.type.gen_deuterio * math.log(e.nivel_almacen)) * 1440
			e.alm_fosiles_max = (e.type.gen_fosiles + e.type.gen_fosiles * math.log(e.nivel_almacen)) * 1440

			e.time_update_alm = e.type.tiempo_construccion + e.type.tiempo_construccion * math.log(e.nivel_almacen)

	@api.constrains('cantidad')
	def update_gen(self):  # Update generacion de recursos
		for f in self:

			print("Boton update_gen. Estado = ", f.estado)
			if f.estado == '2' or f.estado == '3':
				print("Boton update_gen cambio")
				f._pago_recursos()
				f.estado = '6'

	def update_alm(self):
		for f in self:
			if f.estado == '2' or f.estado == '3' :
				f._pago_recursos()
				f.estado = '7'
	def recolectar_recursos(self):  # Action boton: vacía los almacenes de los edificios y deposita los recursos en el almacén general

		for edificio in self:
			print("Recolectando recursos")
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

	# [('1', 'En construcción'), ('2', 'Activo'), ('3', 'Inactivo'), ('4', 'En reparación'), ('5', 'Destruido'), ('6', '↑ Nivel de producción'), ('7', '↑ Nivel de almacén')])
	@api.model
	def cron_update_resources(self):
		print("cron_update_resources")
		for b in self.search([]):
			# Updates
			if b.estado == '1': #En construccion

				b.tiempo_transcurrido += 1

				if b.tiempo_transcurrido == b.tiempo_construccion:
					b.tiempo_transcurrido = 0
					b.nivel_produccion += 1
					b.estado = '2'

			elif b.estado == '6': # ('6', '↑ Nivel de producción')

				b.tiempo_transcurrido += 1

				if b.tiempo_transcurrido == b.time_update_gen:
					b.tiempo_transcurrido = 0
					b.nivel_produccion += 1
					b.estado = '2'

			elif b.estado == '7':

				b.tiempo_transcurrido += 1

				if b.tiempo_transcurrido == b.time_update_alm:
					b.tiempo_transcurrido = 0
					b.nivel_produccion += 1
					b.estado = '2'

			# Generación recursos
			if b.estado == '2' or b.estado == '6' or b.estado == '7':
				if b.alm_hierro < b.alm_hierro_max:
					b.alm_hierro += b.gen_hierro
				if b.alm_cobre < b.alm_cobre_max:
					b.alm_cobre += b.gen_cobre
				if b.alm_plata < b.alm_plata_max:
					b.alm_plata += b.gen_plata
				if b.alm_oro < b.alm_oro_max:
					b.alm_oro += b.gen_oro
				if b.alm_fosiles < b.alm_fosiles_max:
					b.alm_fosiles += b.gen_fosiles
				if b.alm_deuterio < b.alm_deuterio_max:
					b.alm_deuterio += b.gen_deuterio
					if b.alm_deuterio >= b.alm_deuterio_max:
						b.alm_deuterio = b.alm_deuterio_max


class starship_type(models.Model):
	_name = 'odoogame.starship_type'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
	name = fields.Char(required=True)
	icon = fields.Image(max_width=300, max_height=300, string=" ")

	vida_inicial = fields.Float(string='Vida inicial de la nave',
								help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')
	tipo_energia = fields.Selection([('1', 'Comb. Fósiles'), ('2', 'Deuterio')])
	energia_funcionamiento = fields.Float(string='Energia')

	ataque = fields.Float(string='Ataque de la unidad')
	defensa = fields.Float(string='Defensa de la unidad')
	velocidad = fields.Float(string='Velocidad de la unidad')
	almacen = fields.Float(string='Almacenamiento de la unidad')

	coste_hierro = fields.Float(string='Coste de hierro')
	coste_cobre = fields.Float(string='Coste de Cobre')
	coste_plata = fields.Float(string='Coste de Plata')
	coste_oro = fields.Float(string='Coste de Oro')

	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


class constructed_starship(models.Model):
	_name = 'odoogame.constructed_starship'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'

	name = fields.Char(string='Nombre', compute='set_name')
	type = fields.Many2one('odoogame.starship_type', string="Tipo de nave")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")

	# Rel 4
	jugador = fields.Many2one('odoogame.player', 'Jugador', related='flota.jugador', store=True)
	planeta = fields.Many2one('odoogame.planet', 'Planeta', related='flota.ubi_actual', store=True)
	cantidad = fields.Integer(string='Unidades', default=0, readonly=True)
	flota = fields.Many2one('odoogame.flota', 'Flota', help='Este conjunto de naves forma parte de una flota')


	estado = fields.Selection([('1', 'En construcción'), ('2', 'Activo'), ('3', 'En reparación'), ('4', 'Destruido'),
	                           ('5', 'Subiendo nivel producción'), ('6', 'Subiendo nivel almacén')], default='1', string='Estado')
	vida_actual = fields.Float(string='Vida actual')
	nivel_almacen = fields.Float(default=1)

	@api.depends('type', 'cantidad')
	def set_name(self):
		for f in self:
			f.name = str(f.type.name) + " - " + str(f.cantidad)

class hangar_tail_starship(models.Model):  # Nombre para relaciones: Elemento a contruir
	_name = 'odoogame.hangar_tail_starship'
	_description = 'Cola de contrucción'
	name = fields.Char(string='Nombre', compute='set_name')

	# relacion: Elemento a contruir "es de 1 tipo"...
	nave = fields.Many2one('odoogame.constructed_starship')
	cantidad = fields.Integer(default=0)
	max = fields.Integer(compute='_compute_costes')

	fin = fields.Datetime(string="Fin de la construccion")
	duracion = fields.Integer(string="Tiempo que tardará en completarse", compute="_compute_fechas")
	tiempo_transcurrido = fields.Integer(string="Tiempo transcurrido", default=0)

	# Costes de construcción
	coste_hierro = fields.Float(string='Coste de hierro', compute='_compute_costes')
	coste_cobre = fields.Float(string='Coste de Cobre', compute='_compute_costes')
	coste_plata = fields.Float(string='Coste de Plata', compute='_compute_costes')
	coste_oro = fields.Float(string='Coste de Oro', compute='_compute_costes')

	@api.constrains('cantidad')
	def _constrain_recursos_necesarios(self):
		for f in self:
			if f.coste_hierro > f.nave.planeta.hierro:
				raise ValidationError("No tienes suficientes recursos (hierro)")
			if f.coste_cobre > f.nave.planeta.cobre:
				raise ValidationError("No tienes suficientes recursos (cobre)")
			if f.coste_plata > f.nave.planeta.plata:
				raise ValidationError("No tienes suficientes recursos (plata)")
			if f.coste_oro > f.nave.planeta.oro:
				raise ValidationError("No tienes suficientes recursos (oro)")

	@api.depends('nave', 'cantidad')
	def set_name(self):
		for f in self:
			f.name = str(f.nave.name) + " - " + str(f.cantidad)

	@api.depends('nave', 'cantidad')
	def _compute_fechas(self):
		for f in self:
			f.duracion = f.cantidad * f.nave.type.tiempo_construccion

	@api.depends('cantidad', 'nave', 'nave.flota.ubi_actual.hierro', 'nave.flota.ubi_actual.cobre', 'nave.flota.ubi_actual.plata',
	             'nave.flota.ubi_actual.oro')
	def _compute_costes(self):
		for f in self:
			f.coste_hierro = f.cantidad * f.nave.type.coste_hierro
			f.coste_cobre = f.cantidad * f.nave.type.coste_cobre
			f.coste_plata = f.cantidad * f.nave.type.coste_plata
			f.coste_oro = f.cantidad * f.nave.type.coste_oro

			min = sys.maxsize  # calculamos el máximo de naves de un tipo q se pueden construir según el recurso 'limitante' del planeta
			if f.nave.type.coste_hierro > 0:
				cant = f.nave.flota.ubi_actual.hierro / f.nave.type.coste_hierro

				if cant < min:
					min = cant
			if f.nave.type.coste_cobre > 0:
				cant = f.nave.flota.ubi_actual.cobre / f.nave.type.coste_cobre

				if cant < min:
					min = cant
			if f.nave.type.coste_plata > 0:
				cant = f.nave.flota.ubi_actual.plata / f.nave.type.coste_plata

				if cant < min:
					min = cant
			if f.nave.type.coste_oro > 0:
				cant = f.nave.flota.ubi_actual.oro / f.nave.type.coste_oro

				if cant < min:
					min = cant

			f.max = min

	@api.model
	def cron_update_starship_construction(self):
		planetas = self.env['odoogame.planet'].search([])
		print("Cron cola naus")
		for p in planetas:
			primer_elemento = self.env['odoogame.hangar_tail_defense'].search(
				[('nave.planeta', '=', p.id)]
				, limit=1
			)

			if primer_elemento is not None:
				primer_elemento.tiempo_transcurrido += 1
				primer_elemento.fin = fields.Datetime.to_string(
					fields.Datetime.now() + timedelta(minutes=primer_elemento.duracion))

				if primer_elemento.tiempo_transcurrido >= primer_elemento.duracion:
					primer_elemento.nave.cantidad += primer_elemento.cantidad
					# borrar
					primer_elemento.unlink()

	@api.model  # al crear una instancia del modelo se restan los recursos del planeta. No modificar una vez creada (bug)
	def create(self, values):
		new_id = super(hangar_tail_starship, self).create(values)

		new_id.nave.flota.ubi_actual.hierro -= new_id.coste_hierro
		new_id.nave.flota.ubi_actual.cobre -= new_id.coste_cobre
		new_id.nave.flota.ubi_actual.plata -= new_id.coste_plata
		new_id.nave.flota.ubi_actual.oro -= new_id.coste_oro

		return new_id


# tiempo_reparacion = fields.datetime(compute=)
class defense_type(models.Model):
	_name = 'odoogame.defense_type'
	_description = 'Tipos de estructuras defensivas'

	name = fields.Char(required=True)
	icon = fields.Image(max_width=300, max_height=300, string=" ")

	vida_inicial = fields.Float(string='Vida inicial de la nave',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')

	ataque = fields.Float(string='Ataque de la unidad')
	defensa = fields.Float(string='Defensa de la unidad')

	coste_hierro = fields.Float(string='Coste de hierro')
	coste_cobre = fields.Float(string='Coste de Cobre')
	coste_plata = fields.Float(string='Coste de Plata')
	coste_oro = fields.Float(string='Coste de Oro')

	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


class constructed_defense(models.Model):
	_name = 'odoogame.constructed_defense'
	_description = 'Estructuras defensivas construidas'

	name = fields.Char(string='Nombre', compute='set_name')
	type = fields.Many2one('odoogame.defense_type', string="Tipo de defensa")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")
	jugador = fields.Many2one(related="planeta.jugador", string="jugador")
	# Rel 4

	planeta = fields.Many2one('odoogame.planet', string='Planeta')
	cantidad = fields.Integer(string='Unidades', default=0, readonly=True)

	vida_actual = fields.Float(string='Vida actual')

	@api.depends('type', 'planeta')
	def set_name(self):
		print("Nueva instancia 'constructed_defense'")
		for f in self:
			f.name = str(f.planeta.name) + " - " + str(f.type.name)
			print("Nombre: ", str(f.type.name))


class hangar_tail_defense(models.Model):  # Nombre para relaciones: Elemento a contruir
	_name = 'odoogame.hangar_tail_defense'
	_description = 'Cola de contrucción'
	name = fields.Char(string='Nombre', compute='set_name')

	# relacion: Elemento a contruir "es de 1 tipo"...
	defensa = fields.Many2one('odoogame.constructed_defense', help='Apunta a las defensas de cierto tipo construidas en un determinado planeta')
	planeta = fields.Many2one(related='defensa.planeta')
	cantidad = fields.Integer(default=1)
	max = fields.Integer(compute='_compute_costes')

	fin = fields.Datetime(string="Fin de la construccion")
	duracion = fields.Integer(string="Tiempo que tardará en completarse", compute="_compute_fechas")
	tiempo_transcurrido = fields.Integer(string="Tiempo en construccion", default=0)

	# Costes de construcción
	coste_hierro = fields.Float(string='Coste de hierro', compute='_compute_costes')
	coste_cobre = fields.Float(string='Coste de Cobre', compute='_compute_costes')
	coste_plata = fields.Float(string='Coste de Plata', compute='_compute_costes')
	coste_oro = fields.Float(string='Coste de Oro', compute='_compute_costes')

	@api.constrains('cantidad')
	def _constrain_recursos_necesarios(self):
		for f in self:
			if f.coste_hierro > f.defensa.planeta.hierro:
				raise ValidationError("No tienes suficientes recursos (hierro)")
			if f.coste_cobre > f.defensa.planeta.cobre:
				raise ValidationError("No tienes suficientes recursos (cobre)")
			if f.coste_plata > f.defensa.planeta.plata:
				raise ValidationError("No tienes suficientes recursos (plata)")
			if f.coste_oro > f.defensa.planeta.oro:
				raise ValidationError("No tienes suficientes recursos (oro)")

	@api.depends('defensa', 'cantidad')
	def set_name(self):
		for f in self:
			f.name = str(f.defensa.name) + " - " + str(f.cantidad)

	@api.depends('defensa', 'cantidad')
	def _compute_fechas(self):
		for f in self:
			f.duracion = f.cantidad * f.defensa.type.tiempo_construccion

	@api.depends('cantidad', 'defensa', 'defensa.planeta.hierro', 'defensa.planeta.cobre', 'defensa.planeta.plata',
	             'defensa.planeta.oro')
	def _compute_costes(self):
		for f in self:
			f.coste_hierro = f.cantidad * f.defensa.type.coste_hierro
			f.coste_cobre = f.cantidad * f.defensa.type.coste_cobre
			f.coste_plata = f.cantidad * f.defensa.type.coste_plata
			f.coste_oro = f.cantidad * f.defensa.type.coste_oro

			min = sys.maxsize  # calculamos el máximo de defensas de un tipo q se pueden construir según el recurso 'limitante' del planeta
			if f.defensa.type.coste_hierro > 0:
				cant = f.defensa.planeta.hierro / f.defensa.type.coste_hierro

				if cant < min:
					min = cant
			if f.defensa.type.coste_cobre > 0:
				cant = f.defensa.planeta.cobre / f.defensa.type.coste_cobre

				if cant < min:
					min = cant
			if f.defensa.type.coste_plata > 0:
				cant = f.defensa.planeta.plata / f.defensa.type.coste_plata
				
				if cant < min:
					min = cant
			if f.defensa.type.coste_oro > 0:
				cant = f.defensa.planeta.oro / f.defensa.type.coste_oro
				
				if cant < min:
					min = cant
			
			f.max = min
	
	@api.model
	def cron_update_defense_construction(self):
		planetas = self.env['odoogame.planet'].search([])
		print("Cron cola defenses")
		for p in planetas:
			primer_elemento = self.env['odoogame.hangar_tail_defense'].search([('defensa.planeta', '=', p.id)], limit=1)
			primer_elemento.tiempo_transcurrido += 1
			primer_elemento.fin = fields.Datetime.to_string(
				fields.Datetime.now() + timedelta(minutes=primer_elemento.duracion))
			
			if primer_elemento.tiempo_transcurrido >= primer_elemento.duracion:
				primer_elemento.defensa.cantidad += primer_elemento.cantidad
				# borrar
				primer_elemento.unlink()
	
	@api.model  # al crear una instancia del modelo se restan los recursos del planeta. No modificar una vez creada (bug)
	def create(self, values):
		new_id = super(hangar_tail_defense, self).create(values)
		
		new_id.defensa.planeta.hierro -= new_id.coste_hierro
		new_id.defensa.planeta.cobre -= new_id.coste_cobre
		new_id.defensa.planeta.plata -= new_id.coste_plata
		new_id.defensa.planeta.oro -= new_id.coste_oro

		return new_id


class flota(models.Model):
	_name = 'odoogame.flota'
	_description = 'Flota de un jugador en un planeta'
	
	name = fields.Char(compute='_set_name', readonly=True)
	jugador = fields.Many2one('odoogame.player', 'Jugador', related='ubi_actual.jugador')
	ubi_actual = fields.Many2one('odoogame.planet', string='Planeta', related='mision.origen')
	naves = fields.One2many('odoogame.constructed_starship', 'flota', string='Naves', delegate=True)
	mision = fields.Many2one('odoogame.mission')
	@api.depends('jugador', 'ubi_actual')
	def _set_name(self):
		for f in self:
			f.name = str(f.jugador.name) + " - " + str(f.ubi_actual.name)


class mission(models.Model):
	_name = 'odoogame.mission'
	_description = 'Flota desplazándose con un objetivo o misión'
	name = fields.Char(compute='_set_name', readonly=True)
	origen = fields.Many2one('odoogame.planet', string='Origen')
	destino = fields.Many2one('odoogame.planet', string='Destino')
	ubi_actual = fields.Many2one('odoogame.planet', string='Ubicacion actual')

	salida = fields.Datetime(string='Inicio', default=lambda self: fields.Datetime.now())
	llegada = fields.Datetime(string='Llegada', compute='compute_dates')
	retorno = fields.Datetime(string='Retorno', compute='compute_dates')

	mision = fields.Selection([('1', 'Transporte'), ('2', 'Despliegue'), ('3', 'Espiar'),
	                           ('4', 'Atacar'), ('5', 'Colonizar'), ('6', 'Mantener posición')],
	                          default='1', string='Misión')

	flota = fields.One2many('odoogame.flota', 'mision', string='Flota misión', delegate=True)
	
	@api.depends('type', 'origen', 'destino')
	def _set_name(self):
		for f in self:
			f.name = str(f.type) + " - " + str(f.origen) + " - " + str(f.destino)
	@api.depends('salida')
	def compute_dates(self):
		for f in self:
			tiempo_desplazamiento = 3
			salida = fields.Datetime.from_string(f.salida)
			f.llegada = fields.Datetime.to_string(salida + timedelta(minutes=tiempo_desplazamiento))
			f.retorno = fields.Datetime.to_string(salida + timedelta(minutes=tiempo_desplazamiento * 2))
	
	@api.model
	def cron_update_mission(self):
		for mision in self.search([]):
			if fields.Datetime.now() > mision.end:
				mision.ubi_actual = mision.destino
				
				defensas_defensor = self.env['odoogame.constructed_defenses'].search([('planeta', '=', mision.destino)])
				naves_defensor = self.env['odoogame.flota'].search([('ubi_actual', '=', mision.destino)])
				
				ataque_defensor = 0
				defensa_defensor = 0
				ataque_atacante = 0
				defensa_atacante = 0
				
				for dd in defensas_defensor:
					ataque_defensor += dd.type.ataque
					defensa_defensor += dd.type.defensa
				for dd in naves_defensor:
					ataque_defensor += dd.type.ataque
					defensa_defensor += dd.type.defensa

				for dd in mision.flota.naves:
					ataque_atacante += dd.type.ataque
					defensa_atacante += dd.type.defensa

				puntos_atacante = 0
				puntos_defensor = 0
				if (ataque_defensor > ataque_atacante): puntos_defensor += 1
				if (ataque_defensor > defensa_atacante): puntos_defensor += 2
				if (ataque_atacante > ataque_defensor): puntos_atacante += 1
				if (ataque_atacante > defensa_defensor): puntos_atacante += 2

				ganador = None
				porcentaje_ganado = 50/100
				if puntos_atacante > puntos_defensor:
					ganador = mision.destino.jugador
					ganador.puntos_honor_batalla += 10

					print("Batalla!!. Ha ganado: " + ganador.name)
					
					metal_ganado = mision.destino.metal * porcentaje_ganado
					cobre_ganado = mision.destino.cobre * porcentaje_ganado
					plata_ganado = mision.destino.plata * porcentaje_ganado
					oro_ganado = mision.destino.oro * porcentaje_ganado
					deuterio_ganado = mision.destino.deuterio * porcentaje_ganado
					fosiles_ganado = mision.destino.fosiles * porcentaje_ganado

					mision.destino.metal -= metal_ganado
					mision.destino.cobre -= cobre_ganado
					mision.destino.plata -= plata_ganado
					mision.destino.oro -= oro_ganado
					mision.destino.deuterio -= deuterio_ganado
					mision.destino.fosiles -= fosiles_ganado

					mision.origen.metal += metal_ganado
					mision.origen.cobre += cobre_ganado
					mision.origen.plata += plata_ganado
					mision.origen.oro += oro_ganado
					mision.origen.deuterio += deuterio_ganado
					mision.origen.fosiles += fosiles_ganado
					

					
				elif puntos_atacante < puntos_defensor:
					ganador = mision.origen.jugador
					ganador.puntos_honor_batalla += 10
					print("Batalla!!. Ha ganado: " + ganador.name)
					
				else:
					mision.origen.jugador.puntos_honor_batalla += 5
					mision.destino.jugador.puntos_honor_batalla += 5
					print("Batalla!! Empate ")
					
				#Destruccion de recursos según puntos
				self._destruir_recursos(defensas_defensor, puntos_atacante * 0.06)
				self._destruir_recursos(naves_defensor, puntos_atacante * 0.06)
				self._destruir_recursos(mision.flota.naves, puntos_defensor * 0.06)
				
	def _destruir_recursos(self, recordset, porcentaje : float):
		for recurso in recordset:
			recurso.unidades -= recurso.unidades * porcentaje
	
	@api.constrains('origen', 'destino')
	def _constrain_origen_vs_destino(self):
		for b in self:
			if b.origen == b.destino:
				raise ValidationError("Origen y destino no pueden ser iguales")


class planet_img(models.Model):
	_name = 'odoogame.planet_img'
	_description = 'Template Images'

	name = fields.Char()
	type = fields.Char()
	image = fields.Image(max_width=400, max_height=400)
	image_small = fields.Image(related="image", string="ismall", max_width=200, max_height=200)
	image_thumb = fields.Image(related="image", string="ithumb", max_width=100, max_height=100)


"""""
ps aux | grep /usr/bin/odoo


eval no funciona a demo.xml no s'agreguen planetes al jugador
no es creen els tipus de naus quan es crea un planeta
puc crear recursos encara que no tinga els recursos necessaris comprovar al Oncreate o Domain

Els related de flota van molt bé quan vaig desde missió. Pero si ho cree desde flota no.
Tampoc hi ha necessitat. Sempre q creem una flota es desde missió. També es creen desde la creacio de planeta (deurien, no ho fan)
"""""
