# Sprint 7 (B7) — Contexto de magnificación (pendiente; lanzar el próximo fin de semana)

> Registra lo que Sebastián dijo en la reunión 13-jul sobre magnificación + la matemática
> área↔magnificación↔parche (pregunta §6.2). **Marcado explícitamente qué es dato
> verificado vs qué es interpretación de Ernesto A VERIFICAR con Sebastián/el código**
> (regla 5). Conecta con el hallazgo B6 [[cohortes-magnificacion-fisica]] y el
> pre-registro `sprints/B6_sprint6/magnificacion_microcalc/prereg_magnificacion.md`.

---

## Lo que Sebastián reportó (13-jul)

- Detectó **slides a distinta magnificación** al generar los mapas de atención con CLAM
  (aparecían distintos niveles de zoom/escala). Dice que lo **parcheó hace ~2 semanas**.
  → **A VERIFICAR:** qué parche exactamente aplicó y dónde (¿en su pipeline de patching /
  extracción? ¿en qué script?). No darlo por cierto hasta ver el código o que lo confirme.
- **Enviará los papers de microcalcificaciones** (los de la semana pasada, para elegir la
  dimensión): hablan de **luz polarizada** y del **lobulillo (0.5–2 mm)**.
  → Al estudiarlos, **citar en qué párrafo/sección** se menciona cada punto antes de
  usarlos (regla 5). Enlaza con [[luz-polarizada-oxalato-birrefringencia]].

## Cómo lo entendió Ernesto (A VERIFICAR con Sebastián — NO darlo por cierto)

> Interpretación de Ernesto, a confirmar: TCGA está a **×40**; eligió un parche de **224**
> → cubre **menos área** que a ×20, así que **definió un parche más grande que cubra la
> misma área que a ×20**: **misma área física, cambia la resolución**.

Esto es consistente con la matemática de abajo, pero hay que confirmar el número de
parche que usó y si equivale a lo que ya pre-registramos en B6.

## §Q2 — La matemática área ↔ magnificación ↔ tamaño de parche (para la slide)

**La cantidad física clave es MPP** (microns per pixel, µm/px), no la magnificación ni el
`level`. La magnificación (×20, ×40) es proporcional a 1/MPP: más aumento = MPP más chico
= cada píxel ve menos micras.

Relación base (un parche cuadrado de `P` píxeles de lado):

```
lado_físico (µm)  =  P (px)  ×  MPP (µm/px)
área_física (µm²) =  (P × MPP)²
```

**MPP verificado por cohorte a level 0** (openslide, 10-jul, [[cohortes-magnificacion-fisica]]):

| Cohorte | MPP level0 (µm/px) | Magnif ≈ | 256 px cubren | 224 px cubren |
|---|---|---|---|---|
| TCGA | 0.2325 | ×40 | 59.5 µm | 52.1 µm |
| Privado | 0.465 | ×20 | 119.0 µm | 104.2 µm |
| HistAI | sin MPP confiable (placeholder) | ¿? | no recuperable | excluido |

→ El pipeline actual (parche 256 @ level0, resize a 224 para CONCH) ya mete un
**confound 2×**: un parche mide el **doble de tejido** en privado que en TCGA. A CONCH se
le da TCGA a ~×40 (2× su nativo esperado). Ese es el hallazgo B6.

**La lógica de Sebastián, en números (A VERIFICAR):** para que un parche de TCGA (×40)
cubra la misma **área física** que un parche de 224 px a ×20 (104.2 µm de lado), hay que
agrandar el parche en TCGA:

```
P_TCGA = lado_físico_objetivo / MPP_TCGA = 104.2 µm / 0.2325 (µm/px) ≈ 448 px
```

Es decir: **448 px @ ×40 cubren el mismo campo (104 µm) que 224 px @ ×20**. Como MPP
difiere 2×, el parche escala 2× (224→448). Después se baja 448→224 para CONCH → **misma
área física capturada, distinta resolución nativa** (TCGA la captura más fina y luego se
downsamplea). Eso es exactamente "misma área física, cambia la resolución".

**Regla general:** para igualar el campo de visión físico entre cohortes de distinto MPP,
el tamaño de parche en píxeles escala **inversamente al MPP**:
`P_cohorte = lado_físico_objetivo / MPP_cohorte`.

## Reconciliación con el pre-registro B6 (a revisar con Sebastián)

- El pre-registro B6 (`prereg_magnificacion.md`) parametriza la pirámide en **µm/px
  físicos**: escala fina **112 µm** + contexto **512 µm** por cohorte.
- El "igualar a ×20" de Sebastián apunta a un campo de ~**104 µm** (224 px @ ×20) → cae
  cerca de nuestra escala fina (112 µm). **A confirmar:** ¿el parche de Sebastián es
  equivalente a la escala fina pre-registrada, o define solo una escala (no la pirámide
  multi-escala)? Su fix parece **normalizar la escala única entre cohortes**; nuestra
  pirámide **agrega** una escala de contexto encima. No son lo mismo; hay que ver cómo
  encajan.
- **Todo se parametriza en µm/px, no en `level`** — coincide con [[cohortes-magnificacion-fisica]].

## Slide a añadir al deck (§3 del prompt)

- [ ] Slide con la matemática de arriba: MPP, `lado_físico = P × MPP`, área física, y el
      ejemplo 224@×20 ≡ 448@×40 (misma área, distinta resolución). Que quede clara la
      relación µm/px ↔ área física ↔ píxeles. Benjamín va a preguntar.

## Pendientes (inputs de terceros)

- [ ] Recibir de Sebastián los **papers de microcalcificaciones** (luz polarizada,
      lobulillo 0.5–2 mm) → estudiarlos citando sección/párrafo.
- [ ] **Verificar con Sebastián** el parche exacto que aplicó y dónde (código).
- [ ] **Reconciliar** su parche con el pre-registro B6 (escala fina 112 µm / contexto 512 µm).
- [ ] Gate: el multi-escala se lanza el **próximo fin de semana** con **OK explícito de
      Ernesto** (gate d) — nada a GPU antes.

## Fuentes

- [[cohortes-magnificacion-fisica]] (MPP por cohorte, openslide 10-jul).
- `sprints/B6_sprint6/magnificacion_microcalc/{prereg_magnificacion.md, investigacion_magnificacion.md, histai_magnificacion.md}`.
- CLAUDE.md §"Pipeline OncoMets" (parche 256@level0 → 59µm TCGA / 119µm privado).
