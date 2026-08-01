# Pre-registro — ¿la atención de CLAM cae donde marcó el patólogo?

> Escrito el 1-ago-2026, **antes de correr nada**. Es el experimento del §4 de
> [`../tareas_geometricas/README.md`](../tareas_geometricas/README.md), que quedó planteado
> con hipótesis pero con la familia de checkpoint sin decidir. Esto cierra esa decisión y
> fija el estadístico.
>
> Etapa 0: **CPU, post-hoc, sin GPU, sin `sbatch`**. Inferencia sobre checkpoints congelados;
> no toca modelo ni training, así que la regla 9 no aplica en su forma de "cambio de código".
> Igual va pre-registrado porque la decisión del checkpoint es exactamente el grado de
> libertad que puede fabricar el resultado.

## 1. La pregunta

El patólogo dijo que en mitosis los núcleos son finos y dispersos y que a CLAM y a Mammoth
se les escapan **porque esos parches quizá no reciben atención suficiente**. Esa frase es
medible: ¿los parches que él marcó rankean alto en la atención de nuestros modelos ya
entrenados, o no se distinguen del resto de la lámina?

## 2. Hipótesis, fijadas antes de ver el número

- **H_primaria** (la del patólogo): los parches marcados **no** rankean mejor que el azar.
  El estadístico se queda en su valor nulo. Lectura: la atención no se concentra donde está
  la evidencia diagnóstica ⇒ el operador de agregación es parte del problema ⇒ empuja hacia
  la **familia A** (cambiar el operador, README §3.A).
- **H_alternativa**: rankean alto. Lectura: el modelo **sí** mira ahí, y entonces lo que se
  pierde está aguas arriba, en el vector de 512 que representa al parche ⇒ empuja hacia las
  **familias B y C** (campo de visión y unidad de representación) y **no** hacia A.
- **Caso mixto esperable y explícitamente contemplado**: que las regiones grandes (Tumor,
  necrosis) rankeen alto y los objetos celulares (Mitosis, núcleos de alto grado) no. Ese
  contraste es el resultado más informativo posible y por eso los grupos de control entran
  a la medición desde el diseño, no después.

Las tres lecturas están escritas antes de correr. Ninguna se decide mirando el número.

## 3. La decisión de checkpoint (el grado de libertad peligroso)

El problema tabulado en README §4: la lámina 129741 cae en `train` en los 5 folds de
**nuestro** k-fold, que es justo el de los checkpoints cuyo baseline citamos (Tier 0,
AUC 0.721). Verificado hoy, `data/splits_kfold/grado_mitotic_3clases_pth_100/splits_{0..4}_bool.csv`:
`129741,True,False,False` en los cinco.

Al revisar las corridas de Sebastián apareció una salida mejor que la disyuntiva binaria del
README. El mapa completo, verificado hoy:

| Corrida | Tarea / clases | Split | 129741 |
|---|---|---|---|
| `results_modelo/grado_histologico_mitotic_rate_s1` | privado, 4 clases | `splits/…_100` | **`val`** |
| `results_modelo_combined/…_combined_s1` | priv+TCGA, 4 clases | `splits/…_combined_100` | **`val`** |
| `results_modelo_combined_5fold/…_combined_s1` | priv+TCGA, 4 clases | `splits_5fold/…_combined_100` | **`val` en folds 0 y 2; `train` en 1, 3, 4** |
| `results_modelo_pth/…_pth_s1` | priv+TCGA+HistAI, 4 clases | `splits/…_pth_100` | `train` |
| `results/pathpt_etapa1/mitotic/clam_*_f{0..4}` (nuestro, Tier 0) | 3 clases | `data/splits_kfold/…` | `train` en los 5 |

La corrida 5-fold de Sebastián tiene la lámina en `val` en dos folds y en `train` en tres,
**dentro de la misma corrida**: mismo modelo, misma tarea, mismos hiperparámetros. Eso
convierte el estorbo en un control interno — la diferencia entre esos dos grupos mide cuánto
mueve el estadístico el solo hecho de haber visto la lámina.

**Se decide correr las tres familias, con roles asimétricos fijados ahora:**

- **Primario** — checkpoints donde 129741 **nunca se vio en entrenamiento**: `results_modelo`
  (privado), `results_modelo_combined`, y los folds **0 y 2** del 5-fold combinado. La
  conclusión del experimento sale de acá.
- **Control interno** — folds **1, 3 y 4** del 5-fold combinado (misma corrida, lámina vista).
  Sirve para una sola cosa: cuantificar el sesgo de haberla visto.
- **Corroboración** — nuestros 5 folds de Tier 0 (3 clases). Se reportan **rotulados como
  lámina de train** y su único papel es conectar con el baseline que citamos en README §2.e.
  **No** sostienen la conclusión.

