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
    primera_pieza = fields.Boolean(string="Primera Pieza", readonly = True)

    def action_finalizar(self):#Quita la orden de pendientes por corte a cortes realizados
        cont = 0;
        for corte in self.cortadora_id:
            if corte.estado != "Material cortado":
              break
            cont +=1
        if len(self.cortadora_id) == cont: #Revisa que todos los archivos esten cortados para poder pasarlos al modulo de realizados
            vals = {
                "orden_trabajo": self.orden_trabajo,
                "fecha_entrada": datetime.today(),
                "nombre_orden": self.nombre_orden,
                "tipo_orden":self.tipo_orden,
                # "materiales_id":self.materiales_id
            }
            # Proceso para cambiar el status en el modulo de procesos
            get_otp = self.env['dtm.proceso'].search([("ot_number","=",self.orden_trabajo),("tipe_order","=",self.tipo_orden)],order='id desc',limit=1)
            get_info = self.env['dtm.laser.realizados'].search([])
            if self.primera_pieza: #Cambia status y pone valor verdadero a primera pieza
                vals["primera_pieza"]=True
                get_info.create(vals) #Crea la orden cortada de primera pieza
                get_info =  self.env['dtm.laser.realizados'].search([("orden_trabajo","=", self.orden_trabajo),("tipo_orden","=", self.tipo_orden),("primera_pieza","=",True)],order='id desc',limit=1)
                get_otp.write({
                    "status":"revision"
                })
            else:  #Cambia status y pone valor verdadero false a primera pieza
                vals["primera_pieza"]=False
                vals["materiales_id"]= self.materiales_id
                get_info.create(vals)#Crea la orden cortada de segunda pieza
                get_info =  self.env['dtm.laser.realizados'].search([("orden_trabajo","=", self.orden_trabajo),("tipo_orden","=", self.tipo_orden),("primera_pieza","=",False)],order='id desc',limit=1)
                get_otp.write({
                    "status":"doblado"
                })
                for lamina in self.materiales_id:
                    get_lamina = self.env['dtm.materiales'].search([("codigo","=",lamina.identificador)])
                    cantidad = 0
                    apartado = 0
                    if get_lamina:
                        cantidad = get_lamina[0].cantidad - lamina.cantidad
                        apartado = get_lamina[0].apartado - lamina.cantidad
                    vals = {
                        "cantidad":cantidad,
                        "apartado":apartado,
                        "disponible":cantidad - apartado,
                    }
                    get_lamina.write(vals)

            lines = []
            for docs in self.cortadora_id:
                line = (0,get_info[0].id,{
                    "nombre": docs.nombre,
                    "documentos":docs.documentos,
                })
                lines.append(line)
            get_info.cortadora_id = lines

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
    primera_pieza = fields.Boolean(string="Primera Pieza",readonly=True)
    materiales_id = fields.Many2many("dtm.cortadora.laminas", readonly=True)

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
            for main in get_laser: #Revisa todos los archivos que estan para corte en dtm_materiales_laser
                archivo = main.cortadora_id.mapped("nombre")
                if self.nombre in archivo:
                    documento = main.primera_pieza_id if main.primera_pieza else main.cortadora_id
                    if self.nombre in documento.mapped("nombre"):#Revisa que el archivo este en la lista de archivos a cortar
                        estado = "Material cortado" if self.cortado else "" #Pone etiqueta en cortado si el botón boleano es verdadero
                        self.estado = estado # Cambia el estado de la etiqueta
                        get_otp = self.env['dtm.proceso'].search([("ot_number","=",main.orden_trabajo),("tipe_order","=",main.tipo_orden)])
                        documentos = get_otp.primera_pieza_id if main.primera_pieza else get_otp.cortadora_id #Carga la lista de archivos según el tipo
                        if self.nombre in documentos.mapped("nombre"):
                            documentos.search([("nombre","=",self.nombre)]).write({"cortado":estado})#Cambia el status del corte en el modulo de procesos


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




