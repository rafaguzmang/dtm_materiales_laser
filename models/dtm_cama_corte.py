from odoo import fields, models, api

class CamaCorte(models.Model):
    _name = 'dtm.cama.corte'
    _description = 'Modelo para llevar el control del material que está en las camas de corte de las diferentes máquinas'

    codigo = fields.Integer(string='Código')
    maquina = fields.Char(string='Máquina')
    index = fields.Integer(string='Index')
    cortado = fields.Boolean(string='Cortado')
    nombre = fields.Char(string='Lámina')
    medida = fields.Char(string='Medida')
    orden = fields.Integer(string='Orden')
    archivo = fields.Char(string='Archivo')
    borrado = fields.Boolean(string='Borrado')
    play  = fields.Boolean(string='Play')
    tiempo_start = fields.Datetime()
    tiempo = fields.Float(string='Tiempo')
    cantidad = fields.Integer(string='Cantidad')
    contador = fields.Integer(string='Contador')
