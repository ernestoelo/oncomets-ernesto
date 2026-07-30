# SI-MIL: la matemática, desarmada

> Material pedagógico producido el **30-jul-2026** a pedido de Ernesto, que ya había leído
> el paper y marcó las **ecuaciones 1 y 2** como las que no cerraban.
>
> **Este documento NO reemplaza a [`simil_estudio.md`](simil_estudio.md)**, que es el
> estudio del método (qué propone, qué reporta, contraste con lo nuestro, costos).
> Acá va solo la mecánica de las fórmulas y del diagrama, al nivel de detalle que hace
> falta para **explicarlas en una presentación**.
>
> Todo lo que sigue está verificado contra el PDF (`simil_kapse2024.pdf`, arXiv:2312.15010v2)
> y contra el código real de CLAM en `clam_environ/models/model_clam.py`. Nada de memoria.

---

## 1. El mapa de símbolos

| Símbolo | Qué es | Nuestro número real |
|---|---|---|
| `N` | cuántos parches tiene la lámina | 2793 a 28170 (B7 §3) |
| `D` | ancho del vector de un parche en el espacio **profundo** | 512 con CONCH (ellos: DINO ViT-S) |
| `d` | ancho del vector en el espacio **PathExpert** | 246 features con nombre |
| `K` | cuántos parches sobreviven al Top-K | 20 |

**Trampa de notación a desarmar de entrada:** `D` mayúscula y `d` minúscula son **dos
espacios distintos** y el paper alterna sin remarcarlo. `D` es lo ilegible (números que
eligió una red para sí misma). `d` es lo legible (246 mediciones de núcleos con nombre de
patólogo). Las ecuaciones 1 y 2 viven enteras en `D`; la rama interpretable vive en `d`.

**Las ecuaciones 1 y 2 no son de SI-MIL.** Son la §3.1, titulada *Conventional MIL*: el
paper escribe primero lo que ya existía. Es decir, es CLAM (casi) en la notación de ellos.

---

## 2. Ecuación 1

```
g̃_i = H(g_i);      α_i = A^p(g̃_i);      i ∈ {1, 2, ... N}          (1)
```

### 2.1 La bolsa

La lámina se parte en `N` parches y cada uno se vuelve un vector `g_i ∈ R^D`. El conjunto
es la **bolsa de instancias**, y "bolsa" es literal: es un conjunto **sin orden**. Si se
permutan los parches, la predicción tiene que salir igual. Esa exigencia es la que fuerza
toda la maquinaria posterior: no se puede usar nada que dependa de la posición, así que
hace falta una operación que resuma `N` fichas en una sola sin mirar el orden.

En nuestro pipeline la bolsa es literalmente el `.pt` de la lámina, de forma `[N, 512]`.

### 2.2 El proyector `H(·)`

**Analogía**: cada `g_i` es una ficha de 512 números que escribió CONCH para su propio
objetivo, que no es nuestra tarea. `H` es una **traducción aprendida**: reescribe la ficha
midiéndola contra varas que se aprenden durante el entrenamiento de *nuestra* tarea.

**En CLAM es una línea de código**, [`model_clam.py:191`](../../../clam_environ/models/model_clam.py):

```python
fc = [nn.Linear(size[0], size[1]), nn.ReLU(), nn.Dropout(dropout)]
```

Con nuestros argumentos `size[0] = size[1] = 512`, o sea `H: R^512 → R^512`.
**Ese `nn.Linear` es exactamente la capa que Mammoth reemplaza por la mezcla de expertos.**
El sprint 7 entero y el encargo 1 del sprint 8 se trataron de esta letra.

### 2.3 La atención por parche `A^p(·)`

**Analogía**: hay un presupuesto de importancia del 100 % para repartir entre las `N`
fichas. La atención pone un puntaje crudo a cada una y después convierte los `N` puntajes
en porcentajes que suman 1.

