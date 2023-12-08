# -*- coding: utf-8 -*-
# https://github.com/xxjcaxx

import random
from odoo import models, fields, api
import math

from datetime import datetime, timedelta
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

	incorporacion_al_servidor = fields.Datetime(readonly=True)

	name = fields.Char(required=True)
	#     value = fields.Integer()
	#     value2 = fields.Float(compute="_value_pc", store=True)
	description = fields.Text()
	icon = fields.Image(max_width=300, max_height=300, string=" ")

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

	def generate_planet(self):
		for p in self:
			planet_img = self.env['odoogame.planet_img'].search([]).ids
			random.shuffle(planet_img)
			stars = self.env['odoogame.star'].search([]).ids
			random.shuffle(stars)
			planetas = p.planetas.create({
				"name": "Planet" + str(p.id),
				"icon": self.env['odoogame.planet_img'].browse(planet_img[0]).image_small,
				"jugador": p.id,
				"star": stars[0]
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
	icon = fields.Image(max_width=300, max_height=300, string=" ")

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

	#ataques = fields.One2many('odoogame.battle', 'atacante', string='Batallas iniciadas')
	#defensas = fields.One2many('odoogame.battle', 'atacante', string='Ataques recibidos')

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

	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")
	type = fields.Many2one('odoogame.building_type', string="Tipo de edificio")

	vida_inicial = fields.Float(string='Vida inicial edificio',
	                            help='Va perdiendo vida por desgaste o por ataques. Se puede reparar',
	                            related='type.vida_inicial')
	tipo_energia = fields.Selection(related='type.tipo_energia')

	# Rel 4
	planeta = fields.Many2one('odoogame.planet', 'Planeta')

	estado = fields.Selection(
		[('1', 'En construcción'), ('2', 'Activo'), ('3', 'Inactivo'), ('4', 'En reparación'), ('5', 'Destruido'),
		 ('6', 'Nivel de producción'), ('7', 'Nivel de almacén')])
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
	gen_hierro = fields.Integer(string='Gen hierro', compute='_calculo_por_nivel_produccion')
	gen_cobre = fields.Integer(string='Gen Cobre', compute='_calculo_por_nivel_produccion')
	gen_plata = fields.Integer(string='Gen Plata', compute='_calculo_por_nivel_produccion')
	gen_oro = fields.Integer(string='Gen Oro', compute='_calculo_por_nivel_produccion')
	gen_deuterio = fields.Integer(string='Gen Deuterio', compute='_calculo_por_nivel_produccion')
	gen_fosiles = fields.Integer(string='Gen Comb. fósiles', compute='_calculo_por_nivel_produccion')
	gen_energia = fields.Integer(string='Gen W/s', compute='_calculo_por_nivel_produccion')

	energia_funcionamiento = fields.Integer(string='Energia de funcionamiento', compute='_calculo_por_nivel_produccion')

	# Costes de construcción
	coste_hierro = fields.Integer(string='Coste de hierro', compute='_calculo_por_nivel_produccion')
	coste_cobre = fields.Integer(string='Coste de Cobre', compute='_calculo_por_nivel_produccion')
	coste_plata = fields.Integer(string='Coste de Plata', compute='_calculo_por_nivel_produccion')
	coste_oro = fields.Integer(string='Coste de Oro', compute='_calculo_por_nivel_produccion')

	tiempo_construccion = fields.Integer(related='type.tiempo_construccion')
	time_update_gen = fields.Integer(string='Tiempo construcción', compute='_calculo_por_nivel_produccion',
	                                 stored='true')
	time_update_alm = fields.Integer(string='Tiempo construcción', compute='_calculo_por_nivel_produccion',
	                                 stored='true')

	tiempo_restante = fields.Integer(
		default=0)  # variable que segun el caso, nos servirá para contar el tiempo restante

	hierro_vs_max = fields.Char(string='Hierro', compute='_compute_qty_display')
	cobre_vs_max = fields.Char(string='Cobre', compute='_compute_qty_display')
	plata_vs_max = fields.Char(string='Palta', compute='_compute_qty_display')
	oro_vs_max = fields.Char(string='Oro', compute='_compute_qty_display')
	deuterio_vs_max = fields.Char(string='Deuterio', compute='_compute_qty_display')
	fosiles_vs_max = fields.Char(string='Fósiles', compute='_compute_qty_display')
	tiempo_vs_max = fields.Char(string='Tiempo restante', compute='_compute_qty_display')

	@api.depends('alm_hierro', 'alm_hierro_max', 'alm_cobre', 'alm_cobre_max', 'alm_plata', 'alm_plata_max', 'alm_oro',
	             'alm_oro_max', 'alm_deuterio', 'alm_deuterio_max', 'alm_fosiles', 'alm_fosiles_max', 'tiempo_restante')
	def _compute_qty_display(self):
		for record in self:
			record.hierro_vs_max = f'{record.alm_hierro}/{record.alm_hierro_max}'
			record.cobre_vs_max = f'{record.alm_cobre}/{record.alm_cobre_max}'
			record.plata_vs_max = f'{record.alm_plata}/{record.alm_plata_max}'
			record.oro_vs_max = f'{record.alm_oro}/{record.alm_oro_max}'
			record.deuterio_vs_max = f'{record.alm_deuterio}/{record.alm_deuterio_max}'
			record.fosiles_vs_max = f'{record.alm_fosiles}/{record.alm_fosiles_max}'

			if record.estado == '1':
				record.tiempo_vs_max = f'{record.tiempo_restante}/{record.tiempo_construccion} minutos'
			if record.estado == '6':
				record.tiempo_vs_max = f'{record.tiempo_restante}/{record.time_update_gen} minutos'
			if record.estado == '7':
				record.tiempo_vs_max = f'{record.tiempo_restante}/{record.time_update_alm} minutos'

			print("Hierro: ", record.hierro_vs_max)
			print("Cobre: ", record.cobre_vs_max)
			print("Plata: ", record.plata_vs_max)
			print("Oro: ", record.oro_vs_max)

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

			e.time_update_gen = e.type.tiempo_construccion + e.type.tiempo_construccion * math.log(e.nivel_produccion)
			e.energia_funcionamiento = e.type.energia_funcionamiento + e.type.energia_funcionamiento * math.log(
				e.nivel_produccion)

			print("Gen Hierro: ", e.type.gen_hierro)

	@api.depends('nivel_almacen')
	def _calculo_por_nivel_almacen(self):
		for e in self:
			e.alm_hierro_max = (e.type.gen_hierro + e.type.gen_hierro * math.log(e.nivel_almacen)) * 1440
			e.alm_cobre_max = (e.type.gen_cobre + e.type.gen_cobre * math.log(e.nivel_almacen)) * 1440
			e.alm_plata_max = (e.type.gen_plata + e.type.gen_plata * math.log(e.nivel_almacen)) * 1440
			e.alm_oro_max = (e.type.gen_oro + e.type.gen_oro * math.log(e.nivel_almacen)) * 1440
			e.alm_deuterio_max = (e.type.gen_deuterio + e.type.gen_deuterio * math.log(e.nivel_almacen)) * 1440
			e.alm_fosiles_max = (e.type.gen_fosiles + e.type.gen_fosiles * math.log(e.nivel_almacen)) * 1440

			e.time_update_alm = e.type.tiempo_construccion + e.type.tiempo_construccion * math.log(e.nivel_almacen)

	def update_gen(self):
		for edificio in self:
			edificio.estado = '6'

	def update_alm(self):
		for edificio in self:
			edificio.estado = '7'

	def recolectar_recursos(self):

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
		for b in self.search([]):
			# Updates
			if b.estado == '1':

				b.tiempo_restante += 1

				if b.tiempo_restante == b.tiempo_construccion:
					b.tiempo_restante = 0
					b.nivel_produccion += 1
					b.estado = '2'

			elif b.estado == '6':

				b.tiempo_restante += 1

				if b.tiempo_restante == b.time_update_gen:
					b.tiempo_restante = 0
					b.nivel_produccion += 1
					b.estado = '2'

			elif b.estado == '7':

				b.tiempo_restante += 1

				if b.tiempo_restante == b.time_update_alm:
					b.tiempo_restante = 0
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

	coste_hierro = fields.Integer(string='Coste de hierro')
	coste_cobre = fields.Integer(string='Coste de Cobre')
	coste_plata = fields.Integer(string='Coste de Plata')
	coste_oro = fields.Integer(string='Coste de Oro')

	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


class constructed_starship(models.Model):
	_name = 'odoogame.constructed_starship'
	_description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
	type = fields.Many2one('odoogame.starship_type', string="Tipo de nave")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")

	# Rel 4
	player = fields.Many2one('odoogame.player', 'Jugador')
	ubicacion = fields.Many2one('odoogame.planet', 'Planeta')

	estado = fields.Selection([('1', 'En construcción'), ('2', 'Activo'), ('3', 'En reparación'), ('4', 'Destruido'),
	                           ('5', 'Subiendo nivel producción'), ('6', 'Subiendo nivel almacén')],
	                          default='1', string='Estado')

	vida_actual = fields.Float(string='Vida actual')
	nivel_almacen = fields.Integer(default=1)

	#atacando_en_batalla = fields.Many2one('odoogame.battle', string='En ataque')


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

	coste_hierro = fields.Integer(string='Coste de hierro')
	coste_cobre = fields.Integer(string='Coste de Cobre')
	coste_plata = fields.Integer(string='Coste de Plata')
	coste_oro = fields.Integer(string='Coste de Oro')

	tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')

class constructed_defense(models.Model):
	_name = 'odoogame.constructed_defense'
	_description = 'Estructuras defensivas construidas'

	name = fields.Char(string='Nombre', compute='set_name')
	type = fields.Many2one('odoogame.defense_type', string="Tipo de defensa")
	icon = fields.Image(max_width=300, max_height=300, related='type.icon', string=" ")

	# Rel 4

	planeta = fields.Many2one('odoogame.planet', string='Planeta')
	cantidad = fields.Integer(string='Unidades')

	vida_actual = fields.Float(string='Vida actual')

	@api.depends('type', 'planeta')
	def set_name(self):
		print("Nueva instancia 'constructed_defense'")
		for f in self:
			f.name = str(f.planeta.name) + "-" + str(f.type.name)
			print("Nombre: ",str(f.type.name))




class hangar_tail_defense(models.Model): #Nombre para relaciones: Elemento a contruir
	_name = 'odoogame.hangar_tail_defense'
	_description = 'Cola de contrucción'
	name = fields.Char(string='Nombre', compute='set_name')

	#relacion: Elemento a contruir "es de 1 tipo"...
	defensa = fields.Many2one('odoogame.constructed_defense')
	cantidad = fields.Integer(default=1)
	max = fields.Integer(compute='_compute_costes')


	inicio = fields.Datetime(default = lambda self: fields.Datetime.now()) #no mola, data al obrir formulari, no al guardar
	fin = fields.Datetime(string="Fin de la construccion", compute="_compute_fechas")
	restante = fields.Datetime(string="Tiempo restante", compute="_compute_fechas")

	# Costes de construcción
	coste_hierro = fields.Integer(string='Coste de hierro', compute='_compute_costes')
	coste_cobre = fields.Integer(string='Coste de Cobre', compute='_compute_costes')
	coste_plata = fields.Integer(string='Coste de Plata', compute='_compute_costes')
	coste_oro = fields.Integer(string='Coste de Oro', compute='_compute_costes')

	@api.depends('defensa', 'cantidad')
	def set_name(self):
		for f in self:
			f.name = str(f.defensa.name) + "-" + str(f.cantidad)

	@api.depends('inicio')
	def _compute_fechas(self):
		for f in self:
			inicio = fields.Datetime.from_string(f.inicio)
			duracion = f.cantidad * f.defensa.type.tiempo_construccion
			f.fin = fields.Datetime.to_string(inicio + timedelta(minutes = duracion))
			f.restante = 0

	@api.depends('cantidad', 'defensa', 'defensa.planeta.hierro', 'defensa.planeta.cobre', 'defensa.planeta.plata', 'defensa.planeta.oro')
	def _compute_costes(self):
		for f in self:
			f.coste_hierro = f.cantidad * f.defensa.type.coste_hierro
			f.coste_cobre = f.cantidad * f.defensa.type.coste_cobre
			f.coste_plata = f.cantidad * f.defensa.type.coste_plata
			f.coste_oro = f.cantidad * f.defensa.type.coste_oro


			max = 0
			if f.defensa.type.coste_hierro > 0:
				cant = f.defensa.planeta.hierro / f.defensa.type.coste_hierro
				print(cant)
				if cant > max:
					max = cant
			if f.defensa.type.coste_cobre > 0:
				cant = f.defensa.planeta.cobre / f.defensa.type.coste_cobre
				print(cant)
				if cant > max:
					max = cant
			if f.defensa.type.coste_plata > 0:
				cant = f.defensa.planeta.plata / f.defensa.type.coste_plata
				print(cant)
				if cant > max:
					max = cant
			if f.defensa.type.coste_oro > 0:
				cant = f.defensa.planeta.oro / f.defensa.type.coste_oro
				print(cant)
				if cant > max:
					max = cant

			f.max = max

class flota(models.Model):
	_name = 'odoogame.flota'
	_description = 'Flota de un jugador en un planeta'

	planeta = fields.Many2one('odoogame.planet', string='Planeta')
	#naves = fields.One2many('odoogame.constructed_starship', 'flota', string='Naves atacantes')


class mission(models.Model):
	_name = 'odoogame.mission'
	_description = 'Flota desplazándose con un objetivo o misión'
	origen = fields.Many2one('odoogame.planet', string='Origen')
	destino = fields.Many2one('odoogame.planet', string='Destino')

	salida = fields.Datetime(string='Inicio', default=lambda self: fields.Datetime.now())
	llegada = fields.Datetime(string='Llegada', compute='compute_dates')
	retorno = fields.Datetime(string='Retorno', compute='compute_dates')

	mision = fields.Selection([('1', 'Transporte'), ('2', 'Despliegue'), ('3', 'Espiar'),
	                           ('4', 'Atacar'), ('5', 'Colonizar'), ('6', 'Mantener posición')],
	                          default='1', string='Misión')

	flota = fields.One2many('odoogame.flota', 'id', string='Flotas atacantes')

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

"""""
