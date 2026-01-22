from odoo import api,models,fields
from datetime import datetime
from odoo.exceptions import ValidationError
import base64
import logging

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
    usuario  = fields.Char()
    permiso = fields.Boolean(compute="_compute_permiso")
    # Campo para saber que orden está en corte
    en_corte = fields.Boolean()

    def write(self, vals):

        res = super(MaterialesLasser, self).write(vals)
        self.env['bus.bus']._sendone(
            'canal_corte',  # Nombre del canal
            'corte_laser',
            {'mensaje': 'Actualiza Corte Laser'}  # json con la información
        )
        return res

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

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(MaterialesLasser, self).get_view(view_id, view_type, **options)

        get_self = self.env['dtm.materiales.laser'].search([])
        for record in get_self:
            # Pone los estados (play) en falso
            record.en_corte = False
            if True in record.cortadora_id.mapped("start"):
                record.en_corte = True

            if all(record.cortadora_id.mapped('cortado')):
                vals = {
                    "orden_trabajo": record.orden_trabajo,
                    "tipo_orden": record.tipo_orden,
                    "revision_ot": record.revision_ot,
                    "fecha_entrada": datetime.today(),
                    "nombre_orden": record.nombre_orden,
                    "primera_pieza": record.primera_pieza
                }
                get_realizado = self.env['dtm.laser.realizados'].search([
                    ('orden_trabajo', '=', record.orden_trabajo),
                    ('tipo_orden', '=', record.tipo_orden),
                    ('revision_ot', '=', record.revision_ot),
                    ('primera_pieza', '=', record.primera_pieza)])
                if get_realizado:
                    get_realizado.write(vals)
                else:
                    get_realizado = self.env['dtm.laser.realizados'].create(vals)

                for corte in record.cortadora_id:
                    vals = {
                        'model_id': get_realizado.id,
                        'documentos': corte.documentos,
                        'nombre': corte.nombre,
                        'lamina': corte.lamina,
                        'cantidad': corte.cantidad,
                        'cortadora': corte.cortadora,
                        'cortado': corte.cortado,
                        'contador': corte.contador,
                    }
                    get_doc = self.env['dtm.documentos.finalizados'].search([
                        ('model_id', '=', get_realizado.id),
                        ('nombre', '=', corte.nombre),
                        ('lamina', '=', corte.lamina)
                    ], limit=1)
                    if get_doc:
                        get_doc.write(vals)
                    else:
                        get_doc = self.env['dtm.documentos.finalizados'].create(vals)
                    # Pasa los tiempos a finalizado
                    [tiempo.write({'model_id': None, 'model_id2': get_doc.id}) for tiempo in corte.tiempos_id]

                record.cortadora_id.unlink()
                record.unlink()

            # Borra ordenes vacías
            if not record.cortadora_id:
                record.unlink()
        return res

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
    documentos = fields.Binary()
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

    status_bar = fields.Float(string='%', compute='_compute_status', readonly=True)
    porcentaje = fields.Float()
    status = fields.Char(string='Status',readonly=True)
    tiempo_total = fields.Float(string="Tiempo",readonly=True,compute='_compute_tiempo_total')

    tiempo_teorico = fields.Float(string="T/Est", readonly=True)
    priority = fields.Selection([
        ('0', 'Muy baja'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy alta'),
    ], string="Prioridad")
    fecha_corte = fields.Date(string='F.Corte')

    usuario = fields.Char()
    permiso = fields.Boolean(compute="_compute_permiso")



    def write(self,vals):
        res = super().write(vals)
        # for rec in self:
        #     if 'priority' in vals:
        #         rec.env['bus.bus'].sendone(
        #             (self.env.user.partner_id, 'cortadora_channel'),
        #             {
        #                 'id':rec.id,
        #                 'cortadora':rec.cortadora,
        #                 'priority':rec.priority,
        #                 'status':rec.status
        #             }
        #         )
        # for rec in self:
        #     if rec.fecha_corte and rec.priority and rec.priority != '0':
        #         cortadora = self.env['dtm.cortadora.laser'].search([('nombre', '=', rec.nombre)], limit=1)
        #         doc = rec.documentos
        #         if isinstance(doc, (bytes, bytearray)):
        #             doc = base64.b64encode(doc).decode()
        #         vals_copy = {
        #             'documentos': doc,
        #             'nombre': rec.nombre,
        #             'lamina': rec.lamina,
        #             'cantidad': rec.cantidad,
        #             'cortadora': rec.cortadora,
        #             'priority': rec.priority,
        #         }
        #         if cortadora:
        #             cortadora.write(vals_copy)
        #         else:
        #             self.env['dtm.cortadora.laser'].create(vals_copy)
        return res

    def _compute_permiso(self):
        for record in self:
            record.usuario = self.env.user.partner_id.email
            record.permiso = False
            if record.usuario in ["rafaguzmang@hotmail.com", "calidad2@dtmindustry.com"]:
                record.permiso = True

    def _compute_status(self):
        for record in self:
            if record.cantidad > 0:
                record.status_bar = max((record.contador * 100) / record.cantidad, 0)
                record.porcentaje = max((record.contador * 100) / record.cantidad, 0)
            else:
                record.status_bar = 0
                record.porcentaje = 0

    def _compute_tiempo_total(self):
        for record in self:
            get_laser = self.env['dtm.documentos.cortadora'].search([('nombre', '=', record.nombre)], limit=1)
            record.tiempo_total = sum(get_laser.tiempos_id.mapped('tiempo'))




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