El superíndice `p` es de *patch*, y está ahí porque en la ecuación 4 aparece un hermano
`A^f` de *feature*. Dos atenciones sobre ejes distintos.

**Sobre qué eje normaliza (el detalle que importa).** El paper dice *"a parameterized
module with softmax activation"*, y la softmax corre sobre los `N` parches:

```
Σ_{i=1}^{N} α_i = 1
```

Consecuencia práctica: **la atención de un parche depende de los demás parches de la
lámina**. No es una propiedad del parche, es su tajada del presupuesto. El mismo tejido en
una lámina de 3000 parches y en una de 28000 recibe atención distinta. En CLAM es
[`model_clam.py:213`](../../../clam_environ/models/model_clam.py), `A = F.softmax(A, dim=1)`,
con el comentario `# softmax over N` puesto por los propios autores.

---

## 3. Ecuación 2, que es donde estaba el nudo

```
Ŷ_g = ψ( Σ_{i=1}^{N} C(α_i · g̃_i) )                                  (2)
```

Dos ingredientes nuevos: `C(·)`, el predictor, que toma una ficha y devuelve el **logit**
(el puntaje a favor de la clase, antes de volverlo probabilidad); y `ψ`, la activación
final (sigmoide, porque todas sus tareas son binarias).

### 3.1 Por qué no se entiende leyéndola

Porque parece decir lo obvio (multiplicá por la atención, sumá, clasificá) y en realidad
dice algo muy específico sobre **el orden de dos operaciones**.

**Orden A, agregar y después clasificar.** Es ABMIL clásico y es CLAM:

```
Ŷ = C( Σ_i α_i · g̃_i )
```

Primero se funden los `N` parches en **una sola ficha promedio** (promedio ponderado por
atención) y a esa ficha se le aplica el clasificador. En CLAM son dos líneas separadas:
`M = torch.mm(A, h)` ([`model_clam.py:239`](../../../clam_environ/models/model_clam.py))
funde, y `logits[0, c] = self.classifiers[c](M[c])`
([`model_clam.py:243`](../../../clam_environ/models/model_clam.py)) clasifica lo fundido.

**Orden B, clasificar y después agregar.** Es la ecuación 2, y se llama *Additive MIL*
(Javed et al., referencia [24] del paper):

```
Ŷ_g = ψ( Σ_i C(α_i · g̃_i) )
```

El clasificador se aplica **`N` veces, una por parche**, y lo que se suma no son fichas:
son `N` puntajes. La diferencia tipográfica es dónde cierra el paréntesis de `C`. Esa es
toda la diferencia conceptual.

### 3.2 La analogía que funcionó

**Orden A, la licuadora.** Se echan las cuatro frutas a la licuadora en su proporción, se
licúa, queda **un solo jugo**, se prueba y se dictamina "ácido, puntaje −0.1".

**Orden B, la libreta.** Se prueba cada fruta por separado, ya multiplicada por su
proporción, y se anota su puntaje. Se suma la columna. Total: −0.1.

El veredicto es el mismo número. Lo que no es el mismo es **lo que queda en la mano al
terminar**. Y lo que no se puede deshacer: una vez licuado no hay manera de separar el jugo
en frutas. Uno se acuerda de las proporciones que usó, pero **la proporción dice cuánta
fruta se puso, jamás si esa fruta era dulce o ácida**.

### 3.3 Mini ejemplo numérico, los dos órdenes sobre los mismos datos

Cuatro parches, fichas de dos números para poder hacerlo a mano, `C` lineal con
`w = (1, −2)` y sin sesgo:

```
g̃₁ = (3, 1)   α₁ = 0.6
g̃₂ = (1, 0)   α₂ = 0.1
g̃₃ = (0, 2)   α₃ = 0.1
g̃₄ = (2, 2)   α₄ = 0.2
```

