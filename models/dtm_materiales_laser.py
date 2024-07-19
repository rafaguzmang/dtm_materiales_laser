from odoo import api,models,fields
from datetime import datetime
from odoo.exceptions import ValidationError



class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"
    _description = "Lleva el listado de los materiales a cortar en la laser"

    orden_trabajo = fields.Integer(string="Orden de Trabajo", readonly=True)
    fecha_entrada = fields.Date(string="Fecha de antrada", readonly=True)
    nombre_orden = fields.Char(string="Nombre", readonly=True)
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" , readonly=True)
    tipo_orden = fields.Char(string="Tipo", readonly=True)
    materiales_id = fields.Many2many("dtm.cortadora.laminas", readonly=True)

    def action_finalizar(self):
        cont = 0;
        for corte in self.cortadora_id:
            if corte.estado != "Material cortado":
              break
            cont +=1
        if len(self.cortadora_id) == cont:
            vals = {
                "orden_trabajo": self.orden_trabajo,
                "fecha_entrada": datetime.today(),
                "nombre_orden": self.nombre_orden,
                "tipo_orden":self.tipo_orden
            }
            get_info = self.env['dtm.laser.realizados'].search([])
            get_info.create(vals)
            get_otp = self.env['dtm.proceso'].search([("ot_number","=",self.orden_trabajo),("tipe_order","=",self.tipo_orden)])
            get_otp.write({
                "status":"doblado"
            })
            get_info =  self.env['dtm.laser.realizados'].search([("orden_trabajo","=", self.orden_trabajo),("tipo_orden","=", self.tipo_orden)],order='id desc',limit=1)
            lines = []
            for docs in self.cortadora_id:
                line = (0,get_info.id,{
                    "nombre": docs.nombre,
                    "documentos":docs.documentos,
                })
                lines.append(line)
            get_info.cortadora_id = lines

            for lamina in self.materiales_id:
                get_lamina = self.env['dtm.materiales'].search([("codigo","=",lamina.identificador)])
                cantidad = get_lamina.cantidad - lamina.cantidad
                apartado = get_lamina.apartado - lamina.cantidad
                vals = {
                    "cantidad":cantidad,
                    "apartado":apartado,
                    "disponible":cantidad - apartado,
                }
                get_lamina.write(vals)
            get_self = self.env['dtm.materiales.laser'].browse(self.id)
            get_self.unlink()
        else:
             raise ValidationError("Todos los nesteos deben estar cortados")



class Realizados(models.Model): #--------------Muestra los trabajos ya realizados---------------------
    _name = "dtm.laser.realizados"
    _description = "Lleva el listado de todo el material cortado en la Laser"

    orden_trabajo = fields.Integer(string="Orden de Trabajo",readonly=True)
    tipo_orden = fields.Char(string="Tipo", readonly=True)
    fecha_entrada = fields.Date(string="Fecha de Término",readonly=True)
    nombre_orden = fields.Char(string="Nombre",readonly=True)
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" , readonly = True)

class Documentos(models.Model):
    _name = "dtm.documentos.cortadora"
    _description = "Guarda los nesteos del Radán"

    documentos = fields.Binary()
    nombre = fields.Char()
    cortado = fields.Boolean()
    contador = fields.Integer()
    primera_pieza = fields.Boolean()
    estado = fields.Char(string="Estado del corte")

    def action_mas(self):
        self.contador += 1

    def action_menos(self):
        self.contador -= 1
        if self.contador < 0:
            self.contador = 0

    @api.onchange("cortado")
    def _action_cortado (self):
            get_laser = self.env['dtm.materiales.laser'].search([])
            for main in get_laser:
                for n_archivo in main.cortadora_id:
                    if self.nombre == n_archivo.nombre:
                        get_otp = self.env['dtm.proceso'].search([("ot_number","=",main.orden_trabajo),("tipe_order","=",main.tipo_orden)])
                        if self.primera_pieza:
                            documentos = get_otp.primera_pieza_id
                        else:
                            documentos = get_otp.cortadora_id
                        for documento in documentos:
                            if documento.nombre == self.nombre:
                                get_self = self.env['dtm.documentos.cortadora'].search([("id","=",self._origin.id)])
                                if self.cortado:
                                    get_self.write({
                                        "estado": "Material cortado"
                                    })
                                    self.estado = "Material cortado"
                                    documento.cortado = "Material cortado"
                                    get_otp.write({"status":"corte"})
                                    if self.primera_pieza:
                                        get_otp.write({"status":"revision"})
                                else:
                                    get_self.write({
                                        "estado": ""
                                    })
                                    self.estado = ""
                                    documento.cortado = ""

class Cortadora(models.Model):
    _name = "dtm.cortadora.laminas"
    _description = "Guarda las laminas a cortar con su id, localización y medidas"

    identificador = fields.Integer(string="ID")
    nombre = fields.Char(string="Material")
    medida = fields.Char(string="Medidas")
    cantidad = fields.Integer(string="Cantidad")
    inventario = fields.Integer(string="Inventario")
    requerido = fields.Integer(string="Requerido (Compras)")
    localizacion = fields.Char(string="Localizacion")




