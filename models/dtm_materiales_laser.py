from odoo import api,models,fields
from datetime import datetime


class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"
    _description = "Lleva el listado de los materiales a cortar en la laser"

<<<<<<< HEAD
    orden_trabajo = fields.Integer(string="Orden de Trabajo")
    fecha_entrada = fields.Date(string="Fecha de antrada")
    nombre_orden = fields.Char(string="Nombre")
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" , readonly = True)
=======
    material = fields.Char(string="MATERIAL", readonly=True)
    calibre = fields.Char(string="CALIBRE", readonly=True)
    largo = fields.Char(string="LARGO", readonly=True)
    ancho = fields.Char(string="ANCHO", readonly=True)
    sheets = fields.Char(string="SHEETS", readonly=True)
    drawingname  = fields.Char(string="DRAWINGNAME", readonly=True)
    material_id = fields.Integer()

    #--------------------  Llena la tabla con las ordenes de servicio ----------------

<<<<<<< HEAD
    def acction_less(self):
        get_cantidad = self.env["dtm.materiales"].browse(self.material_id)
        cantidad = get_cantidad.cantidad - int(self.sheets)
=======
    def acction_less(self):#----------------------- Borra los procesos ya realizados en la coratadora laser y en el modulo de diseño pasandolos a otra tabla donde se llevará el registro
        # get_cantidad = self.env["dtm.materiales"].browse(self.material_id)
        # cantidad = get_cantidad.cantidad - int(self.sheets)
>>>>>>> a3ef8156c324f80ea25b553eb81ef8c9e6cc1839

        material = self.material
        calibre = self.calibre
        largo = self.largo
        ancho = self.ancho
        sheets = self.sheets
        drawingname = self.drawingname
        material_id = str(self.material_id)

<<<<<<< HEAD
        self.env.cr.execute("UPDATE dtm_materiales SET cantidad = "+str(cantidad)+" WHERE id = "+str(self.material_id))

        self.env.cr.execute("INSERT INTO dtm_laser_realizados (material, calibre, largo, ancho, sheets, drawingname, material_id)" +
                            "VALUES ('"+material+"', '"+calibre+"', '"+largo+"', '"+ancho+"', '"+sheets+"', '"+drawingname+"', "+material_id+");")

=======
        # Descuenta los materiales ya utilizados del stock
        # self.env.cr.execute("UPDATE dtm_materiales SET cantidad = "+str(cantidad)+" WHERE id = "+str(self.material_id))
        # Pasa la orden de pendientes a realizados en el modulo de dtm_materiales_laser
        self.env.cr.execute("INSERT INTO dtm_laser_realizados (material, calibre, largo, ancho, sheets, drawingname, material_id)" +
                            "VALUES ('"+material+"', '"+calibre+"', '"+largo+"', '"+ancho+"', '"+sheets+"', '"+drawingname+"', "+material_id+");")
        # Retira las ordenes ya cortadas de Cortadora Laser
>>>>>>> a3ef8156c324f80ea25b553eb81ef8c9e6cc1839
        self.env.cr.execute("DELETE FROM dtm_materiales_laser WHERE material_id = "+str(material_id))

        get_material = self.env['dtm.materiales'].search([("id","=",material_id)])

<<<<<<< HEAD
        print(get_material)

=======
>>>>>>> a3ef8156c324f80ea25b553eb81ef8c9e6cc1839
        list_material =  '{} - CALIBRE: {} LARGO:  {} ANCHO: {} '.format(get_material.material_id.nombre,
                                                                         get_material.calibre_id.calibre,
                                                                         get_material.largo_id.largo,
                                                                         get_material.ancho_id.ancho)

<<<<<<< HEAD
        print(list_material)

        self.env.cr.execute("INSERT INTO dtm_diseno_realizados (drawingname, sheets, material_id)" +
                            "VALUES ('"+drawingname+"', '"+sheets+"', '"+list_material+"');")

=======
        # print(list_material)
        # Pasa la orden de pendientes a realizados en el modulo de dtm_diseno de Diseño a Realizados
        self.env.cr.execute("INSERT INTO dtm_diseno_realizados (drawingname, sheets, material_id)" +
                            "VALUES ('"+drawingname+"', '"+sheets+"', '"+list_material+"');")
        # Retira las ordenes ya cortadas de Diseño
>>>>>>> a3ef8156c324f80ea25b553eb81ef8c9e6cc1839
        self.env.cr.execute("DELETE FROM dtm_diseno WHERE drawingname = '"+drawingname+"'")
>>>>>>> 08d5accf4ec8b4c17048ef97325a79f52aa4fae5


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


<<<<<<< HEAD
class Realizados(models.Model):
=======
class Realizados(models.Model): #--------------Muestra los trabajos ya realizados---------------------
>>>>>>> a3ef8156c324f80ea25b553eb81ef8c9e6cc1839
    _name = "dtm.laser.realizados"
    _description = "Lleva el listado de todo el material cortado en la Laser"

    orden_trabajo = fields.Integer(string="Orden de Trabajo")
    fecha_entrada = fields.Date(string="Fecha de Término")
    nombre_orden = fields.Char(string="Nombre")
    cortadora_id = fields.Many2many("dtm.documentos.cortadora" , readonly = True)



