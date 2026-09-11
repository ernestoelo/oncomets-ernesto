# Figuras del B10

Las dibuja `scripts/b10_figuras_o1_o3.py`, que es el **único escritor** de todo lo que hay en este
directorio. No mide nada: lee los artefactos de `results/`, verifica que reproduzcan los
`resultados.md` y aborta si alguno no cuadra.

```bash
/home/sdonoso/miniconda3/envs/pruebas/bin/python scripts/b10_figuras_o1_o3.py
```

`envs/pruebas` porque el script importa `ESCALERA` y `cargar_offset()` del driver de O1, que trae
zarr al tope (workaround B: binario absoluto).

| figura | se lee con |
|---|---|
| `o1_apertura_grado.png` (1600 × 960) | [`../grado_sin_marca/resultados.md`](../grado_sin_marca/resultados.md) §3, §4 y §6.a |
| `o3_auc_por_lamina.png` (1600 × 1120) | [`../cdis_localizacion/resultados.md`](../cdis_localizacion/resultados.md) §1.a, §2 y §3.b |

## Qué muestra cada una

Para escribir pies y guion sin volver a abrir la imagen ([[image-api-qa-limit]]).

**O1.** Título «O1 · El tamaño reencuentra las marcas de alto grado, no las de bajo». Eje x en
escala log con N = 10, 20, 50, 100, 200, 500, 1000 y 2000, y debajo de cada N la carga media en
mm² por lámina (0,13 a 9,55). Eje y de 0 a 100 %, porcentaje de las alcanzables. Tres curvas
sólidas con marcador, alto oscuro, moderado medio y bajo claro, y cada una con su p97,5 del nulo
punteado en el mismo color. Línea vertical en N = 500 con un bloque de texto a su derecha: «N =
500 · 4,07 mm² por lámina · alto 41 de 76 · moderado 12 de 53 · bajo 0 de 16». Etiquetas directas
al final de cada curva (57 de 76, 23 de 53, 6 de 16) y leyenda arriba a la izquierda.

**O3.** Título «O3 · La localización se sostiene en train y val; en láminas que el fold no usó, no
está mostrada». Forest plot de 10 filas agrupadas bajo cuatro encabezados de tier (train, val,
test, ausente), cada uno con un punto del color de su tier. Eje x de AUC de 0 a 1, con línea
punteada en 0,5 rotulada «azar». Columna a la derecha con los parches con CDIS de cada lámina.
Punto relleno si `p` < 0,05, hueco si no. `†` junto a la 164001 y la B25-158899, que además lleva
debajo el sub-rótulo «rama si, región anotada». Leyenda al pie con el relleno y la barra de IC.

## Paleta

Grado y tier son **ordinales**: cambiar el orden cambia el significado. Por eso van en una rampa de
un solo tono y no en colores categóricos, con más oscuro = grado más alto o tier más limpio. Los dos
azares del medio son `#1B4F8C` de la plantilla oficial y pasos de la rampa de referencia de la skill
`dataviz`. Validada con su `validate_palette.py --ordinal --surface "#ffffff"`:

| rampa | uso | monótona | ΔL adyacente ≥ 0,06 | extremo claro | dispersión de tono |
|---|---|---|---|---|---|
| `#6da7ec, #3987e5, #1B4F8C` | O1: bajo, moderado, alto | PASS | PASS | 2,50:1 | 1° |
| `#6da7ec, #3987e5, #1B4F8C, #0d366b` | O3: train, val, test, ausente | PASS | PASS | 2,50:1 | 3° |

El node de `envs/pruebas` está roto (le falta `sqlite3session_attach`), así que se usó el gemelo
en Python del validador, que trae la misma skill. Tipografía Barlow desde `clam_testing2/fonts/barlow/`
con `font_manager.addfont`. Barlow no trae `●` (U+25CF): los puntos de los encabezados de O3 van
como marcador y no como glifo.

## CSV

