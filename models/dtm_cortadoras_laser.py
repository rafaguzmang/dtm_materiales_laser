from odoo import fields, models, api
from datetime import date,datetime
from odoo.exceptions import ValidationError


class CortadoraLaser(models.Model):
    _name = "dtm.cortadora.laser"
    _description = "Modelo para visualizar las ordenes diarias"
    _rec_name = "nombre"
    _order = 'fecha_corte desc, priority desc'

    orden_trabajo = fields.Integer(string='Orden')
    documentos = fields.Binary()
    nombre = fields.Char()
    lamina = fields.Char(string='Lámina',readonly=True)
    cantidad = fields.Integer(string='Cantidad',readonly=True)
    cortadora = fields.Char(string="Máquina",readonly=True)
    cortado = fields.Boolean(string="Terminado",readonly=True)
    contador = fields.Integer(readonly=True)
    timer = fields.Datetime()
    start = fields.Boolean()
    # Campos many
    tiempos_id = fields.One2many('dtm.documentos.tiempos', 'model_id', readonly=True)

    status_bar = fields.Float(string='%', compute='_compute_status')
    porcentaje = fields.Float()
    status = fields.Char(string='Status', readonly=True)
    tiempo_total = fields.Float(string="Tiempo", compute="_compute_tiempo_total", readonly=True)

    tiempo_teorico = fields.Float(string="T/Est", readonly=True)
    priority = fields.Selection([
        ('0', 'Muy baja'),
        ('1', 'Baja'),
        ('2', 'Media'),
        ('3', 'Alta'),
        ('4', 'Muy alta'),
    ], string="Prioridad",readonly=True)

    usuario = fields.Char()
    permiso = fields.Boolean(compute="_compute_permiso")
    fecha_corte = fields.Date()

    def _compute_tiempo_total(self):
        for record in self:
            get_laser = self.env['dtm.documentos.cortadora'].search([('nombre','=',record.nombre)],limit=1)
            print(get_laser.tiempos_id)
            record.tiempo_total = sum(get_laser.tiempos_id.mapped('tiempo'))

    def _compute_permiso(self):
        for record in self:
            record.usuario = self.env.user.partner_id.email
            record.permiso =  record.usuario in ["rafaguzmang@hotmail.com", "calidad2@dtmindustry.com"]

    def _compute_status(self):
        for record in self:
            if record.cantidad > 0:
                record.status_bar = max((record.contador * 100) / record.cantidad, 0)
                record.porcentaje = max((record.contador * 100) / record.cantidad, 0)
            else:
                record.status_bar = 0
                record.porcentaje = 0

    def action_inicio(self):
        get_corte = self.env['dtm.cortadora.laser'].search([('start','=',True)])

        if self.cortadora in get_corte.mapped('cortadora'):
            raise ValidationError(f"Ya existe otra orden con play para la cortadora {self.cortadora}")


        self.start = True
        self.timer = datetime.today()
        self.status = 'En Proceso'

    def action_stop(self):
        self.start = False
        get_laser = self.env['dtm.documentos.cortadora'].search([('nombre','=',self.nombre)],limit=1)
        if get_laser:
            get_laser.tiempos_id.create({
                'model_id': get_laser.id,
                'contador': self.contador,
                'tiempo': round((datetime.today() - self.timer).total_seconds() / 60.0, 4)
            })
        self.status = 'Pausado'

    def action_mas(self):
        get_laser = self.env['dtm.documentos.cortadora'].search([('nombre', '=', self.nombre)], limit=1)
        self.contador += 1
        get_laser.write({'contador':1})
        if self.contador >= self.cantidad:
            self.contador = self.cantidad
            self.cortado = True
            self.status = 'Terminado'
            get_laser.write({
                'contador':self.contador,
                'cortado':self.cortado,
                'status':self.status,
            })
            self.action_stop()
            self.unlink()

    def action_menos(self):
        self.contador -= 1
        self.contador = max(self.contador, 0)
        get_laser = self.env['dtm.documentos.cortadora'].search([('nombre', '=', self.nombre)], limit=1)
        get_laser.write({
            'contador': self.contador,
            'cortado': max(self.contador, 0),
            'status': self.status,
        })

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(CortadoraLaser, self).get_view(view_id, view_type, **options)

        get_cortes = self.env['dtm.documentos.cortadora'].search([('fecha_corte','!=',False),('cortado','!=',True)],order='create_date desc, priority desc')
        for nesteo in get_cortes:
            if nesteo.fecha_corte <= date.today():
                get_self = self.env['dtm.cortadora.laser'].search([('nombre','=',nesteo.nombre)],limit=1)
                vals = {
                            'orden_trabajo':nesteo.model_id.orden_trabajo,
                            'documentos': nesteo.documentos,
                            'nombre': nesteo.nombre,
                            'lamina': nesteo.lamina,
                            'cantidad': nesteo.cantidad,
                            'cortadora': nesteo.cortadora,
                            'priority': nesteo.priority,
                            'fecha_corte':nesteo.fecha_corte,
                            'tiempo_teorico':nesteo.tiempo_teorico
                        }
                get_self.write(vals) if get_self else get_self.create(vals)

        get_self = self.env['dtm.cortadora.laser'].search([])
        for nesteo in get_self:
            get_cortes = self.env['dtm.documentos.cortadora'].search([('model_id.orden_trabajo','=',nesteo.orden_trabajo),('nombre','=',nesteo.nombre)],limit=1)
            if not get_cortes.fecha_corte:
                nesteo.unlink()




        return res