`results_modelo_pth` se excluye: la lámina está en `train` y no aporta nada que el control
interno no dé mejor.

Correr las tres es barato (CPU, once checkpoints sobre 4799 parches) y la regla operativa del
proyecto es preferir la matriz completa antes que omitir una prueba barata
([[completitud-matriz-por-defensibilidad]]). Lo que **no** se hace es elegir cuál reportar
después de ver los números: los roles quedan escritos arriba.

## 4. El estadístico

- Atención: `A_raw = model(x, attention_only=True)` → `(n_classes, N)` **pre-softmax**, y se
  aplica `softmax(A_raw, dim=1)` sobre los N parches (CLAUDE.md, hechos validados). CLAM_MB
  tiene **una cabeza por clase**, así que todo se reporta **por clase**, más un resumen para
  la clase verdadera de la lámina y para la predicha.
- Clase verdadera de 129741 = `score_3`. Índice **3** en las corridas de 4 clases
  (`{no_identificado:0, score_1:1, score_2:2, score_3:3}`) y **2** en la nuestra de 3 clases
  (`{score_1:0, score_2:1, score_3:2}`). Ambos órdenes verificados contra el CSV de labels con
  la regla de `--auto-label-dict` (orden alfabético).
- **Estadístico primario: AUC de ranking** = probabilidad de que un parche anotado reciba más
  atención que un parche no anotado tomado al azar (equivalente a Mann-Whitney U normalizado).
  Valor nulo = **0.5**. Se elige sobre "percentil mediano" porque no depende de la escala de
  la atención y es directamente comparable entre checkpoints y entre clases.
- Se reporta además el **percentil mediano** de los parches anotados, que es la forma en que
  el README §4 enunció la medida y la que se lee más fácil en una lámina del deck.
- **Grupos**: `Mitosis` (28 parches) y `Nucleos alto grado` (13) son los grupos de interés.
  `Tumor` (45), `Tejido Adiposo` (27), `Immune cells` (21), `necrosis` (16) y `Stroma` (10)
  entran como **contraste**, no como control negativo — ver §5.

### El nulo, que no es el obvio

Permutar la etiqueta de parche al azar es un nulo **demasiado fácil de rechazar**: los parches
anotados son espacialmente contiguos (28 parches salen de 26 marcas, muchas vecinas) y la
atención tiene estructura espacial, así que cualquier mancha compacta "gana" contra un nulo
que rompe la contigüidad. El p-valor de Mann-Whitney sería optimista y lo sé antes de correrlo.

Nulo que sí se usa: **traslación rígida aleatoria** de la máscara de parches anotados sobre la
grilla de la lámina (múltiplos del paso de 256 px, verificado como la moda del paso entre
coords contiguas, [[patch-size-desde-geometria-h5]]), quedándose con las traslaciones donde al
menos el 90 % de los parches desplazados sigue cayendo sobre parches extraídos. Preserva forma,
tamaño y contigüidad del grupo, y solo mueve **dónde** está. 2000 traslaciones. El p-valor es
la fracción de traslaciones con AUC ≥ la observada. Se reportan los dos p (permutación simple
y traslación) para que se vea la diferencia.

## 5. Lo que NO se va a afirmar

- **Una lámina y 28 parches describen, no establecen.** Un anotador, un caso.
- **Los parches sin marca no son negativos.** El patólogo solo marca donde la evidencia es más
  clara ([`../anotaciones_patologo/hallazgos.md`](../anotaciones_patologo/hallazgos.md) §3).
  Esto tiene una consecuencia direccional que conviene dejar dicha: mitosis no marcadas dentro
  del conjunto "no anotado" **acercan la AUC medida a 0.5**. O sea que el sesgo es
  **conservador** — un AUC alto es creíble, pero un AUC en 0.5 es ambiguo entre "el modelo no
  mira ahí" y "el modelo mira mitosis que el patólogo no marcó". H_primaria **no se puede
  confirmar** con este diseño, solo se puede **no rechazar**. Eso se escribe en el resultado.
- **Un parche no marcado con atención alta no cuenta como error del modelo**, por lo mismo.
- Las clases de contraste (Tumor, Stroma, …) **no son control negativo**: son regiones
  grandes marcadas con otro criterio. Un AUC alto en Tumor no valida el método, solo muestra
  que la atención tiene estructura y sabe distinguir tejido.

## 6. Salidas

`sprints/B8_sprint8/atencion_vs_patologo/`: `resultados.md`, `auc_por_checkpoint.csv`,
`percentiles_por_parche.csv`, `run.log`, y las figuras que salgan. Script reproducible en
`scripts/atencion_vs_anotaciones.py`.
