# Sistema de Boletería en Django

### _Estrusturas de carpetas_
```
├── .gitignore
├── README.md
├── boleteria_site
    ├── __init__.py
    ├── asgi.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py
├── boletos
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── migrations
    │   ├── 0001_initial.py
    │   ├── 0002_rename_boletos_boleto.py
    │   ├── 0003_bus_boleto_bus.py
    │   ├── 0004_boleto_asiento_bus_capacidad.py
    │   └── __init__.py
    ├── models.py
    ├── templates
    │   └── boletos
    │   │   ├── base.html
    │   │   ├── buscar_boletos.html
    │   │   ├── comprobante_pdf.html
    │   │   ├── crear_boleto.html
    │   │   ├── detalle_boleto.html
    │   │   ├── editar_boleto.html
    │   │   ├── eliminar_boleto.html
    │   │   ├── filtro_fecha.html
    │   │   ├── listar_boletos.html
    │   │   ├── login.html
    │   │   └── registro.html
    ├── tests.py
    ├── urls.py
    └── views.py
├── manage.py
└── requirements.txt

```

