"""Analiza y reasigna distribuciones del dataset de reclamos."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(r"C:\Users\Luis Alcala\Documents\gestiones reps ml")
SOURCE = BASE_DIR / "base_datos_reclamos.xlsx"
DEST = BASE_DIR / "base_datos_reclamos_modificado.xlsx"
SHEET = "reclamos"
RNG_SEED = 42
GLOBAL_PRICE_MIN = 10.0
GLOBAL_PRICE_MAX = 1800.0

PRODUCTO_CANDIDATES = [
    "producto_reclamado",
    "Producto_Reclamado",
    "PRODUCTO_RECLAMADO",
    "producto reclamado",
    "Producto Reclamado",
]

PAIS_WEIGHTS = {
    "Mexico": 0.18,
    "Brasil": 0.16,
    "Colombia": 0.15,
    "Argentina": 0.14,
    "Chile": 0.12,
    "Peru": 0.10,
    "Venezuela": 0.08,
    "Uruguay": 0.04,
    "Panama": 0.03,
}

CANAL_WEIGHTS = {
    "App movil": 0.30,
    "Chat": 0.28,
    "Web": 0.20,
    "Email": 0.12,
    "Telefono": 0.10,
}

TIPO_RECLAMO_WEIGHTS = {
    "producto_no_recibido": 0.47,
    "caja_vacia": 0.27,
    "producto_diferente_defectuoso": 0.18,
    "devolucion": 0.08,
}

# Países agrupados por perfil geográfico/económico
PAIS_CALIDO = {"Mexico", "Brasil", "Colombia"}
PAIS_ALTO_PODER = {"Chile", "Argentina", "Uruguay"}
PAIS_MEDIO = {"Peru", "Panama", "Venezuela"}

# Productos con preferencia geográfica
PRODUCTO_CALIDO = {
    "Aire acondicionado", "Ventilador",
}
PRODUCTO_ALTO_PODER = {
    "Audifonos", "Smartwatch", "iPhone 17", "Samsung S26 Ultra", "iPad Air",
    "Camara", "Consola de videojuegos", "Laptop Lenovo", "Monitor 27\"",
    "Tablet", "Televisor 55\"", "Televisor 65\"",
}
PRODUCTO_BICICLETA = {"Bicicleta"}
PRODUCTO_ELECTRO_GRANDE = {
    "Nevera", "Lavadora", "Cocina", "Microondas",
}
PRODUCTO_BAJO_TICKET = {
    "Licuadora", "Tarjeta de regalo", "Zapatos deportivos", "Silla gamer",
    "Escritorio",
}


def find_column(columns, candidates):
    cols_lower = {c: str(c).strip().lower().replace(" ", "_") for c in columns}
    for cand in candidates:
        key = cand.lower().replace(" ", "_")
        for col, norm in cols_lower.items():
            if norm == key:
                return col
    return None


def find_producto_column(columns):
    cols_lower = {c: str(c).strip().lower().replace(" ", "_") for c in columns}
    for cand in PRODUCTO_CANDIDATES:
        key = cand.lower().replace(" ", "_")
        for col, norm in cols_lower.items():
            if norm == key:
                return col
    for col, norm in cols_lower.items():
        if "producto" in norm and "reclam" in norm:
            return col
    return None


def distribution_table(series, total=None):
    total = total or len(series)
    counts = series.value_counts(dropna=False)
    rows = []
    for val, cnt in counts.items():
        label = "<vacío>" if pd.isna(val) else str(val)
        rows.append(
            {
                "valor": label,
                "conteo": int(cnt),
                "porcentaje": round(100 * cnt / total, 2),
            }
        )
    return rows


def build_weights(products):
    """Pesos manuales realistas: top productos con más reclamos (power-law suave)."""
    n = len(products)
    manual = {}
    if n >= 1:
        manual[products[0]] = 0.28
    if n >= 2:
        manual[products[1]] = 0.22
    if n >= 3:
        manual[products[2]] = 0.16
    if n >= 4:
        manual[products[3]] = 0.12
    if n >= 5:
        manual[products[4]] = 0.08
    remaining = [p for p in products if p not in manual]
    if remaining:
        tail_total = max(0.0, 1.0 - sum(manual.values()))
        ranks = np.arange(1, len(remaining) + 1, dtype=float)
        tail = (1.0 / ranks) ** 1.4
        tail = tail / tail.sum() * tail_total
        for p, w in zip(remaining, tail):
            manual[p] = float(w)
    arr = np.array([manual[p] for p in products], dtype=float)
    arr = arr / arr.sum()
    return arr


def reassign_productos(series, rng):
    products = sorted(series.dropna().unique().tolist(), key=str)
    if not products:
        return series.copy(), {}

    n = len(series)
    weights = build_weights(products)
    new_values = rng.choice(products, size=n, p=weights)
    out = series.copy()
    out.iloc[:] = new_values
    return out, dict(zip(products, weights.tolist()))


def build_price_ranges(df_orig, prod_col, valor_col):
    """Rangos de precio por producto a partir del dataset original."""
    stats = (
        df_orig.groupby(prod_col)[valor_col]
        .agg(["min", "max", "mean", "std"])
        .round(4)
    )
    ranges = {}
    for producto, row in stats.iterrows():
        std = row["std"]
        if pd.isna(std) or std <= 0:
            std = max((row["max"] - row["min"]) / 6, 1.0)
        ranges[producto] = {
            "min": float(row["min"]),
            "max": float(row["max"]),
            "mean": float(row["mean"]),
            "std": float(std),
        }
    return ranges


def align_valor_producto(series_producto, price_ranges, rng):
    """Asigna valor_producto_usd coherente con producto_reclamado."""
    values = np.empty(len(series_producto), dtype=float)
    fallback_mean = np.mean([r["mean"] for r in price_ranges.values()])

    for i, producto in enumerate(series_producto):
        info = price_ranges.get(producto)
        if info is None:
            val = fallback_mean
        else:
            val = rng.normal(info["mean"], info["std"])
            val = np.clip(val, info["min"], info["max"])
        val = np.clip(val, GLOBAL_PRICE_MIN, GLOBAL_PRICE_MAX)
        values[i] = round(float(val), 2)

    return pd.Series(values, index=series_producto.index)


def build_pais_weights(countries):
    """Pesos desiguales por país; normaliza si faltan países en el mapping."""
    weights = {}
    unknown = []
    for country in countries:
        if country in PAIS_WEIGHTS:
            weights[country] = PAIS_WEIGHTS[country]
        else:
            unknown.append(country)

    if unknown:
        tail_total = max(0.05, 1.0 - sum(weights.values()))
        tail = (1.0 / np.arange(1, len(unknown) + 1)) ** 1.2
        tail = tail / tail.sum() * tail_total
        for country, w in zip(sorted(unknown, key=str), tail):
            weights[country] = float(w)

    arr = np.array([weights[c] for c in countries], dtype=float)
    arr = arr / arr.sum()
    return arr


def reassign_pais_region(series, rng):
    countries = sorted(series.dropna().unique().tolist(), key=str)
    if not countries:
        return series.copy(), {}

    n = len(series)
    weights = build_pais_weights(countries)
    new_values = rng.choice(countries, size=n, p=weights)
    out = series.copy()
    out.iloc[:] = new_values
    return out, dict(zip(countries, weights.tolist()))


def reassign_weighted_column(series, weight_map, rng):
    """Reasigna valores categóricos según pesos manuales."""
    values = sorted(series.dropna().unique().tolist(), key=str)
    if not values:
        return series.copy(), {}

    weights = np.array([weight_map.get(v, 1.0) for v in values], dtype=float)
    weights = weights / weights.sum()
    new_values = rng.choice(values, size=len(series), p=weights)
    out = series.copy()
    out.iloc[:] = new_values
    return out, dict(zip(values, weights.tolist()))


def geo_weight(pais, producto):
    """Peso país×producto según lógica geográfica realista."""
    w = 1.0

    if producto in PRODUCTO_CALIDO:
        if pais in PAIS_CALIDO:
            w *= 3.5
        elif pais in PAIS_ALTO_PODER:
            w *= 0.6
        else:
            w *= 0.8

    elif producto in PRODUCTO_ALTO_PODER:
        if pais in PAIS_ALTO_PODER:
            w *= 3.0
        elif pais in PAIS_MEDIO:
            w *= 1.2
        else:
            w *= 0.7

    elif producto in PRODUCTO_BICICLETA:
        if pais in {"Colombia", "Chile"}:
            w *= 2.8
        elif pais in PAIS_CALIDO:
            w *= 1.5
        else:
            w *= 0.9

    elif producto in PRODUCTO_ELECTRO_GRANDE:
        if pais in {"Mexico", "Brasil", "Argentina"}:
            w *= 2.5
        elif pais in PAIS_CALIDO:
            w *= 1.8
        else:
            w *= 0.8

    elif producto in PRODUCTO_BAJO_TICKET:
        w *= 1.0

    else:
        # Productos medianos (Cama, Closet, etc.): distribución más pareja
        w *= 1.0

    return w


def build_seed_matrix(paises, productos):
    """Matriz semilla de pesos geográficos país×producto."""
    matrix = np.zeros((len(paises), len(productos)), dtype=float)
    for i, pais in enumerate(paises):
        for j, producto in enumerate(productos):
            matrix[i, j] = geo_weight(pais, producto)
    return matrix


def ipf(seed_matrix, row_targets, col_targets, max_iter=200, tol=1e-8):
    """Iterative Proportional Fitting para ajustar márgenes."""
    matrix = seed_matrix.copy().astype(float)
    row_targets = np.asarray(row_targets, dtype=float)
    col_targets = np.asarray(col_targets, dtype=float)

    for _ in range(max_iter):
        row_sums = matrix.sum(axis=1)
        row_sums[row_sums == 0] = 1.0
        matrix *= (row_targets / row_sums)[:, None]

        col_sums = matrix.sum(axis=0)
        col_sums[col_sums == 0] = 1.0
        matrix *= (col_targets / col_sums)[None, :]

        if (
            np.allclose(matrix.sum(axis=1), row_targets, rtol=0, atol=tol)
            and np.allclose(matrix.sum(axis=0), col_targets, rtol=0, atol=tol)
        ):
            break

    return matrix


def integer_contingency(continuous, row_targets, col_targets):
    """Convierte matriz continua IPF a enteros preservando márgenes exactos."""
    row_targets = np.asarray(row_targets, dtype=int)
    col_targets = np.asarray(col_targets, dtype=int)
    n_rows, n_cols = continuous.shape
    total = int(row_targets.sum())
    assert int(col_targets.sum()) == total

    base = np.floor(continuous).astype(int)
    remainder = total - int(base.sum())
    frac = continuous - np.floor(continuous)
    idxs = np.argsort(-frac.ravel())

    for idx in idxs:
        if remainder <= 0:
            break
        i, j = np.unravel_index(idx, (n_rows, n_cols))
        if base[i].sum() < row_targets[i] and base[:, j].sum() < col_targets[j]:
            base[i, j] += 1
            remainder -= 1

    if remainder > 0:
        for i in range(n_rows):
            for j in range(n_cols):
                while remainder > 0 and base[i].sum() < row_targets[i] and base[:, j].sum() < col_targets[j]:
                    base[i, j] += 1
                    remainder -= 1

    if remainder != 0:
        raise ValueError(f"Remanente sin asignar: {remainder}")

    assert int(base.sum()) == total
    assert np.array_equal(base.sum(axis=1), row_targets)
    assert np.array_equal(base.sum(axis=0), col_targets)
    return base


def reassign_pais_producto_correlated(df, prod_col, pais_col, rng):
    """
    Reasigna producto y país con correlación geográfica,
    preservando los conteos marginales actuales.
    """
    producto_counts = df[prod_col].value_counts()
    pais_counts = df[pais_col].value_counts()

    productos = producto_counts.index.tolist()
    paises = pais_counts.index.tolist()

    row_targets = np.array([pais_counts[p] for p in paises], dtype=int)
    col_targets = np.array([producto_counts[p] for p in productos], dtype=int)

    seed = build_seed_matrix(paises, productos)
    continuous = ipf(seed, row_targets, col_targets)
    contingency = integer_contingency(continuous, row_targets, col_targets)

    pairs = []
    for i, pais in enumerate(paises):
        for j, producto in enumerate(productos):
            count = int(contingency[i, j])
            pairs.extend([(pais, producto)] * count)

    expected = int(row_targets.sum())
    if len(pairs) != expected:
        raise ValueError(
            f"Contingencia inválida: {len(pairs)} pares vs {expected} filas"
        )

    rng.shuffle(pairs)
    new_paises = [p[0] for p in pairs]
    new_productos = [p[1] for p in pairs]

    df_out = df.copy()
    df_out[pais_col] = new_paises
    df_out[prod_col] = new_productos

    return df_out, contingency, paises, productos


def contingency_summary(df, prod_col, pais_col, top_n=5):
    """Top y bottom combinaciones país×producto."""
    ct = (
        df.groupby([pais_col, prod_col])
        .size()
        .reset_index(name="conteo")
        .sort_values("conteo", ascending=False)
    )
    ct["porcentaje"] = (100 * ct["conteo"] / len(df)).round(2)
    top = ct.head(top_n).to_dict("records")
    bottom = ct.tail(top_n).sort_values("conteo").to_dict("records")
    return top, bottom


def verify_marginals(df_before, df_after, prod_col, pais_col):
    """Confirma que los totales marginales se conservan."""
    prod_before = df_before[prod_col].value_counts().sort_index()
    prod_after = df_after[prod_col].value_counts().sort_index()
    pais_before = df_before[pais_col].value_counts().sort_index()
    pais_after = df_after[pais_col].value_counts().sort_index()

    prod_ok = prod_before.equals(prod_after)
    pais_ok = pais_before.equals(pais_after)

    return {
        "producto_marginal_preservado": bool(prod_ok),
        "pais_marginal_preservado": bool(pais_ok),
        "producto_diferencias": (
            (prod_after - prod_before).to_dict() if not prod_ok else {}
        ),
        "pais_diferencias": (
            (pais_after - pais_before).to_dict() if not pais_ok else {}
        ),
    }


def price_summary_by_product(df, prod_col, valor_col):
    stats = (
        df.groupby(prod_col)[valor_col]
        .agg(["count", "min", "max", "mean"])
        .round(2)
        .sort_values("count", ascending=False)
    )
    return stats.to_dict("index")


def main():
    report = {"origen": str(SOURCE), "destino": str(DEST), "semilla": RNG_SEED}
    rng = np.random.default_rng(RNG_SEED)

    df_orig = pd.read_excel(SOURCE, sheet_name=SHEET)
    prod_col = find_producto_column(df_orig.columns)
    valor_col = find_column(df_orig.columns, ["valor_producto_usd", "Valor_Producto_USD"])
    pais_col = find_column(
        df_orig.columns,
        ["pais_region", "país_region", "Pais_Region", "pais", "país"],
    )
    canal_col = find_column(df_orig.columns, ["canal_contacto", "Canal_Contacto"])
    tipo_col = find_column(df_orig.columns, ["tipo_reclamo", "Tipo_Reclamo"])

    required = {
        "producto_reclamado": prod_col,
        "valor_producto_usd": valor_col,
        "pais_region": pais_col,
        "canal_contacto": canal_col,
        "tipo_reclamo": tipo_col,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise SystemExit(f"Columnas no encontradas: {', '.join(missing)}")

    price_ranges = build_price_ranges(df_orig, prod_col, valor_col)

    if not DEST.exists():
        raise SystemExit(
            f"No existe el archivo modificado: {DEST}. Ejecutar primero la versión inicial."
        )

    df_mod = pd.read_excel(DEST, sheet_name=SHEET)
    report["modo"] = "actualizar_modificado_existente"
    report["filas"] = int(len(df_mod))

    # --- ANTES ---
    report["canal_contacto_antes"] = distribution_table(df_mod[canal_col])
    report["tipo_reclamo_antes"] = distribution_table(df_mod[tipo_col])
    report["producto_marginal_antes"] = distribution_table(df_mod[prod_col])
    report["pais_marginal_antes"] = distribution_table(df_mod[pais_col])

    # --- 1. canal_contacto ---
    df_mod[canal_col], weights_canal = reassign_weighted_column(
        df_mod[canal_col], CANAL_WEIGHTS, rng
    )
    report["canal_contacto_despues"] = distribution_table(df_mod[canal_col])
    report["pesos_canal_aplicados"] = {
        str(k): round(v, 4) for k, v in sorted(weights_canal.items(), key=lambda x: -x[1])
    }

    # --- 2. tipo_reclamo ---
    df_mod[tipo_col], weights_tipo = reassign_weighted_column(
        df_mod[tipo_col], TIPO_RECLAMO_WEIGHTS, rng
    )
    report["tipo_reclamo_despues"] = distribution_table(df_mod[tipo_col])
    report["pesos_tipo_aplicados"] = {
        str(k): round(v, 4) for k, v in sorted(weights_tipo.items(), key=lambda x: -x[1])
    }

    # --- 3. correlación país×producto (IPF) ---
    df_mod, contingency, paises, productos = reassign_pais_producto_correlated(
        df_mod, prod_col, pais_col, rng
    )
    report["marginales_verificacion"] = verify_marginals(
        pd.read_excel(DEST, sheet_name=SHEET), df_mod, prod_col, pais_col
    )
    report["producto_marginal_despues"] = distribution_table(df_mod[prod_col])
    report["pais_marginal_despues"] = distribution_table(df_mod[pais_col])

    top_ct, bottom_ct = contingency_summary(df_mod, prod_col, pais_col)
    report["pais_producto_top5"] = top_ct
    report["pais_producto_bottom5"] = bottom_ct

    # --- Recalcular valor_producto_usd ---
    df_mod[valor_col] = align_valor_producto(df_mod[prod_col], price_ranges, rng)
    report["precios_por_producto_despues"] = price_summary_by_product(
        df_mod, prod_col, valor_col
    )
    report["valor_producto_usd_global"] = {
        "min": round(float(df_mod[valor_col].min()), 2),
        "max": round(float(df_mod[valor_col].max()), 2),
        "media": round(float(df_mod[valor_col].mean()), 2),
    }

    df_mod.to_excel(DEST, index=False, sheet_name=SHEET)

    report["filas_modificadas"] = int(len(df_mod))
    report["archivo_guardado"] = str(DEST)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
