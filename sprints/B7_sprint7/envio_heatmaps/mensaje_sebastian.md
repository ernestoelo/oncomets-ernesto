# Mensaje para Sebastián (chat) + inventario del envío

> Fuente canónica versionada. Los PNG y el .zip de esta carpeta son **derivados**
> (gitignorados); el original versionado vive en
> `results/b7_mammoth_interp/interpretabilidad/<tarea>/<lámina>/attention_side_by_side.png`.
> Redactado en el registro de Ernesto ([[entregable-externo-sanitizado]]).

## Texto para copiar y pegar — ENVÍO DE UNA SOLA IMAGEN (el elegido)

> Adjuntar `tipo_TCGA-AC-A8OS_lobulillar.png`. Es la que sostiene las dos mitades del
> mensaje a la vez (Spearman 0.885, de las más altas, y Jaccard top-5% 0.243), es una cuña
> de tejido limpia sin fragmentos sueltos que inviten preguntas de artefacto, y es de
> **tipo histológico**, así que no arrastra el punto delicado de CDIS.

te mando una comparación de atención, clam contra mammoth sobre la misma lámina: carcinoma
lobulillar invasivo, del test del fold 0 y bien clasificada por las dos. izquierda clam,
centro mammoth, derecha la resta.

la lámina tiene 4201 parches y cada modelo le da un puntaje de atención a cada uno. ordeno
los parches por ese puntaje en cada modelo y comparo los dos ordenamientos (correlación de
rangos): 0.885 sobre 1, o sea ordenan el tejido casi igual.

después miro solo el tejido más atendido, el 5% de arriba: 210 parches por modelo. de esos
comparten 82 y cada uno se queda con 128 que el otro ni marca. el solapamiento da 0.243,
cuando al azar daría 0.026.

resumido: coinciden en qué zona del tejido importa y no en qué parches puntuales miran ahí
adentro. si le señaláramos regiones a un patólogo con esto, los dos le apuntarían al mismo
sector pero a parches distintos.

ojo que el mapa es la atención sobre los parches, no el ruteo de expertos: en mammoth los
30 ya vienen mezclados en cada parche antes de esta etapa.

tengo las otras 6 láminas si las querés ver.

### De dónde salen esas cuentas

`topk_jaccard` (`scripts/clam_vs_mammoth_attention.py`) toma `k = round(N · 0.05)` parches
por modelo y devuelve intersección sobre unión. Para N = 4201: k = 210, y J = 0.243 implica
82 compartidos (82/338). El azar sería k²/N ≈ 10.5 compartidos → J ≈ 0.026.

## Texto alternativo — ENVÍO DE LAS 7 LÁMINAS

te paso los mapas de atención de las 7 láminas, clam contra mammoth. son 7 imágenes y cada
una tiene tres paneles: clam a la izquierda, mammoth al medio, y la resta de los dos a la
derecha.

los nombres van por tarea y lámina, así que se ubican solos: tipo_TCGA-AO-A12D_ductal-NST,
tipo_TCGA-AC-A8OS_lobulillar, tipo_TCGA-E9-A1NE_otros, cdis_TCGA-D8-A1XB_si,
cdis_TCGA-A7-A4SB_no, lvi_TCGA-D8-A1X5_presente, lvi_TCGA-D8-A1XW_ausente.

todas son del test del fold 0, o sea ninguna la vieron entrenando, y las dos ramas las
clasifican bien. así lo que se ve es dónde mira cada una y no que alguna se esté
equivocando.

lo que dicen los números: la correlación de rangos entre los dos mapas da 0.805 promedio,
pero si te quedás con el 5% de parches más atendidos el solapamiento cae a 0.172, y con el
1% a 0.073. o sea ordenan el tejido parecido, pero los parches puntuales que ponen arriba
son casi todos distintos.

la otra diferencia es que mammoth reparte más la atención: entropía 0.894 contra 0.781 de
clam, y pasa en 6 de las 7. donde más se nota es en la lámina de cdis positiva, que clam
concentra harto (0.642) y mammoth abre (0.927).

una salvedad: en cdis mammoth también mide un poco mejor, pero con 7 láminas no me da para
decir que sea por la forma de la atención. queda como sospecha nomás.

## Inventario del paquete

| Archivo | Tarea | Clase real | N parches | Spearman | Jaccard top-5% |
|---|---|---|---|---|---|
| `tipo_TCGA-AO-A12D_ductal-NST.png` | tipo histológico | inv. tipo no especificado | 7097 | 0.848 | 0.079 |
| `tipo_TCGA-AC-A8OS_lobulillar.png` | tipo histológico | lobulillar invasivo | 4201 | 0.885 | 0.243 |
| `tipo_TCGA-E9-A1NE_otros.png` | tipo histológico | otros | 5592 | 0.669 | 0.315 |
| `cdis_TCGA-D8-A1XB_si.png` | CDIS | si | 16442 | 0.847 | 0.202 |
| `cdis_TCGA-A7-A4SB_no.png` | CDIS | no | 2793 | 0.921 | 0.261 |
| `lvi_TCGA-D8-A1X5_presente.png` | invasión linfovascular | presente | 28170 | 0.668 | 0.008 |
| `lvi_TCGA-D8-A1XW_ausente.png` | invasión linfovascular | ausente | 22206 | 0.796 | 0.101 |

Total 7.4 MB sueltos, 7.3 MB comprimidos (`heatmaps_clam_vs_mammoth.zip`).

## Salvedades que NO deben caerse si repregunta

- Los nombres de tejido son **lectura visual nuestra, no anotación**: no hay etiqueta de
  tejido por parche, sólo la clínica de la lámina. Sign-off de patólogo pendiente.
- La mayor difusión de Mammoth en CDIS **no explica** que mida mejor ahí. Con n=7 no se
  atribuye.
- CDIS **no es una mejora establecida** (65 negativos en total).

## Defecto conocido del raster

Las 7 figuras llevan una raya larga en el título («TCGA-… — clase … (rama N)»), generada en
`scripts/clam_vs_mammoth_attention.py:236`. Es cosmético y viaja dentro del PNG. Arreglarlo
exige re-correr el forward de las 7 láminas (CPU, ~70 min, desatado por workaround J), porque
las atenciones no quedan cacheadas en disco.
