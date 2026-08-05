# Encargo 2 — «entrenar los slots de MAMMOTH con nuestro dataset»

> **Estado: ABIERTO.** Es la única pregunta del B8 que sigue esperando una respuesta de
> Sebastián. No bloquea a ningún otro objetivo.
>
> Extraído de `objetivos_sprint8.md` el 5-ago-2026, al reestructurar ese documento como
> índice. El texto de abajo es el análisis original del 27-jul más lo que se verificó
> después; el documento de objetivos ahora solo lo resume y enlaza.

## La pregunta

En la reunión del 24-jul-2026 pidieron «entrenar los slots de MAMMOTH con nuestro
dataset». **Verificado contra el código, eso ya está hecho**, así que el pedido tiene que
significar otra cosa y hay que preguntar cuál antes de ejecutar nada
([[surface-premise-discrepancies]]).

## Por qué la premisa no calza con el repo

- `slot_embeds` es un `nn.Parameter` del paquete `mammoth` instalado
  (`clam_testing2/MAMMOTH/src/mammoth/mammoth.py:281`), inicializado al azar
  (`orthogonal_` y después `xavier_uniform_`, L284-285) y **entrenado de punta a punta con
  el resto del modelo**. No hay pesos pre-entrenados del paper en juego.
- El job **4589** (17-18 jul) entrenó `CLAM_MB_Mammoth` **desde cero sobre nuestros
  splits** (`tipo_histologico_4clases_ci_100` de Sebastián y los `_ci_reform` nuestros).
  O sea: **los slots que analizamos ya están entrenados con nuestro dataset.**
- Refuerzo posterior (4-ago, job 4774): el control 30×10 del grid reprodujo al 4589 **bit
  a bit**, lo que confirma que esos slots salen de nuestro entrenamiento y no de ningún
  estado heredado ([[pipeline-determinista-bit-a-bit]]).

## Las tres lecturas posibles, en orden de plausibilidad

1. **Analizar sobre nuestras láminas privadas, no sobre TCGA.** Las 7 del Sprint 7 son
   **todas TCGA** (`interp_slides.json`), porque hacía falta el `.svs` para el overlay. Si
   lo que quieren es ver los slots sobre la cohorte de Environ, el pedido se solapa con el
   encargo 1 y se resuelve barriendo las privadas.
   **Parcialmente respondido por el encargo 1** (27-jul): el barrido de 1858 láminas-fold
   ya incluyó las tres cohortes y **la cohorte casi no mueve la aguja** (privado 162.7 vs
   TCGA 162.2 vs HistAI 154.9 slots efectivos). Si la lectura 1 es la correcta, la parte
   numérica ya está contestada; faltarían solo los **mapas** sobre láminas privadas, que sí
   exigen verificar disponibilidad de WSI.
2. **Una etapa de pre-entrenamiento de los slots**, por ejemplo auto-supervisada, o
   congelar el resto y entrenar solo el ruteo. Eso sí sería un objetivo nuevo, con
   pre-registro propio (regla 9) y `reviewer`.
3. **Que en la reunión haya quedado la impresión de que los slots venían del paper.** Si es
   esto, se cierra mostrando el `nn.Parameter`, el job 4589 y la reproducción bit a bit.

## Qué hace falta para cerrarlo

Preguntarle a Sebastián cuál de las tres es. Nada de código hasta entonces: la lectura 2 es
la única que implicaría entrenamiento, y entra por regla 9.

## Enlaces

- Barrido del encargo 1: [`q1_slots_escalado/resultados.md`](q1_slots_escalado/resultados.md)
- Determinismo del pipeline: [`grid_expertos_slots/resultados.md`](grid_expertos_slots/resultados.md)
- Memorias: [[mammoth-slot-routing-weight]], [[slot-unidad-de-morfologia]],
  [[reunion-24jul-encargos-b8]]
