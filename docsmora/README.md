# docsmora — Carpetas de ejecución

Estructura por **año / fecha de corte / lote**:

```
docsmora/
└── 2026/
    └── 05052026/              # Fecha de corte (MMDDYYYY = mes-día-año)
        └── cartera05052026b/  # Lote de cartera
            ├── camorosico_05052026_2341_of_0.lis
            └── cadetacaco_cobra05052026_0148_of_0.lis
```

## Ejecutar (rutas automáticas)

En `.env`:

```env
DOCSMORA_DIR=docsmora
DESTINO_DIR=destino
USAR_RUTAS_AUTOMATICAS=true
```

El job busca **la fecha de hoy** en formato **MMDDYYYY** (ej. `05052026` = 5 de mayo de 2026):

```
docsmora/2026/05052026/cartera05052026b/
  camorosico_05052026_....lis
  cadetacaco_cobra05052026_....lis
```

Salidas en `destino/2026/05052026/cartera05052026b/`.

Para otra fecha: `FECHA_CORTE=05052026` o en API `{"fecha": "2026-05-05"}`.

```bash
python main.py
```

Coloca aquí los archivos exportados del core (TAB) antes de cada corrida.