**Orden A:** `M = 0.6·(3,1) + 0.1·(1,0) + 0.1·(0,2) + 0.2·(2,2) = (2.3, 1.2)`,
después `logit = 1·2.3 + (−2)·1.2 = −0.1`.

**Orden B:**

| parche | `α_i · g̃_i` | `C(α_i · g̃_i)` |
|---|---|---|
| 1 | (1.8, 0.6) | **+0.6** |
| 2 | (0.1, 0.0) | **+0.1** |
| 3 | (0.0, 0.2) | **−0.4** |
| 4 | (0.4, 0.4) | **−0.4** |

Suma: `+0.6 + 0.1 − 0.4 − 0.4 = −0.1`. **El mismo número.**

**Y ahí está el punto:** el orden B deja los cuatro sumandos en la mano. El orden A produce
un `−0.1` y un vector de atención que dice "el parche 1 se llevó el 60 %". El orden B
produce un `−0.1` **desarmado** en cuatro contribuciones que suman exacto.

Mirá los parches 3 y 4: el 4 tiene **el doble** de atención que el 3 y contribuyen **lo
mismo**. Si la atención fuera un proxy de la contribución esa fila sería imposible.

### 3.4 Qué queda en memoria después de un forward

| | Orden A (CLAM) | Orden B (ec. 2) |
|---|---|---|
| ficha fundida `M` | sí, `[512]` | no existe |
| logit final | un número | un número, **el mismo** |
| desglose por parche | **no existe** | `N` números **con signo**, suman exacto el logit |
| atención `α` | `N` números, todos positivos, suman 1 | igual |

La fila que decide todo es la tercera. En el orden A, `M = torch.mm(A, h)` colapsa
`[N, 512]` en `[512]`: el eje de los parches se pierde **antes** de que el clasificador
opine. El clasificador nunca vio parches, vio un promedio.

### 3.5 Por qué la atención no rescata lo perdido

Porque **`α` sale de una softmax, así que todos sus valores son positivos**. Un número
positivo expresa *cuánto*, nunca *hacia dónde*.

**El caso extremo**, que es el que le preocupa al paper:

| parche | `α` | `α·g̃` | contribución |
|---|---|---|---|
| 1 | **0.6** | (0, 1.8) | **−3.6** |
| 2 | 0.2 | (0.8, 0) | +0.8 |
| 3 | 0.1 | (0.5, 0) | +0.5 |
| 4 | 0.1 | (0.6, 0) | +0.6 |

Total −1.7. El parche 1 se llevó el 60 % de la atención **y es el que más empuja en contra**
de la clase positiva. Un mapa de calor hecho con `α` le pinta un rojo intenso encima, y un
patólogo lee "acá el modelo encontró la evidencia" cuando el modelo lo usó como evidencia
de lo contrario. El orden A no puede detectar ese caso ni descartarlo. El orden B lo tiene
escrito.

Eso es el *spatial credit assignment* que el paper menciona en la §3.1 sin explicar:
repartir el crédito de la predicción entre las regiones, **con signo y magnitud**, de manera
exacta y no aproximada.

### 3.6 Tres precisiones honestas

1. **Los dos órdenes dieron el mismo número porque `C` es lineal.** Con `C` lineal sin
   sesgo, `Σ C(x_i) = C(Σ x_i)` por definición de linealidad, y la diferencia entre órdenes
   es puramente conceptual (se obtiene el desglose gratis). Si `C` fuera un MLP, los dos
   órdenes darían números **distintos** y serían dos modelos distintos.
2. **El sesgo rompe la equivalencia aunque `C` sea lineal**: sumar `b` una vez no es sumar
   `b` `N` veces. Con `N = 28170` no es redondeo. Por eso en la ecuación 9 el `+ b` aparece
   **fuera** de la suma (ver §6.3).
3. **`ψ` va después de la suma**, y no es cosmético: el desglose vive en el espacio de los
   **logits**, donde las contribuciones se suman limpio. Si `ψ` estuviera adentro se
   sumarían probabilidades y el desglose perdería sentido. Toda la interpretabilidad del
   paper se apoya en que la parte aditiva queda antes de la activación.

