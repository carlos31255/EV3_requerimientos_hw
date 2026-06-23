# Tienda Hardware Intelligence — EV3

Sistema de inteligencia de mercado y recomendación de hardware para PC, diseñado para responder a la demanda técnica actual cruzando requisitos de videojuegos, estadísticas de uso global y precios de mercado en tiempo real.

Este proyecto consolida un pipeline completo de datos (ETL), integración de APIs externas, almacenamiento relacional (MySQL) y visualización interactiva mediante Dashboards adaptados a distintas audiencias (Ejecutiva, Técnica y Operativa), todo ello empaquetado y orquestado con Docker.

---

## 🎯 ¿Qué resuelve?

El sistema integra y analiza 3 fuentes de datos para la toma de decisiones:
1. **Requisitos de la Industria (Kaggle)** — Requisitos mínimos y recomendados de juegos en Steam, definiendo la "demanda técnica".
2. **Uso Real del Mercado (Steam HW Survey)** — Estadísticas de hardware a nivel mundial, indicando qué componentes usan realmente los jugadores.
3. **Precios en Vivo (eBay Browse API v1)** — Costo actual en el mercado para cada componente (convertido automáticamente a CLP usando mindicador.cl).

**El resultado:** Dashboards interactivos que permiten a la gerencia ver rentabilidades, a los ingenieros entender qué componentes exigen los juegos actuales, y a la tienda ajustar sus precios frente al mercado global.

---

## 🏗️ Arquitectura y Componentes

El proyecto está estructurado modularmente siguiendo las mejores prácticas:

- **`/etl/`**: Pipeline de extracción y transformación que toma los datasets crudos y genera muestras procesadas limpias (con logging profesional).
- **`/api/`**: Módulo que consume la API de eBay y mindicador.cl para consultar y almacenar precios en tiempo real en la base de datos (con soporte concurrente y caché).
- **`/db/`**: Base de datos MySQL con un esquema relacional (`1_schema.sql`) poblado inicialmente con datos de la tienda y el mercado (`2_data.sql`).
- **`/dashboards/`**: Aplicación en Streamlit (`app.py`) con visualizaciones interactivas diferenciadas por audiencia.
- **`/docker/`**: Configuración de contenedores. Orquestado con `docker-compose.yml` en la raíz.
- **`/docs/`**: Documentación técnica detallada.

---

## 📚 Documentación Técnica

Para información profunda sobre el funcionamiento, instalación y arquitectura del proyecto, consulte los siguientes documentos:

- 📘 [**Arquitectura del Sistema**](docs/arquitectura_sistema.md): Diseño del pipeline, modelos de datos y flujo de la información.
- 📙 [**Guía de Despliegue y Manual de Usuario**](docs/guia_despliegue.md): Instrucciones paso a paso para levantar el proyecto con Docker, manual del dashboard y solución de problemas.
- 📕 [**Documentación de la API**](docs/documentacion_api.md): Endpoints, autenticación, manejo de errores y optimizaciones del módulo de obtención de precios.

---

## 🚀 Despliegue Rápido (Docker)

El sistema está completamente contenerizado. Para levantarlo:

```bash
# En Windows (recomendado)
iniciar_proyecto.bat

# Manualmente
docker-compose up --build -d
```
El dashboard estará disponible en [**http://localhost:8501**](http://localhost:8501).

Para detener el sistema de forma segura:
```bash
# En Windows
apagar_proyecto.bat

# Manualmente
docker-compose down
```

---

## 📁 Fuentes de Datos

| Fuente | Tipo de Integración | Descripción |
|---|---|---|
| [Kaggle PC Requirements](https://www.kaggle.com/datasets/baraazaid/pc-video-game-requirements) | Archivo Estático (CSV) | Requisitos de hardware de juegos de Steam. |
| [Steam Hardware Survey](https://github.com/jdegene/steamHWsurvey) | Archivo Estático (CSV) | Porcentaje de adopción global de hardware (GPUs, RAM, Discos). |
| [eBay Browse API v1](https://developer.ebay.com/) | API REST (OAuth2) | Precios de mercado en tiempo real en USD. |
| [Mindicador.cl](https://mindicador.cl/) | API REST Pública | Tipo de cambio diario USD a CLP. |

---

> Desarrollado como proyecto final (EV3) de Programación para la Ciencia de Datos.
