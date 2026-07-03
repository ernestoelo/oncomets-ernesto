# 🗂️ Hoja de reunión — CPathAgent (magnificación) · jueves 2-jul

> Para tener al lado en la reunión. Pedagógica: cada término tiene su analogía. Leé de arriba a abajo.

---

## 0. La idea en 1 frase
CPathAgent es un **patólogo digital**: en vez de "mirar todo de un saque y escupir el diagnóstico" (lo que hace
nuestro CLAM), **navega** el portaobjetos como un humano — panorama a bajo aumento → zoom a lo sospechoso →
razona en palabras. Es interpretable y multi-escala.

---

## 1. Glosario mínimo (si me trabo, miro acá)
- **WSI** = el portaobjetos digitalizado. Imagen **gigapíxel** (~100.000 × 100.000 px). No entra en memoria → por eso todo el campo trocea.
- **Parche** = un cuadradito del WSI (nosotros: 256 px). La unidad chica.
- **Magnificación** = el aumento del microscopio. **Baja (2-4×)** = mucho tejido, poco detalle (¿dónde está el tumor?). **Alta (40×)** = pocas células, mucho detalle (¿núcleo atípico? ¿mitosis?).
- **Huge region** = pedazo GRANDE (16.000 px), escala intermedia entre parche y slide. *"Donde el patólogo realmente decide."*
- **MIL** = Multi-Instance Learning. Tenés la etiqueta de la **bolsa** (el paciente), NO de cada **ficha** (parche). Aprendés a diagnosticar sin que nadie te diga qué parche mirar. = **nuestro CLAM**.
- **LMM** = modelo multimodal tipo GPT-4V (mira imagen + escribe texto).
- **Agente** = modelo que toma **acciones** en secuencia (zoom, moverse) y decide sobre la marcha, en vez de responder de un tiro.
- **Instruction-tuning** = enseñarle al modelo el **formato de respuesta** con ejemplos (instrucción → respuesta ideal).
- **Destilación** = un modelo grande y caro (Gemini) **le genera los ejemplos** a uno más chico (CPathAgent), que aprende a imitarlo.

---

## 2. Cómo FUNCIONA (§3.1) — 3 etapas, ejemplo mama

```
  ①  ¿DÓNDE MIRO?        ②  ¿CÓMO RECORRO?       ③  MIRO Y CONCLUYO
     Global Screening       Navigation Planning     Multi-scale Reasoning
```

**① Global Screening** — achica el WSI (thumbnail) → grilla de regiones grandes. A cada una le pone:
severidad `s` (0-5) + flag `d` (¿la miro sí/no?). Descarta el fondo (adiposo, `s=0`), se queda con el tumor.

**② Navigation Planning** — por cada región tumoral, escribe un **recorrido** = lista de pasos `(x, y, m, o)`:
- `x,y` = dónde miro (coord. 0 a 1) · `m` = cuánto zoom (1.0 = región completa, 4.0 = zoom 4×) · `o` = qué busco (en texto)
- Patrón: empieza `m=1.0` (panorama) → hace zoom `m=2.5 → 4.0` en el mismo punto → se mueve a otro lado. **= el gesto del patólogo.**
- Es **autorregresivo** (paso a paso, cada uno condicionado por el anterior; puede adaptarse).

**③ Multi-scale Reasoning** — recorta TODAS las vistas del plan, se las mete JUNTAS, y razona sobre todas a la vez
(cruza escalas) hasta el reporte. *(No es zoom en vivo; es planear → recortar → razonar todo junto.)*

---

## 3. Cómo lo ENTRENARON (§3.2) — por qué es CARO
- Le enseñaron con **278.000 ejemplos** de "plan + razonamiento ideal".
- Esos ejemplos los escribió **Gemini-2.5-Pro** (destilación), **anclado al reporte real del patólogo** (dataset TCGA/HistGen) para no alucinar.
- Costo: **5.254 WSIs → 278K muestras, 8× GPU H800.** Nosotros: **1× A6000, sin reportes pareados de la cohorte privada, sin Gemini.**
- 🔑 **Moraleja:** el modelo es fuerte por el **DATO** (dataset enorme), no por la arquitectura (usa piezas estándar). → **confirma nuestra tesis: el cuello es el dato.**

---

## 4. Los NÚMEROS sin humo (§4)
- Clasificación WSI: CPathAgent **82.8%** vs ABMIL **79.9%** → **solo +2.9%**… y ese ABMIL YA usa fusión multi-escala → la magnificación hace casi todo, el agente casi nada.
- Eficiencia de datos: 88.1% con **5.254 slides** vs TITAN 91.9% con **335.645** (64× menos). Su venta real = "rinde con pocos datos", NO "rompe el techo".
- Ablación clave: aplicar la estrategia-agente a Gemini por prompting **EMPEORA 6.7%** → sin los datos caros, el agente no sirve.

---

## 5. ⭐ LA PALANCA PORTABLE (Apéndice C.1.2) — lo que SÍ nos sirve
Escondido en su baseline MIL: por cada región extraen features a **3 escalas** (parche 2048 + 4×1024 + 16×512),
las **promedian** en 1 vector por región → ABMIL/DSMIL normal. **Sin agente, sin LLM, sin Gemini.**
- = **"jugar con la magnificación"** de Sebastián. Hoy somos **escala única** (parche 256, un solo nivel, CONCH 512).
- Portable: re-extraer CONCH a ≥2 escalas y fusionar, **dentro de CONCH v1 512**, **CLAM intacto**, comparación **paired** vs single-scale.

---

## 6. 🎤 MI POSTURA (leer casi textual)
> "El agente CPathAgent no es factible para nosotros — 8× H800, 278K ejemplos de Gemini y reportes pareados que la
> cohorte privada no tiene; el propio paper muestra que la estrategia-agente por prompting empeora 6.7%. Pero su baseline
> esconde la palanca portable: **fusión de features multi-escala** (Ap. C.1.2), que es exactamente jugar con la
> magnificación — se queda dentro de CONCH, deja CLAM intacto y se prueba paired vs escala única. Y todo el paper
> refuerza nuestra tesis: el motor es el dato, no el modelo."

---

## 7. ❓ PREGUNTAS para Sebastián
1. ¿Confirmamos que "magnificación" = fusión de features multi-escala (Nivel 1), NO el agente LMM?
2. ¿A qué magnificación física extraemos HOY? (¿private/TCGA/HistAI todos al mismo nivel base?)
3. ¿Fusión por **promedio** (mantiene `[N,512]`, CLAM intacto) o **multi-token** (1 embedding por escala)?
4. ¿Sobre qué tareas probamos primero? (propuesta: invasión / patrón, donde el contexto espacial ES el diagnóstico)
5. ¿Hay reportes WSI pareados de la cohorte privada? (si no → agente descartado definitivamente)
6. ¿Cuánto tarda `conch_fe` por slide? (para estimar costo de re-extraer ~3.072 slides a 2-3 escalas)