---

## 4. Dónde queda CLAM parado (verificado en código)

| Ecuación 1 y 2 | En `CLAM_MB` | Línea |
|---|---|---|
| `H(·)` | `nn.Linear(512, 512)` + ReLU + Dropout | 191 |
| `A^p(·)` | `Attn_Net_Gated`, softmax sobre `N` | 193 y 213 |
| `C(·)` | `nn.Linear(512, 1)`, uno por clase | 198 |
| el orden | **A**: funde y después clasifica | 239 y 243 |

Tres diferencias con la §3.1, para no confundir el paper con nuestro modelo:

- **CLAM usa el orden A**, no el aditivo. Curiosidad real: como su `C` es lineal, el logit
  de CLAM **se podría** desarmar por parche a posteriori. La diferencia con SI-MIL es que
  ahí el desglose **es la definición del modelo**, no algo que uno deriva después. Esa
  distinción entre *interpretable por construcción* y *explicado después* es la tesis
  entera del paper.
- **CLAM tiene una atención por clase** (el `MB` de multi-branch, `A` es `n_classes × N`),
  mientras la ecuación 1 escribe una sola `α_i` por parche.
- **CLAM devuelve `A_raw` pre-softmax** (línea 212) y tiene las ramas de instancia con la
  pérdida SVM, que no existen en esta formulación. Las ecuaciones 1 y 2 son una versión más
  **limpia** que CLAM, no más compleja.

### 4.1 Lo que esto acota de nuestros heatmaps del B7

Nuestros mapas de calor de CLAM contra Mammoth son mapas de **atención**. Dicen dónde miró
el modelo. **No dicen hacia qué clase empujó lo que miró**, y por lo de §3.5 no lo pueden
decir: `α` es positiva siempre.

Eso **no invalida** el B7: lo que comparamos fue precisamente *dónde mira* cada modelo, y
esa pregunta la atención sí la responde. Pero marca el límite exacto de esos mapas, y es el
mismo límite que el paper señala en su §1 cuando dice que la atención es *demasiado gruesa*
para explicar en términos de patología. **Al presentar, no decir "acá el modelo encontró
el tumor"; decir "acá el modelo puso su atención".**

Hermana de [[heatmap-atencion-no-es-per-experto]], que acota otra cosa del mismo mapa (no
es per experto). Memoria: [[mil-orden-aditivo-vs-agregado]].

---

## 5. La Figura 2 (página 4), leída como recorrido de un tensor

Tres paneles: **(a)** el mapa completo abajo a la izquierda, **(b)** y **(c)** a la derecha,
que son **zooms** de dos cajas de (a). Orden de lectura correcto: (a) primero como mapa,
después los zooms.

### 5.1 Las dos columnas de entrada

Dos caminos paralelos que salen de la misma lámina:

- **Naranja.** La lámina cuadriculada, rotulada `N patches`, entra a `Deep feature
  extractor` y sale la pila `g₁ … g_N`, rotulada **`R^{N×D}`**, con la `D` dibujada como el
  **ancho** de los bloques.
- **Verde.** Las mismas regiones, rotuladas `N nuclei maps` (los núcleos ya segmentados por
  HoVer-Net), entran a `PathExpert feature extraction`, que lista sus tres familias
  (`Morphometric`, `Graph features`, `Heterogeneity`), y sale la pila `f₁ … f_N`, rotulada
  **`R^{N×d}`**.

**Lo que hay que retener, que es el 80 % de la figura:** son **dos descripciones del mismo
parche**. Misma cantidad de filas (`N`, mismos parches, mismo orden), distinto ancho.

