from odoo import http
from odoo.http import request
from datetime import datetime
import json

class MaterialesLaserController(http.Controller):

    @http.route('/cama_corte_carga', type='json', auth='public', csrf=False)
    def materiales_laser(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        index = data.get('index')
        maquina = data.get('maquina')
        archivo = data.get('archivo')
        # Buscar el material
        get_material = request.env['dtm.materiales'].sudo().search([('id', '=', codigo),('nombre','ilike','Lámina')], limit=1) 
        
        if get_material:
            # Buscar si esta asociado a una orden de trabajo
            get_listado = request.env['dtm.cortadora.laser'].sudo().search([])
            get_listado = request.env['dtm.cortadora.laser'].sudo().search([('lamina','ilike',f"{codigo} -"),('nombre','=',archivo)]) if archivo else request.env['dtm.cortadora.laser'].sudo().search([('lamina','ilike',f"{codigo} -")])
            request.env['dtm.cama.corte'].sudo().create({
                'codigo': codigo,
                'maquina': maquina,
                'index': index,
                'nombre': get_material.nombre,
                'medida': get_material.medida,
                'orden': get_listado.orden_trabajo if get_listado else None,
                'archivo': get_listado.nombre if get_listado else 'N/A',
                'cantidad': get_listado.cantidad if get_listado else 0,
                'contador': get_listado.contador if get_listado else 0,
            })
            if get_listado:
                return{
                    'codigo':codigo,
                    'nombre':get_material.nombre,
                    'medida':get_material.medida,
                    'orden':get_listado.orden_trabajo,
                    'archivo':get_listado.nombre,
                    'encontrado':True,
                    'cantidad':get_listado.cantidad,
                    'contador':get_listado.contador,
                }
            else:
                return {
                    'codigo':codigo,
                    'nombre':get_material.nombre,
                    'medida':get_material.medida,
                    'encontrado':False,
                    'cantidad':0,
                    'contador':0,
                }
        return {'error':f'El material {codigo} no es una lámina'}

    @http.route('/cama_corte_jfy', type='http', auth='public', csrf=False)
    def cama_corte(self):
        result = []
        get_cama_corte = request.env['dtm.cama.corte'].sudo().search([('maquina', '=', 'JFY')])
        for cama in get_cama_corte:
            result.append({
                'codigo':cama.codigo,
                'maquina':cama.maquina,
                'index':cama.index,
                'nombre':cama.nombre,
                'medida':cama.medida,
                'orden':cama.orden,
                'archivo':cama.archivo,
                'play':cama.play,
                'cantidad':cama.cantidad if cama.cantidad else 0,
                'contador':cama.contador if cama.contador else 0,
            })
        return (request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin':'*'
            }

        ))

    @http.route('/cama_corte_remueve', type='json', auth='public', csrf=False)
    def cama_corte_remueve(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        index = data.get('index')
        maquina = data.get('maquina')
        get_cama_corte = request.env['dtm.cama.corte'].sudo().search([('codigo', '=', codigo), ('index', '=', index), ('maquina', '=', maquina)], limit=1)
        if get_cama_corte:
            get_cama_corte.unlink()
            return {'success': True}
        return {'error': 'No se encontro el material'}

    @http.route('/cama_corte_play', type='json', auth='public', csrf=False)
    def cama_corte_play(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        index = data.get('index')
        maquina = data.get('maquina')
        get_cama_corte = request.env['dtm.cama.corte'].sudo().search([('codigo', '=', codigo), ('index', '=', index), ('maquina', '=', maquina)], limit=1)
        if get_cama_corte:
            get_cama_corte.write({
                'play': True,
                'tiempo_start': datetime.now(),
            })
            return {'success': True}
        return {'error': 'No se encontro el material'}

    @http.route('/cama_corte_stop', type='json', auth='public', csrf=False)
    def cama_corte_stop(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        index = data.get('index')
        maquina = data.get('maquina')
        get_cama_corte = request.env['dtm.cama.corte'].sudo().search([('codigo', '=', codigo), ('index', '=', index), ('maquina', '=', maquina)], limit=1)
        if get_cama_corte:
            get_cama_corte.write({
                'play': False,
                'tiempo': round((datetime.today() - get_cama_corte.tiempo_start).total_seconds() / 60.0, 4),
                })
            get_model_id = request.env['dtm.materiales.laser'].sudo().search([('orden_trabajo','=',get_cama_corte.orden)],limit=1)
            get_laser = request.env['dtm.documentos.cortadora'].sudo().search([('model_id','=',get_model_id.id),('nombre','=',get_cama_corte.archivo)],limit=1)
            if get_laser:
                # Pone el tiempo de corte entre un play y un stop
                get_laser.tiempos_id.create({
                    'model_id': get_laser.id,
                    'tiempo': round((datetime.today() - get_cama_corte.tiempo_start).total_seconds() / 60.0, 4)
                })
            else:
                request.env['dtm.documentos.tiempos'].sudo().create({
                    'codigo':codigo,
                    'tiempo': round((datetime.today() - get_cama_corte.tiempo_start).total_seconds() / 60.0, 4)
                })
            return {'success': True}
        return {'error': 'No se encontro el material'}
    # Endpoint para agregar un material cortado
    @http.route('/cama_corte_add_contador', type='json', auth='public', csrf=False)
    def cama_corte_add_contador(self):
        raw = request.httprequest.data
        data = json.loads(raw)
        codigo = data.get('codigo')
        index = data.get('index')
        maquina = data.get('maquina')
        nombre = data.get('nombre')
        cantidad = data.get('cantidad')
        cortadora = 'BFC6025' if maquina == 'JFY' else None
       
        #Busca dentro del modelo donde están los cortes a realizarse
        get_cama_corte = request.env['dtm.cama.corte'].sudo().search([('codigo', '=', codigo), ('index', '=', index), ('maquina', '=', maquina)], limit=1)
        if get_cama_corte.contador + 1 >= get_cama_corte.cantidad:
            #Indica a almacen las láminas que ya fueron cortadas
            request.env['dtm.control.laminas'].sudo().create({'lamina':f"{codigo} - {nombre}","cantidad":cantidad if cantidad else 1})
            get_cama_corte.write({
                'play': False,
                'cortado': True,
                })
            # Busca el id del orden de trabajo
            get_model_id = request.env['dtm.materiales.laser'].sudo().search([('orden_trabajo','=',get_cama_corte.orden)],limit=1)
            # Busca el corte en el programa de corte
            get_laser = request.env['dtm.documentos.cortadora'].sudo().search([('model_id','=',get_model_id.id),('nombre','=',get_cama_corte.archivo)],limit=1)            
            if get_laser:
                get_laser.write({
                    'contador':get_laser.contador + 1,
                    'cortado':True,
                    'status':'Terminado',
                    'start':False,
                    # 'porcentaje': 100
                })
                # Pone el tiempo de corte entre un play y un stop
                get_laser.tiempos_id.create({
                    'model_id': get_laser.id,
                    'contador':get_laser.contador,
                    'tiempo': round((datetime.today() - get_cama_corte.tiempo_start).total_seconds() / 60.0, 4)
                })   
                get_programa = request.env['dtm.cortadora.laser'].sudo().search([('orden_trabajo','=',get_cama_corte.orden),('nombre','=',get_cama_corte.archivo),('lamina','ilike',codigo),('cortadora','=',cortadora)],limit=1)
                get_programa.unlink() if get_programa else None
            else:# Lámina sin orden de trabajo
                # Pone el tiempo de corte en el modelo dtm.documentos.tiempos para llevar el registro de los tiempos de corte
                request.env['dtm.documentos.tiempos'].sudo().create({
                    'codigo':codigo,
                    'tiempo': round((datetime.today() - get_cama_corte.tiempo_start).total_seconds() / 60.0, 4)
                })
            get_cama_corte.unlink()
            return {'cortado': True}
        if get_cama_corte:
            get_cama_corte.write({
                'contador': get_cama_corte.contador + 1,
            })
            return {'success': True}
        return {'error': 'No se encontro el material'}
    # Obtiene los cortes programados del día
    @http.route('/dtm_corte_laser', type='http', auth='public', csrf=False)
    def get_trabajos(self):

        get_corte_laser = request.env['dtm.documentos.cortadora'].sudo().search([('fecha_corte','!=',False),('cortado','!=',True),('cortadora','=','BFC6025')],order='create_date desc, priority desc')
        result = [
            {
                'orden_trabajo':corte.model_id.orden_trabajo,  # Orden de trabajo
                'documentos': corte.documentos.decode('utf-8') if corte.documentos else False,  # Documentos
                'nombre': corte.nombre,  # Nombre
                'lamina': corte.lamina,  # Lámina
                'cantidad': corte.cantidad,  # Cantidad
                'contador':corte.contador,  # Contador
                'cortadora': corte.cortadora,  # Cortadora
                'priority': corte.priority,  # Prioridad
                'fecha_corte':corte.fecha_corte.strftime('%Y-%m-%d') if corte.fecha_corte else False,  # Fecha de corte
                'tiempo_teorico':corte.tiempo_teorico  # T  iempo teórico
            }
            for corte in get_corte_laser
        ]
        
        return (request.make_response(
            json.dumps(result),
            headers={
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            }
        ))
