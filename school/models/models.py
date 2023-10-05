# -*- coding: utf-8 -*-

from odoo import models, fields, api


class student(models.Model):
     _name = 'school.student'
     _description = 'The students'

     name = fields.Char(
          required = True
     )
     year = fields.Integer()
     birth_date = fields.Date()
     tutor = fields.Many2one('school.teacher', string='Tutor', ondelete='set null')
     matriculat = fields.Boolean(
          string= "Matriculado",
          default = True
     )

     topics = fields.Many2many('school.topic')
     qualification = fields.One2many('school.qualification', 'student', String='Notes')


#    value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

class topic(models.Model):
     _name = 'school.topic'
     _description = 'Topics'

     name = fields.Char()
     students = fields.Many2many('school.students')


class teacher(models.Model):
     _name = 'school.teacher'
     _description = 'Teachers'

     name = fields.Char()
     students = fields.One2many('school.student', 'tutor', String='Alumnes tutoritzats')



class qualification(models.Model):
     _name = 'school.qualification'

     nota = fields.Float()
     student = fields.Many2one('school.student', string='Tutor', ondelete='set null')

