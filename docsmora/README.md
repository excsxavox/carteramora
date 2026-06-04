# docsmora — Carpetas de ejecución

Estructura por **año / fecha de corte / lote**:

```
docsmora/
└── 2026/
    └── 05042026/              # Fecha de corte (DDMMYYYY)
        └── cartera05042026b/  # Lote de cartera
            ├── 01_cuadro_morosidad.txt
            └── 02_te_detallado_cartera.txt
```

## Ejecutar con esta carpeta

En `.env`:

```env
ARCHIVO_MOROSIDAD=docsmora/2026/05042026/cartera05042026b/01_cuadro_morosidad.txt
ARCHIVO_CARTERA=docsmora/2026/05042026/cartera05042026b/02_te_detallado_cartera.txt
ARCHIVO_SALIDA=destino/2026/05042026/cartera05042026b/reporte_mora.json
```

```bash
python main.py
```

Coloca aquí los archivos exportados del core (TAB) antes de cada corrida.
