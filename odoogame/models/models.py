# -*- coding: utf-8 -*-
# https://github.com/xxjcaxx

from odoo import models, fields, api
import math
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
    icon = fields.Image(max_width=200, max_height=200)

    #Rel 0. Un servidor tiene muchos jugadores
    server = fields.Many2one('odoogame.server', string="Servidor", ondelete='restrict')
    # Rel 3. Un jugador ocupa palnetas
    planetas = fields.One2many('odoogame.planet', 'jugador', 'Planetas', delegate=True)

    hierro_total = fields.Float(string="Hierro", compute='_recuento_recursos')
    cobre_total = fields.Float(string="Cobre", compute='_recuento_recursos')
    plata_total = fields.Float(string="Plata", compute='_recuento_recursos')
    oro_total = fields.Float(string="Oro", compute='_recuento_recursos')
    deuterio_total = fields.Float(string="Deuterio", compute='_recuento_recursos')
    fosiles_total = fields.Float(string="Comb. Fósiles", compute='_recuento_recursos')

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

    # Rel 2. Una estrella tiene muchos planetas
    star = fields.Many2one('odoogame.star', string='Estrella', delegate=False, ondelete='restrict')
    #Rel 3. Un jugador ocupa palnetas
    jugador = fields.Many2one('odoogame.player', string='Propietario', delegate=False, ondelete='restrict')
    #Related. En quina galaxia está el planeta
    galaxy = fields.Many2one('odoogame.galaxy', string='Galaxia', related='star.galaxy', store=True, readonly=True)

    #Rel 4
    edificios = fields.One2many('odoogame.constructed_building', 'planeta', string="Edificios construidos")
    naves = fields.One2many('odoogame.constructed_starship', 'ubicacion', string="Naves estacionadas")


    hierro = fields.Float(string='Hierro')
    cobre = fields.Float(string='Cobre')
    plata = fields.Float(string='Plata')
    oro = fields.Float(string='Oro')
    deuterio = fields.Float(string='Deuterio')
    fosiles = fields.Float(string='Comb. fósiles')


class building_type(models.Model):
    _name = 'odoogame.building_type'
    _description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
    name = fields.Char(required=True)
    icon = fields.Image(max_width=200, max_height=200)

    gen_hierro = fields.Float(string='Producción de hierro')
    gen_cobre = fields.Float(string='Producción de Cobre')
    gen_plata = fields.Float(string='Producción de Plata')
    gen_oro = fields.Float(string='Producción de Oro')
    gen_deuterio = fields.Float(string='Producción de Deuterio')
    gen_fosiles = fields.Float(string='Producción de Comb. fósiles')
    gen_energia = fields.Float(strings='Produccion de W/s')

    vida_inicial = fields.Float(string='Vida inicial edificio', help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')
    tipo_energia = fields.Selection([('1','Comb. Fósiles'),('2','Electricidad'),('3','Deuterio')])
    energia_funcionamiento = fields.Float(string='Energia')


    #Costes de construcción
    coste_hierro = fields.Float(string='Coste de hierro')
    coste_cobre = fields.Float(string='Coste de Cobre')
    coste_plata = fields.Float(string='Coste de Plata')
    coste_oro = fields.Float(string='Coste de Oro')
    tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')

class constructed_building(models.Model):
    _name = 'odoogame.constructed_building'
    _description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
    name = fields.Char(required=True)
    #Rel 4
    planeta = fields.Many2one('odoogame.planet', 'Planeta')

    estado = fields.Selection([('1', 'En construcción'), ('2', 'Activo'), ('3', 'Inactivo'), ('4', 'En reparación'), ('5', 'Destruido')])
    vida_actual = fields.Float(string='Coste de Oro')
    nivel_produccion = fields.Integer()
    nivel_almacen = fields.Integer()

    type = fields.Many2one('odoogame.building_type', string="Tipo de edificio")

class starship_type(models.Model):
    _name = 'odoogame.starship_type'
    _description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
    name = fields.Char(required=True)



    coste_hierro = fields.Float(string='Coste de hierro')
    coste_cobre = fields.Float(string='Coste de Cobre')
    coste_plata = fields.Float(string='Coste de Plata')
    coste_oro = fields.Float(string='Coste de Oro')
    tiempo_construccion = fields.Integer(string='Tiempo necesario para su construcción')


    vida_inicial = fields.Float(string='Vida inicial de la nave', help='Va perdiendo vida por desgaste o por ataques. Se puede reparar')
    tipo_energia = fields.Selection([('1', 'Comb. Fósiles'), ('2', 'Deuterio')])
    energia_funcionamiento = fields.Float(string='Energia')

    ataque = fields.Float(string='Ataque de la unidad')
    defensa = fields.Float(string='Defensa de la unidad')

class constructed_starship(models.Model):
    _name = 'odoogame.constructed_starship'
    _description = 'Edificios que estarán por defecto en el juego. El jugador elegirá qué tipo de edificio crear'
    name = fields.Char(required=True)
    # Rel 4
    player = fields.Many2one('odoogame.player', 'Jugador')

    estado = fields.Selection([('1', 'En construcción'), ('2', 'Activo'), ('3', 'En reparación'), ('4', 'Destruido')])
    vida_actual = fields.Float(string='Coste de Oro')
    nivel_almacen = fields.Integer()

    ubicacion = fields.Many2one('odoogame.planet', 'Planeta')
    type = fields.Many2one('odoogame.starship_type', string="Tipo de nave")

    #tiempo_reparacion = fields.datetime(compute=)
"""""
class house(models.Model):
    _name = 'odoogame.house'
    _description = 'Familias que han destacado en las grandes naciones del mundo, ' \
                   'aunque aquí son más conocidas como "casas" y cada una de ellas han c' \
                   'reado un imperio que ha tenido repercusión en el desarrollo de la historia'

    name = fields.Char()


class city(models.Model):
    _name = 'odoogame.player'
    _description = 'odoogame.odoogame'

    name = fields.Char()


class player(models.Model):
    _name = 'odoogame.player'
    _description = 'odoogame.odoogame'

    name = fields.Char()

"""