| | ancho | quién eligió los números | ¿se puede leer? |
|---|---|---|---|
| naranja `g_i` | `D` = 512 con CONCH | una red, para sí misma | no |
| verde `f_i` | `d` = 246 | la literatura de patología | sí, cada columna tiene nombre |

### 5.2 Panel (b), `Conventional MIL branch`

Es **el dibujo de las ecuaciones 1 y 2**:

```
R^{N×D} → [H] → R^{N×D} → [A^p] → (α₁ … α_N) → ⊗ → R^{N×D}
          Projector       Patch attention   circulitos azules
```

- El trapecio `H` (`Projector`) es el `H(·)` de la ecuación 1.
- El trapecio `A^p` (`Patch attention`) es el `A^p(·)`.
- Los **circulitos azules**, rotulados `Patch-attention scores`, son los `α_i`. **Hay `N`,
  uno por parche**, y suman 1 entre todos.
- El `⊗` es el `α_i · g̃_i`.

**El panel (b) nunca colapsa el eje de los parches**: la etiqueta dice `R^{N×D}` al entrar,
en el medio y al salir. El colapso ocurre después, ya en (a), cuando esa pila entra a `C`
(`Predictor`) y sale un solo `Ŷ_g`.

**Y esa caja `C → Ŷ_g` está dentro de un recuadro punteado que dice `Discarded in
inference`.** La rama profunda entera se descarta en producción. Está entrenada para una
sola cosa: producir buenos `α`.

### 5.3 El puente, que es el truco de la figura

En el centro de (a), dos matrices negras (`Patch-wise attention` arriba, las PathExpert
debajo) entran a la caja amarilla `PAG Top-K patch selection`. El movimiento clave:

> **Los índices salen del naranja. La selección se aplica al verde.**

La rama profunda no aporta ni un número a la predicción final. Aporta **20 enteros**:
cuáles parches valen la pena. Es la ecuación 3, donde `S_K` son *índices*, no features.

El embudo, con una lámina nuestra de 10000 parches:

```
naranja  10000 × 512 = 5 120 000 números  →  se descarta entero
verde    10000 × 246 = 2 460 000 números
                            ↓ se queda con 20 filas
verde       20 × 246 =       4 920 números  →  esto es lo que predice
```

De cinco millones de números ilegibles a **4920 que tienen nombre**. Ese embudo es la
figura.

### 5.4 Panel (c), `Self-Interpretable branch`, y por qué es el mismo dibujo girado

(b) y (c) tienen la **misma forma**: pila, trapecio, circulitos, `⊗`, pila. Lo único que
agrega (c) son dos circulitos con una **`T`**, uno al principio y otro al final.

```
R^{K×d} → T → R^{d×K} → [A^f: PF | G] → (β₁ … β_d) → ⊗ → T → R^{K×d}
20×246       246×20    PF-Mixer  Gated att.  circulitos verdes    vuelve a 20×246
```

**Por qué hace falta transponer.** La maquinaria de atención sabe hacer una sola cosa:
recibir una matriz y devolver **un puntaje por fila**. En (b) las filas eran parches, así
que devolvió `N` puntajes. Si se quiere un puntaje por *feature*, no hay que inventar nada:
**se gira la matriz para que las features pasen a ser las filas**, se pasa la misma
maquinaria, y salen `d` puntajes. Después se gira de vuelta. El texto lo confirma: `G(·)`
procesa cada fila de `M^T ∈ R^{d×K}` de forma independiente para determinar el `β_j` de
cada feature `d_j`.

**La confusión de eje que hay que matar** (la misma clase de error que costó
[[mammoth-dispatch-softmax-sobre-parches]]):

| | `α` (panel b) | `β` (panel c) |
|---|---|---|
| ¿cuántos hay? | `N`, uno por **parche** (miles) | `d` = 246, uno por **feature** |
| ¿qué contestan? | ¿qué región de la lámina importa? | ¿qué medición de núcleos importa? |
| ¿suman 1? | **sí**, softmax sobre `N` | **no** |

