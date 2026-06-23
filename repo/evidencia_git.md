# Evidencia de Colaboración Profesional en Git

Este directorio documenta el uso profesional de Git en el proyecto EV3.

## Repositorio
🔗 https://github.com/carlos31255/EV3_requerimientos_hw

## Estrategia de Ramas (Branching)

```
main
 ├── ETL                     ← Pipeline de extracción y transformación
 ├── api                     ← Integración con la API de eBay
 ├── BD                      ← Base de datos (schema + datos iniciales)
 └── feature/integracion-docker ← Docker + Dashboard + integración final
```

## Historial de Commits Relevantes

| Commit | Rama | Descripción |
|---|---|---|
| `agrega modulo api de ebay...` | feature/integracion-docker | Fusión de archivos de la rama api al main |
| `fetch_prices guarda precios en BD...` | feature/integracion-docker | Motor ETL de precios conectado a MySQL |
| `mueve ETL a carpeta etl...` | feature/integracion-docker | Reorganización de carpetas según pauta |
| `agrega documentacion tecnica...` | feature/integracion-docker | Documentación en docs/ |
| `mueve Dockerfile a docker/` | feature/integracion-docker | Estructura Docker profesional |
| `actualiza requirements...` | feature/integracion-docker | Dependencias completas del proyecto |

## Flujo de Trabajo

1. Cada integrante trabajó en su rama temática (`ETL`, `api`, `BD`).
2. Los cambios se fusionaron mediante `git checkout origin/<rama> -- <archivos>` y `git merge` para mantener un historial limpio.
3. La rama `feature/integracion-docker` actuó como rama de integración antes del merge final a `main`.

## Comandos Git Utilizados en el Proyecto

```bash
# Crear y cambiar a una rama
git checkout -b nombre-rama

# Traer archivos específicos de otra rama
git checkout origin/api -- api/client.py api/fetch_prices.py

# Ver historial limpio
git log --oneline --graph --all

# Push al repositorio remoto
git push origin feature/integracion-docker
```
