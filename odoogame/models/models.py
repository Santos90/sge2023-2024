# -*- coding: utf-8 -*-

from odoo import models, fields, api


class player(models.Model):
      _name = 'odoogame.player'
      _description = 'odoogame.odoogame'

      name = fields.Char(required=True)
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
      description = fields.Text()


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

