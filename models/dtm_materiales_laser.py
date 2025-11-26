from odoo import api,models,fields
from datetime import datetime
from odoo.exceptions import ValidationError

class MaterialesLasser(models.Model):
    _name = "dtm.materiales.laser"
    _description = "Lleva el listado de los materiales a cortar en la laser"
    _rec_name = "orden_trabajo"

    orden_trabajo = fields.Integer(string="Orden de Trabajo", readonly=True)
    fecha_entrada = fields.Date(string="Fecha de Entrada", readonly=True)
    nombre_orden = fields.Char(string="Nombre", readonly=True)
    cortadora_id = fields.One2many("dtm.documentos.cortadora","model_id" , readonly=False)
    tipo_orden = fields.Char(string="Tipo", readonly=True)
    revision_ot = fields.Integer(string="VERSIÓN",readonly=True) # Esto es versión
    primera_pieza = fields.Boolean(string="Primera Pieza", readonly = True)
    finalizado = fields.Boolean(compute='_compute_finalizado')
    status = fields.Float(string="Status", compute="_compute_status")
    tiempo_teorico = fields.Float(string="Tiempo Estimado", readonly = True,compute="_compute_tiempo_teorico")
    priority = fields.Selection([
        ('0', 'Muy baja'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy alta'),
    ], string="Prioridad")
    usuario  = fields.Char()
    permiso = fields.Boolean(compute="_compute_permiso")
    # Campo para saber que orden está en corte
    en_corte = fields.Boolean()

    def _compute_tiempo_teorico(self):
        for record in self:
            record.tiempo_teorico = sum(record.cortadora_id.mapped("tiempo_teorico"))

    def _compute_permiso(self):
        for record in self:
            record.usuario = self.env.user.partner_id.email
            record.permiso = False
            if record.usuario in ["rafaguzmang@hotmail.com","calidad2@dtmindustry.com"]:
                record.permiso = True

    def _compute_status(self):
        for record in self:
            nesteos = record.cortadora_id.mapped('status_bar')
            total_nesteos = len(nesteos)
            porcentajes = sum(nesteos)
            record.status = 0
            if total_nesteos > 0:
                record.status = porcentajes/total_nesteos

    def _compute_finalizado(self):
        for record in self:
            record.finalizado = False if False in record.cortadora_id.mapped('cortado') else True

    def action_inicio_corte(self):
        if not self.start:
            self.inicio_corte = datetime.today()
            self.start = True

    def action_finalizar(self):#Quita la orden de pendientes por corte a cortes realizados

        if False in self.cortadora_id.mapped('cortado'): #Revisa que todos los archivos esten cortados para poder pasarlos al modulo de realizados
            raise ValidationError("Todos los nesteos deben estar cortados")
        else:
            vals = {
                "orden_trabajo": self.orden_trabajo,
                "tipo_orden":self.tipo_orden,
                "revision_ot":self.revision_ot,
                "fecha_entrada": datetime.today(),
                "nombre_orden": self.nombre_orden,
                "primera_pieza":self.primera_pieza
            }
            get_realizado = self.env['dtm.laser.realizados'].search([
                ('orden_trabajo','=',self.orden_trabajo),
                ('tipo_orden','=',self.tipo_orden),
                ('revision_ot','=',self.revision_ot),
                ('primera_pieza','=',self.primera_pieza)])
            if get_realizado:
                get_realizado.write(vals)
            else:
                get_realizado = self.env['dtm.laser.realizados'].create(vals)

            for corte in self.cortadora_id:
                vals = {
                    'model_id':get_realizado.id,
                    'documentos':corte.documentos,
                    'nombre':corte.nombre,
                    'lamina':corte.lamina,
                    'cantidad':corte.cantidad,
                    'cortadora':corte.cortadora,
                    'cortado':corte.cortado,
                    'contador':corte.contador,
                }
                get_doc = self.env['dtm.documentos.finalizados'].search([
                    ('model_id','=',get_realizado.id),
                    ('nombre','=',corte.nombre),
                    ('lamina','=',corte.lamina)
                ],limit=1)
                if get_doc:
                    get_doc.write(vals)
                else:
                    get_doc = self.env['dtm.documentos.finalizados'].create(vals)

                [tiempo.write({'model_id':None,'model_id2':get_doc.id})for tiempo in corte.tiempos_id]

            self.cortadora_id.unlink()
            self.unlink()

        return self.env.ref('dtm_materiales_laser.dtm_materiales_laser_accion').read()[0]

    # def get_view(self, view_id=None, view_type='form', **options):
    #     res = super(MaterialesLasser,self).get_view(view_id, view_type,**options)
    #
    #     get_self = self.env['dtm.materiales.laser'].search([])
    #     for record in get_self:
    #         record.en_corte = False
    #         if True in record.cortadora_id.mapped("start"):
    #             record.en_corte = True
    #
    #
    #
    #     return res

class Realizados(models.Model): #--------------Muestra los trabajos ya realizados---------------------
    _name = "dtm.laser.realizados"
    _description = "Lleva el listado de todo el material cortado en la Laser"
    _order = "orden_trabajo desc"
    _rec_name = "orden_trabajo"

    orden_trabajo = fields.Integer(string="Orden de Trabajo",readonly=True)
    tipo_orden = fields.Char(string="Tipo", readonly=True)
    revision_ot = fields.Integer(string="VERSIÓN",readonly=True) # Esto es versión
    fecha_entrada = fields.Date(string="Fecha de Término",readonly=True)
    nombre_orden = fields.Char(string="Nombre",readonly=True)
    cortadora_id = fields.One2many("dtm.documentos.finalizados","model_id" , readonly = True)
    primera_pieza = fields.Boolean(string="Primera Pieza",readonly=True)

class Documentos(models.Model):
    _name = "dtm.documentos.cortadora"
    _description = "Guarda los nesteos del Radán"

    model_id = fields.Many2one('dtm.materiales.laser')
    documentos = fields.Binary(readonly=True)
    nombre = fields.Char()
    lamina = fields.Char(string='Lámina')
    cantidad = fields.Integer(string='Cantidad')
    cortadora = fields.Char(string = "Máquina")
    cortado = fields.Boolean(string="Terminado")
    contador = fields.Integer()
    timer = fields.Datetime()
    start = fields.Boolean()
    # Campos many
    tiempos_id = fields.One2many('dtm.documentos.tiempos','model_id',readonly=True)

    status_bar = fields.Float(string='%',compute='_compute_status')
    porcentaje = fields.Float()
    status = fields.Char(string='Status',readonly=True)
    tiempo_total = fields.Float(string="Tiempo",compute="_compute_tiempo_total",readonly=True)

    tiempo_teorico = fields.Float(string="T/Est", readonly=True)
    priority = fields.Selection([
        ('0', 'Muy baja'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy alta'),
    ], string="Prioridad")
    fecha_corte = fields.Date(string='F.Corte',readonly=False)

    usuario = fields.Char()
    permiso = fields.Boolean(compute="_compute_permiso")

    def _compute_permiso(self):
        for record in self:
            record.usuario = self.env.user.partner_id.email
            record.permiso = False
            if record.usuario in ["rafaguzmang@hotmail.com", "calidad2@dtmindustry.com"]:
                record.permiso = True

    def _compute_tiempo_total(self):
        for record in self:
            record.tiempo_total = sum(record.tiempos_id.mapped('tiempo'))

    def _compute_status(self):
        for record in self:
            if record.cantidad > 0:
                record.status_bar = max((record.contador * 100)/record.cantidad,0)
                record.porcentaje = max((record.contador * 100)/record.cantidad,0)
            else:
                record.status_bar = 0
                record.porcentaje = 0

    def action_inicio(self):
            get_corte = self.env['dtm.materiales.laser'].search([])
            for record in get_corte:
                if True in record.cortadora_id.mapped('start'):
                    for result in record.cortadora_id.ids:
                        if self.cortadora == self.env['dtm.documentos.cortadora'].browse(result).cortadora and self.env['dtm.documentos.cortadora'].browse(result).start:
                            documento = self.env['dtm.documentos.cortadora'].browse(result).nombre
                            orden = self.env['dtm.documentos.cortadora'].browse(result).model_id.orden_trabajo
                            raise ValidationError(f"Cortadora {self.cortadora}:\n Documento {documento} de la Orden {orden} esta en corte ")

            self.start = True
            self.timer = datetime.today()
            self.status = 'En Proceso'

    def action_stop(self):
        self.start = False
        self.tiempos_id.create({
            'model_id':self.id,
            'contador':self.contador,
            'tiempo':round((datetime.today() - self.timer ).total_seconds() / 60.0,4)
        })
        self.status = 'Pausado'

    def action_mas(self):
        self.contador += 1
        if self.contador >= self.cantidad:
            self.contador = self.cantidad
            self.cortado = True
            self.action_stop()
            self.status = 'Terminado'

    def action_menos(self):
        self.contador -= 1
        self.contador = max(self.contador,0)


    @api.onchange("cortado")
    def _action_cortado (self):
            get_procesos = self.env['dtm.proceso'].search([('ot_number','=',self.model_id.orden_trabajo)])
            # print(get_procesos)
            # get_procesos.

class Finalizados(models.Model):
    _name = "dtm.documentos.finalizados"
    _description = "Modelo para guardar los archivos ya cortados"


    model_id = fields.Many2one('dtm.laser.realizados')
    documentos = fields.Binary()
    nombre = fields.Char()
    lamina = fields.Char(string='Lámina')
    cantidad = fields.Integer(string='Cantidad')
    cortadora = fields.Char(string="Máquina")
    tiempos_id = fields.One2many('dtm.documentos.tiempos', 'model_id2')
    cortado = fields.Boolean()
    contador = fields.Integer()

class Tiempos(models.Model):
    _name = "dtm.documentos.tiempos"
    _description = "Modelo para llevar el tiempo del trabajo de las máquinas laser"
    _order = "id desc"
    model_id = fields.Many2one('dtm.documentos.cortadora')
    model_id2 = fields.Many2one('dtm.documentos.finalizados')

    contador = fields.Integer(string='Número de láminas', readonly=True)
    tiempo = fields.Float(string='Duración', readonly=True)



