# Guía de publicación — GitHub + Kaggle

Esta carpeta ya es un repositorio listo para subir. Sigue los pasos.

---

## Parte A — GitHub (repositorio principal para reclutadores)

### 1. Antes de subir: capturas del tablero
Abre `Gestion operativa y reps.pbix` en Power BI y exporta una imagen de cada página (Exportar → o captura de pantalla). Guárdalas en `dashboard/screenshots/` como `01_gestion_operativa.png` y `02_representantes.png`. Luego enlázalas en el README (sección "Tablero en Power BI").

### 2. Tamaño de archivos
`casos.csv` pesa ~50 MB. GitHub admite archivos hasta 100 MB, así que **sube normal**. Si más adelante crece por encima de 100 MB, usa **Git LFS**:
```bash
git lfs install
git lfs track "*.csv"
git add .gitattributes
```
El `.pbix` pesa ~12 MB: cabe sin problema.

### 3. Crear el repo y subir
```bash
cd marketplace-claims-review
git init
git add .
git commit -m "Proyecto: revision de reclamos marketplace (datos sinteticos) + EDA"
git branch -M main
# Crea primero el repo vacio en github.com (sin README) llamado marketplace-claims-review
git remote add origin https://github.com/Alcala1702/marketplace-claims-review.git
git push -u origin main
```

### 4. Toques finales en GitHub
- Reemplaza `Alcala1702` en el README por tu usuario real.
- En "About" del repo: agrega descripción corta y temas (topics): `data-analysis`, `eda`, `pandas`, `power-bi`, `synthetic-data`, `portfolio`.
- Verifica que las figuras de `reports/figures/` se vean en el README.

---

## Parte B — Kaggle (dataset + notebook para comunidad)

### Opción 1 — Web (más simple)
1. Entra a kaggle.com → **Create → New Dataset**.
2. Sube `data/casos.csv` y `data/gestion_operativa.xlsx`.
3. Título: *Marketplace Claims Review (synthetic, LATAM)*.
4. En la descripción, pega el contenido de `data/DATA_CARD.md`.
5. Licencia: **CC BY 4.0**. Publica.
6. Luego **Create → New Notebook**, adjunta tu dataset (Add Data) y sube `notebooks/01_eda_reclamos.ipynb`. Cambia las rutas `../data/` por `/kaggle/input/<slug-del-dataset>/`. Ejecuta y publica.

### Opción 2 — CLI (reproducible)
```bash
pip install kaggle           # coloca tu kaggle.json en ~/.kaggle/
cd data
# dataset-metadata.json ya esta aqui; ajusta el "id" a tu usuario
kaggle datasets create -p . --dir-mode zip
```

### 3. Enlazar ambas plataformas
- En el dataset de Kaggle, añade el enlace al repo de GitHub.
- En el README de GitHub, añade el enlace al dataset y al notebook de Kaggle.

---

## Checklist final
- [ ] Capturas del tablero en `dashboard/screenshots/` y enlazadas en el README
- [ ] `Alcala1702` reemplazado en README y guía
- [ ] Repo de GitHub público con topics y descripción
- [ ] Dataset de Kaggle publicado con la data card
- [ ] Notebook de Kaggle ejecutado con rutas ajustadas
- [ ] Enlaces cruzados GitHub ↔ Kaggle
- [ ] Disclaimer de "datos sintéticos" visible en ambos
