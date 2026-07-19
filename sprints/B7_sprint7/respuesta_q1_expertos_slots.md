# Q1 — ¿cuántos expertos/slots usa Mammoth? (Sprint 7)

«Peso por slot» = `combine_weights`, la segunda softmax sobre los E·S=300 slots (`mammoth.py:411`). No es el top-k de parches por experto.

**Número efectivo** = exp(entropía de la distribución de pesos): sería 300 si el ruteo fuera perfectamente uniforme y 1 si colapsara en un solo slot. Se usa esta medida porque la softmax da peso positivo a todos los slots, así que contar «los que reciben algo» siempre daría el total.

## Respuesta corta

- Slots efectivos: **158.7 de 300**
- Expertos efectivos: **30.0 de 30**

## Por slide

| Tarea | Slide | Slots efect. | Slots p/50% | Slots p/90% | Expertos efect. | Expertos p/50% | Expertos p/90% | Top-5 slots |
|---|---|---|---|---|---|---|---|---|
| carcinoma_ductal_insitu_presente_ci_reform | `TCGA-A7-A4SB-01Z-00-DX1` | 89.7 | 18 | 100 | 30.0 | 15 | 27 | e21·s0, e3·s2, e2·s6, e13·s6, e12·s9 |
| carcinoma_ductal_insitu_presente_ci_reform | `TCGA-D8-A1XB-01Z-00-DX2` | 180.3 | 45 | 183 | 30.0 | 15 | 27 | e28·s4, e6·s9, e13·s6, e28·s5, e19·s9 |
| invasion_linfatica_vascular_ci_reform | `TCGA-D8-A1X5-01Z-00-DX2` | 162.4 | 39 | 175 | 30.0 | 15 | 27 | e6·s7, e15·s5, e19·s9, e15·s7, e26·s2 |
| invasion_linfatica_vascular_ci_reform | `TCGA-D8-A1XW-01Z-00-DX2` | 196.4 | 53 | 192 | 30.0 | 15 | 27 | e17·s0, e15·s5, e8·s9, e29·s3, e27·s4 |
| tipo_histologico_3clases_ci | `TCGA-AC-A8OS-01Z-00-DX1` | 156.0 | 36 | 157 | 30.0 | 15 | 27 | e12·s2, e5·s5, e24·s9, e11·s3, e28·s7 |
| tipo_histologico_3clases_ci | `TCGA-AO-A12D-01Z-00-DX1` | 178.3 | 46 | 173 | 30.0 | 15 | 27 | e12·s2, e19·s7, e24·s1, e21·s4, e3·s1 |
| tipo_histologico_3clases_ci | `TCGA-E9-A1NE-01Z-00-DX1` | 147.5 | 34 | 171 | 30.0 | 15 | 27 | e12·s2, e28·s5, e23·s2, e25·s1, e28·s8 |
