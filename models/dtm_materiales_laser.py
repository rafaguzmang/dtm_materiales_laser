from odoo import api,models,fields
from datetime import datetime
from odoo.exceptions import ValidationError



class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"
    _description = "Lleva el listado de los materiales a cortar en la laser"

    orden_trabajo = fields.Integer(string="Orden de Trabajo")
    fecha_entrada = fields.Date(string="Fecha de antrada")
    nombre_orden = fields.Char(string="Nombre")
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" )
    tipo_orden = fields.Char(string="Tipo")
    materiales_id = fields.Many2many("dtm.cortadora.laminas")


    def action_finalizar(self):
        get_otp = self.env['dtm.proceso'].search([("ot_number","=",self.orden_trabajo),("tipe_order","=","OT")])
        get_otd = self.env['dtm.odt'].search([("ot_number","=",self.orden_trabajo)]) # Actualiza el status en los modelos odt y proceso a corte
        cont = 0;
        for corte in self.cortadora_id:
            if not corte.cortado:
              break
            cont +=1
        if cont == 0:
                 get_otd.write({"status":"Corte"})
                 get_otp.write({"status":"corte"})
        else:
            if corte.primera_pieza:
                get_otd.write({"status":"Corte - Revisión FAI"})
                get_otp.write({"status":"corterevision"})
            else:
                get_otd.write({"status":"Corte - Doblado"})
                get_otp.write({"status":"cortedoblado"})
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
            get_otp.write({
                "status":"doblado"
            })
            get_info =  self.env['dtm.laser.realizados'].search([("orden_trabajo","=", self.orden_trabajo)])
            lines = []
            for docs in self.cortadora_id:
                line = (0,get_info.id,{
                    "nombre": docs.nombre,
                    "documentos":docs.documentos,
                })
                lines.append(line)
            get_info.cortadora_id = lines
            self.env['dtm.materiales.laser'].search([("id","=",self.id)]).unlink()

        else:
             raise ValidationError("Todos los nesteos deben estar cortados")


    def get_view(self, view_id=None, view_type='form', **options):
        res = super(MaterialesLasser,self).get_view(view_id, view_type,**options)
        get_laser = self.env['dtm.materiales.laser'].search([])
        for main in get_laser:

            get_otd = self.env['dtm.odt'].search([("ot_number","=",main.orden_trabajo)]) # Actualiza el status en los modelos odt y proceso a corte
            get_otp = self.env['dtm.proceso'].search([("ot_number","=",main.orden_trabajo),("tipe_order","=","OT")])

            for n_archivo in main.cortadora_id:

                if n_archivo.cortado:
                    break
                get_otd.write({"status":"Corte"})
                get_otp.write({"status":"corte"})





        return res

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
    primera_pieza = fields.Boolean(default=False)

    @api.onchange("cortado")
    def _action_cortado (self):
            get_laser = self.env['dtm.materiales.laser'].search([])
            for main in get_laser:
                for n_archivo in main.cortadora_id:
                    if self.nombre == n_archivo.nombre:

                        get_otd = self.env['dtm.odt'].search([("ot_number","=",main.orden_trabajo)]) # Actualiza el status en los modelos odt y proceso a corte
                        get_otp = self.env['dtm.proceso'].search([("ot_number","=",main.orden_trabajo),("tipe_order","=","OT")])

                        if self.primera_pieza:
                            documentos = get_otp.primera_pieza_id
                        else:
                            documentos = get_otp.cortadora_id

                        for documento in documentos:
                                if documento.nombre == self.nombre:
                                    if self.cortado:
                                        documento.cortado = "Material cortado"
                                        if self.primera_pieza:
                                            get_otd.write({"status":"Corte - Revisión FAI"})
                                            get_otp.write({"status":"corterevision"})
                                        get_otd.write({"status":"Corte - Doblado"})
                                        get_otp.write({"status":"cortedoblado"})
                                    else:
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


