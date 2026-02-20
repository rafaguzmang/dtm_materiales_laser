{
    "name":"Materiales Laser",

    'version': '1.0',
    'author': "Rafael Guzmán",
    "description": "Conteo de materiales de salida",
    "data":[        
        'security/ir.model.access.csv',
        # 'security/res_group.xml',
        # 'security/model_access.xml',
        'views/dtm_materiales_laser_views.xml',
        'views/dtm_laser_realizados_view.xml',
        'views/menu_item.xml',
        'views/dtm_cortadora_laser_view.xml',
        'views/dtm_owl_views.xml',
        'views/dtm_cama_corte_view.xml'
    ],
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'dtm_materiales_laser/static/src/js/cama_jfy.js',
            'dtm_materiales_laser/static/src/xml/cama_jfy.xml',
            'dtm_materiales_laser/static/src/css/cama_jfy.css',
            'dtm_materiales_laser/static/src/css/corte_laser.css',
            'dtm_materiales_laser/static/src/js/corte_laser.js',
            'dtm_materiales_laser/static/src/xml/corte_laser.xml',
        ],
    },
}

