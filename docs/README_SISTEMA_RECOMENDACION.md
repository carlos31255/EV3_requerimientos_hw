# Contexto del Proyecto EV3 — Sistema Recomendador de Hardware

Este documento explica el enfoque del proyecto para alinear el trabajo de todas las ramas (ETL, API, Base de Datos y EDA).

## 🎯 El Objetivo Real
Somos un **sistema de recomendación de hardware para PC**.
Nuestro objetivo es sugerirle a un usuario qué componentes comprar basándonos en lo que piden los juegos actuales, lo que usa la mayoría de la gente y los precios reales del mercado.

---

## 🏗️ Arquitectura de Datos

El proyecto se alimenta de 3 fuentes externas que convergen en nuestra Base de Datos propia:

### 1. Requisitos de Juegos (ETL - Kaggle)
- **Qué es:** Requisitos mínimos y recomendados de +80k juegos.
- **Para qué sirve:** Define la "meta" técnica. (ej. "Para jugar Hogwarts Legacy necesitas mínimo una GTX 960").

### 2. Uso Real del Mercado (ETL - Steam HW Survey)
- **Qué es:** Qué hardware tienen realmente los usuarios a nivel mundial.
- **Para qué sirve:** Conocer las tendencias y popularidad. (ej. "La RTX 3060 es la tarjeta más usada hoy en día").

### 3. Precios de Mercado (API - eBay)
- **Qué es:** Precios reales y actualizados de componentes en CLP.
- **Para qué sirve:** Asignar un costo real a nuestras recomendaciones.

### 4. Base de Datos Propia (MySQL)
- **Qué es:** El núcleo del sistema. Aquí se guarda la información de las 3 fuentes externas ya procesada, MÁS los datos propios que genera nuestro sistema.
- **Datos propios que tendría la BD:**
  - `component_tiers`: Clasificación de rendimiento propia (ej. "Gama Baja", "Gama Media", "Gama Alta"). Esto no viene en los CSV, lo creamos nosotros.
  - `build_templates`: Configuraciones de PC pre-armadas por el sistema (ej. "Build Recomendada 1080p", "Build Presupuesto Ultra").
  - `user_queries` (Simulado): Consultas de ejemplo (ej. Presupuesto: 500k CLP, Juego objetivo: Cyberpunk).

---

## 🔄 El Flujo de Trabajo (Cómo se une todo)

1. El **ETL** toma los CSV estáticos (Kaggle y Steam), los limpia y los sube a la BD.
2. La **API** busca los precios en eBay (USD a CLP) y los actualiza en la BD para los componentes clave.
3. La **Base de Datos (MySQL)** centraliza todo. Contiene los juegos, el hardware de Steam, los precios de la API, y nuestras tablas propias de clasificación (tiers).
4. El **EDA** (Análisis Exploratorio) hace consultas a la BD cruzando toda esta información para generar los *insights* y las recomendaciones del sistema.

### Ejemplos de lo que el EDA responderá:
- *"Para jugar los top 10 juegos más populares de Kaggle, la GPU con mejor relación precio/popularidad es la RTX 3060 (cuesta $X CLP en eBay y la usa el Y% de Steam)."*
- *"El 30% de los usuarios actuales de Steam no podría correr juegos de 2026 sin hacer upgrade de RAM."*
- *"Si tienes 400.000 CLP de presupuesto y quieres jugar Cyberpunk 2077, tu mejor opción de Upgrade según los precios de eBay es..."*

---

## 📝 Próximos pasos por área:

- **Rama ETL:** Entregar los datasets limpios listos para subirse a MySQL.
- **Rama API:** Código que consulta precios en eBay (CLP) de una lista de componentes y los guarda en la BD.
- **Rama Base de Datos:** Crear la BD, importar los datos limpios del ETL, importar precios de la API, e inventar/crear las tablas de datos propios (`component_tiers`, `build_templates`).
- **Rama EDA:** Conectarse a MySQL para cruzar todo y generar las recomendaciones/gráficos finales.
