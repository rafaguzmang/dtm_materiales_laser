from odoo import api,models,fields
from datetime import datetime


class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"
    _description = "Lleva el listado de los materiales a cortar en la laser"

    orden_trabajo = fields.Integer(string="Orden de Trabajo")
    fecha_entrada = fields.Date(string="Fecha de antrada")
    nombre_orden = fields.Char(string="Nombre")
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" )
    tipo_orden = fields.Char(string="Tipo")

    #--------------------  Llena la tabla con las ordenes de servicio ----------------



    def action_terminado(self):
        cont = 0
        for corte in self.cortadora_id:
            cont += 1
            if not corte.cortado:
                break

        if len(self.cortadora_id) == cont:
            vals = {
                "orden_trabajo": self.orden_trabajo,
                "fecha_entrada": datetime.today(),
                "nombre_orden": self.nombre_orden,
            }

            get_info = self.env['dtm.laser.realizados'].search([])
            get_info.create(vals)

            get_otd = self.env['dtm.odt'].search([("ot_number","=",self.orden_trabajo)]) # Actualiza el status en los modelos odt y proceso a corte
            get_otd.write({"status":"Doblado"})
            get_otp = self.env['dtm.proceso'].search([("ot_number","=",self.orden_trabajo),("tipe_order","=","OT")])
            get_otp.write({"status":"doblado"})
            get_info =  self.env['dtm.laser.realizados'].search([("orden_trabajo","=", self.orden_trabajo)])

            lines = []
            line = (5,0,{})
            lines.append(line)
            for docs in self.cortadora_id:
                line = (0,get_info.id,{
                    "nombre": docs.nombre,
                    "documentos":docs.documentos,
                })
                lines.append(line)
            get_info.cortadora_id = lines

            self.env['dtm.materiales.laser'].search([("id","=",self.id)]).unlink()


class Realizados(models.Model): #--------------Muestra los trabajos ya realizados---------------------
    _name = "dtm.laser.realizados"
    _description = "Lleva el listado de todo el material cortado en la Laser"

    orden_trabajo = fields.Integer(string="Orden de Trabajo")
    fecha_entrada = fields.Date(string="Fecha de Término")
    nombre_orden = fields.Char(string="Nombre")
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" , readonly = True)


class Cortadora(models.Model):
    _name = "dtm.documentos.cortadora"
    _description = "Guarda los nesteos del Radán"

    documentos = fields.Binary()
    nombre = fields.Char()
    cortado = fields.Boolean(default=False)


