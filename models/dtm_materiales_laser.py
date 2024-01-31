from odoo import api,models,fields


class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"
    _description = "Lleva el listado de los materiales a cortar en la laser"

    material = fields.Char(string="MATERIAL", readonly=True)
    calibre = fields.Char(string="CALIBRE", readonly=True)
    largo = fields.Char(string="LARGO", readonly=True)
    ancho = fields.Char(string="ANCHO", readonly=True)
    sheets = fields.Char(string="SHEETS", readonly=True)
    drawingname  = fields.Char(string="DRAWINGNAME", readonly=True)
    material_id = fields.Integer()

    #--------------------  Llena la tabla con las ordenes de servicio ----------------

    def acction_less(self):
        get_cantidad = self.env["dtm.materiales"].browse(self.material_id)
        cantidad = get_cantidad.cantidad - int(self.sheets)

        material = self.material
        calibre = self.calibre
        largo = self.largo
        ancho = self.ancho
        sheets = self.sheets
        drawingname = self.drawingname
        material_id = str(self.material_id)

        self.env.cr.execute("UPDATE dtm_materiales SET cantidad = "+str(cantidad)+" WHERE id = "+str(self.material_id))

        self.env.cr.execute("INSERT INTO dtm_laser_realizados (material, calibre, largo, ancho, sheets, drawingname, material_id)" +
                            "VALUES ('"+material+"', '"+calibre+"', '"+largo+"', '"+ancho+"', '"+sheets+"', '"+drawingname+"', "+material_id+");")

        self.env.cr.execute("DELETE FROM dtm_materiales_laser WHERE material_id = "+str(material_id))

        get_material = self.env['dtm.materiales'].search([("id","=",material_id)])

        print(get_material)

        list_material =  '{} - CALIBRE: {} LARGO:  {} ANCHO: {} '.format(get_material.material_id.nombre,
                                                                         get_material.calibre_id.calibre,
                                                                         get_material.largo_id.largo,
                                                                         get_material.ancho_id.ancho)

        print(list_material)

        self.env.cr.execute("INSERT INTO dtm_diseno_realizados (drawingname, sheets, material_id)" +
                            "VALUES ('"+drawingname+"', '"+sheets+"', '"+list_material+"');")

        self.env.cr.execute("DELETE FROM dtm_diseno WHERE drawingname = '"+drawingname+"'")



    def get_view(self, view_id=None, view_type='form', **options):#-----------------Llena la tabla dtm_materiales_laser con los nesteos programados por diseño----------
        res = super(MaterialesLasser,self).get_view(view_id, view_type)

        get_info = self.env['dtm.diseno'].search([])
        self.env.cr.execute("DELETE FROM dtm_materiales_laser ")
        cont = 0;

        for result in get_info:
            print(result.material_id.id)
            material = str(result.material_id.material_id.nombre)
            calibre = str(result.material_id.calibre_id.calibre)
            largo = str(result.material_id.largo_id.largo)
            ancho = str(result.material_id.ancho_id.ancho)
            sheets = str(result.sheets)
            drawingname = str(result.drawingname)
            material_id = str(result.material_id.id)
            cont += 1
            self.env.cr.execute("INSERT INTO dtm_materiales_laser ( id, material, calibre, largo, ancho, sheets, drawingname, material_id) " +
                                "VALUES("+str(cont)+",'"+material+"', '"+calibre+"','"+largo+"','"+ancho+"','"+sheets+"','"+drawingname+"', "+ material_id +")")

        return res

class Realizados(models.Model):
    _name = "dtm.laser.realizados"
    _description = "Lleva el listado de todo el material cortado en la Laser"

    material = fields.Char(string="MATERIAL", readonly=True)
    calibre = fields.Char(string="CALIBRE", readonly=True)
    largo = fields.Char(string="LARGO", readonly=True)
    ancho = fields.Char(string="ANCHO", readonly=True)
    sheets = fields.Char(string="SHEETS", readonly=True)
    drawingname  = fields.Char(string="DRAWINGNAME", readonly=True)
    material_id = fields.Integer()