La última fila no es un detalle. `α` reparte un presupuesto fijo, así que subir uno baja los
demás. `β` termina en una **sigmoide** (ecuación 5), y una sigmoide no reparte nada: da un
número entre 0 y 1 para cada feature **por separado**. Son 246 compuertas independientes,
no una torta. Por eso el paper puede después empujarlas casi todas a cero con el percentil
`γ` y la temperatura `t`, que es lo que fuerza que el reporte tenga pocos renglones. Con una
softmax eso vendría impuesto de fábrica y no se podría regular.

`PF` (`PF-Mixer`) y `G` (`Gated att.`) dentro de `A^f` son la ecuación 4.

### 5.5 El recorrido completo, con las formas que rotula el diagrama

| paso | forma | qué pasó |
|---|---|---|
| entrada profunda | `R^{N×D}` | 10000 × 512 |
| entrada PathExpert | `R^{N×d}` | 10000 × 246 |
| tras `H` y `A^p` | `N` valores `α` | reparto de importancia entre parches |
| tras `TopK` | `K` índices | **20 enteros, único producto de la rama profunda** |
| filas seleccionadas | `R^{K×d}` | 20 × 246 |
| transpuesta | `R^{d×K}` | 246 × 20, para que las features sean filas |
| tras `PF` y `G` | `d` valores `β` | 246 compuertas independientes |
| escalada y de vuelta | `R^{K×d}` | 20 × 246, cada columna atenuada o realzada |
| predictor lineal | `K` números | una contribución por parche, con signo |
| suma y `ψ` | 1 número | `Ŷ_f` |

De (c) sale la matriz ya escalada, entra a la caja `L` (`Linear predictor`) y produce
`Ŷ_f`, el modelo que sobrevive a la inferencia. Abajo al centro, `Loss L` recibe flechas de
`Ŷ_g` **y** de `Ŷ_f`: es la ecuación 10, la que hace que las dos ramas se entrenen juntas.
Sin ella serían dos modelos separados corriendo en paralelo.

---

## 6. Ecuaciones 3 a 10, transcritas literales

**Estas todavía NO se explicaron con Ernesto** (la sesión cerró después de la Figura 2). Se
transcriben acá verificadas contra la página 4 y 5 del PDF para que no haya que
re-extraerlas, junto con las notas de lectura que ya salieron.

### 6.1 Las fórmulas

```
S_K = TopK(α, K)                                                        (3)

β_j = G(PF(M^T));            j ∈ {1, 2, ... d}                          (4)

β_j = (β_j − Pr_γ(β)) / std(β);      β_j = 1 / (1 + e^{−β_j × t})       (5)

M'_ij = β_j × M_ij;          i ∈ {1,2,...K};  j ∈ {1,2,...d}            (6)

M''_i = Σ_{j=1}^{d} w_j M'_ij + b;    i ∈ {1,2,...K}                    (7)

Ŷ_f = ψ( Σ_{i=1}^{K} M''_i )                                            (8)

Ŷ_f = ψ( Σ_{i=1}^{K} Σ_{j=1}^{d} w_j β_j M_ij + b )                     (9)

L = L_CE(Y, Ŷ_g) + L_CE(Y, Ŷ_f) + λ L_KD(Ŷ_g, Ŷ_f)                      (10)
```

### 6.2 Dónde se pone denso, y cómo desarmarlo (plan, no ejecutado)

- **Ec. 3, el Top-K perturbado.** La pregunta real es *por qué* hace falta: el Top-K normal
  **no tiene gradiente** (es una operación de selección, escalonada). Usan el *perturbed
  Top-K* de Cordonnier et al. Analogía del ordenamiento duro contra el blando.
- **Ec. 4 y 5, el eje.** `β` es peso **por feature** (`d` = 246), no por parche. Ver la
  tabla de §5.4: es la misma clase de confusión de eje que costó una memoria entera en
  Mammoth.
