# -*- coding: utf-8 -*-

from odoo import models, fields, api

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
              for p in self.planetas:
                  self.hierro_total += p.hierro
                  self.cobre_total += p.cobre
                  self.plata_total += p.plata
                  self.oro_total += p.oro
                  self.deuterio_total += p.deuterio
                  self.fosiles_total += p.fosiles


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

    hierro = fields.Float(string='Hierro')
    cobre = fields.Float(string='Cobre')
    plata = fields.Float(string='Plata')
    oro = fields.Float(string='Oro')
    deuterio = fields.Float(string='Deuterio')
    fosiles = fields.Float(string='Comb. fósiles')


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