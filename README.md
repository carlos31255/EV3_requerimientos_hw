# EV3 — Sistema Recomendador de Hardware para PC

Herramienta analítica y de inteligencia de mercado que cruza tres fuentes de datos clave para generar **recomendaciones de hardware** y configuraciones de PC (builds), analizando qué componentes se necesitan hoy, qué usa el mercado global y cuáles son los precios reales.

---

## 🎯 ¿Qué hace?

El sistema toma datos de 3 fuentes para alimentar una Base de Datos central y realizar un Análisis Exploratorio (EDA):

1. **Requisitos de la Industria (Kaggle)** — Requisitos de hardware de miles de juegos de Steam, lo que define la "demanda" técnica.
2. **Uso Real del Mercado (Steam HW Survey)** — Datos históricos que indican qué hardware usa la mayoría de los jugadores a nivel mundial.
3. **Precios en Vivo (eBay Browse API v1)** — Costo actual en el mercado para cada componente (convertido a CLP).

**El resultado:** Un motor de base de datos y EDA capaz de responder preguntas de mercado como *"¿Cuál es la GPU óptima para jugar eSports a 144fps bajo un presupuesto de 400.000 CLP?"* o *"¿Qué porcentaje de usuarios necesita actualizar su RAM para correr juegos del 2026?"*.

---

## 🏗️ Arquitectura y Estructura del Proyecto

El proyecto está dividido en distintas ramas de trabajo para cada etapa del pipeline:

- **ETL:** Limpieza, muestreo y filtrado de los datasets crudos.
- **API:** Conexión con eBay y transformación de precios a CLP.
- **Base de Datos:** Almacenamiento en MySQL de los datos procesados + datos propios del sistema (Tiers de rendimiento, perfiles objetivo como "1080p 60fps Alta").
- **EDA:** Análisis final cruzando la Base de Datos central.

---

## 📁 Fuentes de datos

| Fuente | Descripción |
|---|---|
| [Kaggle — PC Video Game Requirements](https://www.kaggle.com/datasets/baraazaid/pc-video-game-requirements) | Requisitos mínimos y recomendados de juegos en Steam |
| [jdegene/steamHWsurvey](https://github.com/jdegene/steamHWsurvey) | Datos históricos de la Steam Hardware Survey scrapeados y mantenidos por jdegene |
| [eBay Browse API v1](https://developer.ebay.com/api-docs/buy/browse/overview.html) | Precios en tiempo real de componentes de PC |

---

## 🚧 Estado del proyecto

> Proyecto en desarrollo por módulos.
