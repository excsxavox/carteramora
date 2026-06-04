# docsmora — Carpetas de ejecución

Estructura por **año / fecha de corte / lote**:

```
docsmora/
└── 2026/
    └── 05042026/              # Fecha de corte (DDMMYYYY)
        └── cartera05042026b/  # Lote de cartera
            ├── camorosico_06032026_0047_of_0.lis      (cuadro morosidad)
            └── cadetacaco_cie06032026_0233_of_0.lis   (reporte detallado cartera)
```

## Ejecutar con esta carpeta

En `.env`:

```env
ARCHIVO_MOROSIDAD=docsmora/2026/05042026/cartera05042026b/camorosico_06032026_0047_of_0.lis
ARCHIVO_CARTERA=docsmora/2026/05042026/cartera05042026b/cadetacaco_cie06032026_0233_of_0.lis
ARCHIVO_SALIDA=destino/2026/05042026/cartera05042026b/reporte_mora.json
```

```bash
python main.py
```

Coloca aquí los archivos exportados del core (TAB) antes de cada corrida.