- **Ec. 5, el percentil `γ` y la temperatura `t`.** Sirven para **forzar dispersión**, que
  pocas features expliquen la predicción, porque un reporte de 246 renglones no lo lee
  nadie. Puente conceptual con lo nuestro: **nosotros medimos dispersión sin forzarla**
  (29.98/30 expertos, 159.5/300 slots sobre 1858 láminas-fold).
- **Ec. 9 es la ecuación clave del paper**, no la 8: muestra que la predicción se desarma en
  `w_j · β_j · M_ij`, o sea contribución del parche *i* por su feature *j*. **Eso es el
  reporte que ve el patólogo.** Si Ernesto se queda con una sola ecuación, es esta.
- **Ec. 10, la destilación.** Aclarar la dirección: la rama interpretable persigue a la
  profunda. `L_KD` es el **error cuadrático medio** entre `Ŷ_f` y `Ŷ_g`, con `λ = 20`.

### 6.3 Dos notas de lectura verificadas

1. **El `+ b` de la ecuación 9 es una simplificación de notación.** Si se sustituye la
   ecuación 7 en la 8 se obtiene `ψ(Σ_i Σ_j w_j β_j M_ij + K·b)`, con el sesgo `K` veces,
   no una. La 9 lo escribe una sola vez. **No es un error de fondo** (`K·b` es otra
   constante y se reabsorbe), pero conviene tenerlo claro para no trabarse al derivarlo en
   el pizarrón. Es el mismo punto de §3.6.2.
2. **El stop-gradient de `L_KD` NO está en el paper principal**: está en el
   **suplementario** (*"Note that L_KD is utilized with stop-gradient since the goal is to
   align the performance of the Self-Interpretable branch to be close to high[-performing
   MIL branch]"*). Si se cita, citar el suplementario.

---

## 7. Qué quedó pendiente de explicar

- **Ecuaciones 3 a 10**, una por una, con el mismo tratamiento que la 1 y la 2 (analogía,
  después notación, después mini-ejemplo numérico). El plan está en §6.2.
- **Las secciones posteriores a las fórmulas**: §4 (experimentos, Tablas 1 y 2,
  ablaciones), §5.1 (interpretación local, reporte patch-feature, Tabla 3 del patólogo),
  §5.2 (interpretación global, silhouette, divergencia de Jensen-Shannon), §5.3 (dataset)
  y §6 (conclusión). Los números de las Tablas 1 y 2 ya están en
  [`simil_estudio.md`](simil_estudio.md) §3.

---

## 8. Insumos para el deck del B8

- **La figura original de la Fig. 2 va como imagen**, que es la única excepción a "todo
  nativo" de la convención de decks (CLAUDE.md, ADDENDUM B5): las figuras externas de un
  paper se insertan como imagen. Está en la **página 4** del PDF, ocupando la banda
  superior de la página.
- **Los diagramas propios** (el contraste orden A contra orden B, el embudo de §5.3, la
  tabla `α` contra `β`) van **nativos** con python-pptx, con la gramática de Deep-LLM-V
  ([[deck-gramatica-diagrama-deep-llm-v]]) y todo en Barlow
  ([[deck-template-fuentes-embebidas]]).
- **Candidatos a lámina visual** en lugar de bullets ([[deck-contenido-visual-no-bullets]]):
  el embudo de 5.1 M a 4920 números (cadena de bloques con la cuenta hecha), la licuadora
  contra la libreta (dos caminos), y la tabla de §3.4 (qué queda en memoria).
- **Las ecuaciones** se escriben con el mismo criterio que los diagramas de arquitectura:
  fórmula con dimensiones al costado, sin bullets ([[diagramas-arquitectura-pptx-editable]]).
- **Vocabulario prohibido**: rayas «—» y «–», la palabra «palanca», la expresión «al revés»
  ([[deck-estilo-sin-rayas-ni-palanca]]).
