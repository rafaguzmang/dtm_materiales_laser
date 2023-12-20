from odoo import api,models,fields


class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"

    material = fields.Char(string="MATERIAL", readonly=True)
    calibre = fields.Char(string="CALIBRE", readonly=True)
    largo = fields.Char(string="LARGO", default="0", readonly=True)
    ancho = fields.Char(string="ANCHO", default="0", readonly=True)
    cantidad = fields.Integer(string="CANTIDAD", readonly=True)


    #--------------------  Llena la tabla con las ordenes de servicio ----------------

    def acction_less(self):
        cantidad = self.cantidad - 1
        if cantidad <= 0:
            cantidad = "0"


        self.env.cr.execute("UPDATE dtm_materiales SET cantidad = "+str(cantidad)+" WHERE id = "+str(self.id))
        self.cantidad = cantidad


    def get_view(self, view_id=None, view_type='form', **options):
        res = super(MaterialesLasser,self).get_view(view_id, view_type)

        get_info = self.env['dtm.materiales'].search([])
        self.env.cr.execute("DELETE FROM dtm_materiales_laser")

        for result in get_info:
            material = result.material_id.nombre
            calibre = result.calibre_id.calibre
            largo = result.largo_id.largo
            ancho = result.ancho_id.ancho 
            cantidad = str(result.cantidad)  
            id = str(result.id)          
            self.env.cr.execute("INSERT INTO dtm_materiales_laser (id, material, calibre, largo, ancho, cantidad)"+
                         " VALUES ("+id+", '"+material +"','"+ calibre +"','"+ largo +"','"+ ancho +"',"+cantidad+")")  
        return res