```
CSV: o1_apertura_grado.csv
Path en server: /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/sprints/B10_sprint10/figuras/o1_apertura_grado.csv
Schema (columnas y tipos):
  - grupo: str, "alto", grado de la marca; "total" suma los tres
  - N: int, 500, núcleos epiteliales más grandes de cada lámina
  - n_laminas: int, 9, láminas del grupo
  - alcanzables: int, 76, marcas cuyo núcleo es epitelial (el denominador)
  - recall: int, 41, marcas recuperadas entre los N
  - pct_alcanzables: float, 53.9474, 100 · recall / alcanzables (la curva sólida)
  - nulo_media: float, 0.35, media del nulo sumado sobre las láminas del grupo
  - nulo_p975: float, 2.0, percentil 97,5 de ese nulo
  - pct_nulo_p975: float, 2.6316, 100 · nulo_p975 / alcanzables (la curva punteada)
  - carga_media_mm2_lamina: float, 4.0655, carga media en N de LAS 21 LÁMINAS
Filas: 32 (8 peldaños × 4 grupos; dentro de cada N, alto, moderado, bajo, total)
Producido por: scripts/b10_figuras_o1_o3.py, desde results/b10_grado_sin_marca/{escalera.csv,nulo.npz}
Consumido por: la figura y ../reunion_martes.md
Ejemplo (head -3):
  grupo,N,n_laminas,alcanzables,recall,pct_alcanzables,nulo_media,nulo_p975,pct_nulo_p975,carga_media_mm2_lamina
  alto,10,9,76,8,10.5263,0.0100,0.0000,0.0000,0.1329
  moderado,10,10,53,0,0.0000,0.0000,0.0000,0.0000,0.1329
Trampas conocidas:
  - La carga NO es por grado: es la de las 21 láminas y se repite en los cuatro grupos.
  - El nulo del grupo se suma iteración a iteración y después se toma el percentil. Sumar los
    percentiles de cada lámina daría otra cosa.
  - N = 5000 no está: corre sobre 19 láminas y el denominador de bajo cae de 16 a 9.
```

```
CSV: o3_auc_por_lamina.csv
Path en server: /media/administrador/Storage1/sdonoso/clam_testing2/oncomets-ernesto/sprints/B10_sprint10/figuras/o3_auc_por_lamina.csv
Schema (columnas y tipos):
  - orden_figura: int, 1, fila de la figura contando desde arriba
  - tier: str, "train" | "val" | "test" | "fuera" ("fuera" se rotula «ausente» en la figura)
  - slide: str, "124729"
  - fuente: str, "ckpt_1fold_verdadera"; la B25-158899 es "ckpt_1fold_predicha"
  - rama: str, "verdadera:si"; la B25-158899 es "predicha:si"
  - universo: str, "lamina" | "region" (solo la B25-158899 va confinada)
  - etiqueta: str, CDIS_presente de la lámina; "None" en la B25-158899, que no tiene fila
  - n_parches: int, 4334, parches del universo
  - n_marcados: int, 32, parches con CDIS
  - auc, ic95_lo, ic95_hi: float, IC de Hanley-McNeil SIN recortar
  - ic_lo_dibujado, ic_hi_dibujado: float, el IC recortado a [0, 1] que se dibuja
  - ic_recortado: bool
  - p_nulo: float, p por traslación rígida; n_iter_nulo: int, iteraciones del nulo
  - relleno: bool, p_nulo < 0,05
  - alineada: bool, leído de sprints/B8_sprint8/anotaciones_patologo/offset_<slide>.json
Filas: 10, en el orden de la figura (tier y, dentro del tier, AUC descendente)
Producido por: scripts/b10_figuras_o1_o3.py, desde results/b10_cdis/{auc_cdis.csv,auc_cdis_region.csv}
Consumido por: la figura y ../reunion_martes.md
Ejemplo (head -3):
  orden_figura,tier,slide,fuente,rama,universo,etiqueta,n_parches,n_marcados,auc,ic95_lo,ic95_hi,ic_lo_dibujado,ic_hi_dibujado,ic_recortado,p_nulo,n_iter_nulo,relleno,alineada
  1,train,124729,ckpt_1fold_verdadera,verdadera:si,lamina,si,4334,32,0.9292,0.8675,0.9909,0.8675,0.9909,False,0.0050,200,True,True
  2,train,110616,ckpt_1fold_verdadera,verdadera:no_identificado,lamina,no_identificado,2933,44,0.7752,0.6934,0.8570,0.6934,0.8570,False,0.0169,58,True,True
Trampas conocidas:
  - La B25-158899 NO es rama verdadera: es la `si`, confinada a su región (resultados.md §3.a).
  - El nulo de la 110616 tiene 58 iteraciones y no 200, así que su p = 0,017 es el piso de ese nulo.
  - `alineada` no viene del driver de O3, que no la lleva: agregarla cambiaría los bytes de
    auc_cdis.csv, que tiene regresión byte a byte. Se lee del JSON del offset.
```
