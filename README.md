# EV3 — Requerimientos de Hardware para Juegos de PC

Herramienta de análisis que cruza tres fuentes de datos para ayudar a jugadores de PC a saber **qué componentes necesitan actualizar** para correr un juego y **cuánto les costaría hacerlo**.

---

## ¿Qué hace?

1. **Requisitos de juegos** — Dataset de Kaggle con los requisitos mínimos y recomendados de más de 80,000 juegos de Steam.
2. **Popularidad de componentes** — Datos históricos de la [Steam Hardware Survey](https://store.steampowered.com/hwsurvey/) para identificar qué GPU, CPU y RAM usan realmente los jugadores de Windows y Linux.
3. **Precios en tiempo real** — Integración con [PCPartPicker](https://pcpartpicker.com/) vía `PyPartPicker` para obtener el costo actual de actualizar cada componente.

El resultado: dado un juego y las especificaciones actuales del usuario, el sistema indica qué piezas no cumplen los requisitos y cuánto costaría reemplazarlas hoy.

---

## Estructura del proyecto

```
EV3/
├── filter_hardware.py          # Filtra la Steam HW Survey (elimina Mac, conserva Windows/Linux)
├── shs_filtered.csv            # Datos globales filtrados por categoría de hardware relevante
├── shs_platform_filtered.csv   # Datos por plataforma (pc + linux) filtrados
├── shs_latest.csv              # Snapshot del mes más reciente — datos globales
├── shs_platform_latest.csv     # Snapshot del mes más reciente — pc + linux
└── README.md
```

> **Nota:** Los CSVs raw de la Steam Hardware Survey (`shs_platform.csv`, `steamHWsurvey/`) no se incluyen en el repositorio por su tamaño. Se pueden regenerar con `filter_hardware.py` a partir del [dataset original de Kaggle](https://www.kaggle.com/datasets/jdegene/steamhardwaresurvey).

---

## Fuentes de datos

| Fuente | Descripción |
|---|---|
| [Kaggle — Steam Games Requirements](https://www.kaggle.com/) | Requisitos mínimos y recomendados de +80k juegos |
| [Steam Hardware Survey](https://store.steampowered.com/hwsurvey/) | Encuesta mensual de hardware de jugadores activos |
| [PCPartPicker](https://pcpartpicker.com/) | Precios en tiempo real de componentes de PC |

---

## Estado del proyecto

> 🚧 En desarrollo activo — los cambios se trabajan en la rama `dev`.
