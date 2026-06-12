"""
etl/validate.py
===============
Funciones de validacion de DataFrames usando pandas puro.
Se apoya en los esquemas definidos en etl/schemas.py.

Uso tipico:
    from etl.validate import validate_dataframe
    df, report = validate_dataframe(df, GAMES_SCHEMA, logger)
"""

import logging
import pandas as pd
from typing import Any

# ─────────────────────────────────────────────
# Helpers internos
# ─────────────────────────────────────────────

def _check_required_columns(df: pd.DataFrame, schema: dict, issues: list) -> None:
    """Verifica que todas las columnas requeridas existan en el DataFrame."""
    missing = [c for c in schema.get("required_columns", []) if c not in df.columns]
    if missing:
        issues.append(f"CRITICO — Columnas faltantes: {missing}")


def _check_non_null_columns(df: pd.DataFrame, schema: dict, issues: list) -> None:
    """Verifica que las columnas criticas no esten completamente vacias."""
    for col in schema.get("non_null_columns", []):
        if col not in df.columns:
            continue
        null_count = df[col].isna().sum()
        if null_count == len(df):
            issues.append(f"CRITICO — '{col}' esta completamente nula ({null_count} filas)")
        elif null_count > 0:
            pct = null_count / len(df) * 100
            issues.append(f"ADVERTENCIA — '{col}' tiene {null_count} nulos ({pct:.1f}%)")


def _check_dtypes(df: pd.DataFrame, schema: dict, issues: list) -> None:
    """Verifica los tipos de datos esperados (de forma flexible)."""
    for col, expected_dtype in schema.get("dtype_checks", {}).items():
        if col not in df.columns:
            continue
        actual = str(df[col].dtype)
        # Comprobacion flexible: 'float64' acepta 'Float64', etc.
        if expected_dtype not in actual and actual not in expected_dtype:
            issues.append(
                f"ADVERTENCIA — '{col}': tipo esperado '{expected_dtype}', "
                f"tipo real '{actual}'"
            )


def _check_value_constraints(df: pd.DataFrame, schema: dict, issues: list) -> None:
    """Aplica las restricciones de negocio definidas en el esquema."""
    for constraint in schema.get("value_constraints", []):
        col = constraint["column"]
        desc = constraint["description"]
        check_fn = constraint["check"]

        if col not in df.columns:
            continue

        try:
            mask = check_fn(df)
            n_violations = (~mask).sum()
            if n_violations > 0:
                pct = n_violations / len(df) * 100
                issues.append(
                    f"ADVERTENCIA — {desc}: {n_violations} violaciones ({pct:.1f}%)"
                )
        except Exception as e:
            issues.append(f"ERROR al evaluar restriccion '{desc}': {e}")


# ─────────────────────────────────────────────
# Funcion principal
# ─────────────────────────────────────────────

def validate_dataframe(
    df: pd.DataFrame,
    schema: dict,
    logger: logging.Logger,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Valida un DataFrame contra un esquema definido en schemas.py.

    Parametros
    ----------
    df     : DataFrame a validar
    schema : diccionario de esquema (de etl/schemas.py)
    logger : logger configurado en el modulo que llama

    Retorna
    -------
    df     : el mismo DataFrame (sin modificar)
    report : diccionario con el resumen de la validacion
    """
    source = schema.get("source", "desconocida")
    logger.info(f"Validando esquema: {source}")

    issues: list[str] = []

    _check_required_columns(df, schema, issues)
    _check_non_null_columns(df, schema, issues)
    _check_dtypes(df, schema, issues)
    _check_value_constraints(df, schema, issues)

    # Clasificar issues
    criticos    = [i for i in issues if i.startswith("CRITICO")]
    advertencias = [i for i in issues if i.startswith("ADVERTENCIA")]
    errores      = [i for i in issues if i.startswith("ERROR")]

    for msg in criticos:
        logger.error(msg)
    for msg in advertencias:
        logger.warning(msg)
    for msg in errores:
        logger.error(msg)

    if not issues:
        logger.info(f"  Validacion OK — sin problemas detectados ({len(df):,} filas)")
    else:
        logger.info(
            f"  Validacion completada: {len(criticos)} criticos, "
            f"{len(advertencias)} advertencias, {len(errores)} errores"
        )

    if criticos:
        raise ValueError(
            f"Validacion fallida para '{source}': {len(criticos)} errores criticos.\n"
            + "\n".join(criticos)
        )

    report = {
        "source":        source,
        "rows":          len(df),
        "columns":       list(df.columns),
        "criticos":      criticos,
        "advertencias":  advertencias,
        "errores":       errores,
        "passed":        len(criticos) == 0,
    }

    return df, report
