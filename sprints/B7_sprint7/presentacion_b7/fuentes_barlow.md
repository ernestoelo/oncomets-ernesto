# Barlow en el servidor Environ (instalación bajo containment)

> Fijado el 23-jul-2026. Resuelve el pendiente 1 del handoff
> `.handoffs/handoff_B7_20260723_2149.md`.
> Canónico del *porqué* tipográfico: memoria `[[deck-template-fuentes-embebidas]]`.

## Para qué

El texto nativo del `.pptx` ya sale en Barlow (`forzar_barlow()` en
`generate_b7_deck.py`). Lo que faltaba era **tener la fuente en el servidor**, por dos
motivos distintos:

1. Sin Barlow instalada, LibreOffice sustituye al rasterizar y **el QA tipográfico no es
   fiel**: se juzga una fuente que no es la que va a ver el que abra el deck.
2. Los rótulos que viven **dentro de los PNG de matplotlib** son píxeles y
   `forzar_barlow()` no los toca. Para que salgan en Barlow hay que regenerarlos con la
   fuente puesta.

## Dónde quedó

Todo bajo `clam_testing2/`, sin tocar `/usr/share/fonts/` ni
`~/.local/share/fonts/` (que es el home del usuario **compartido** `sdonoso`):

```
/media/administrador/Storage1/sdonoso/clam_testing2/fonts/
├── barlow/            18 TTF (Thin a Black, con itálicas), de google/fonts, OFL
├── fonts.conf         hereda /etc/fonts/fonts.conf y le suma barlow/
└── .fccache/          cache de fontconfig del workspace
```

`fonts.conf` es aditivo: incluye la config del sistema, así que activarlo **no le quita
ninguna fuente** a nada.

**Huella cero fuera del workspace.** Verificable:

| comando | resultado esperado |
|---|---|
| `FONTCONFIG_FILE=<...>/fonts.conf fc-list \| grep -ci barlow` | `18` |
| `fc-list \| grep -ci barlow` (sin la variable) | `0` |
| `FONTCONFIG_FILE=<...>/fonts.conf fc-list \| wc -l` | `574`, las del sistema intactas |

## Cómo usarla

**Prefijo para cualquier cosa que rasterice** (LibreOffice, `fc-list`, `fc-match`):

```bash
export FONTCONFIG_FILE=/media/administrador/Storage1/sdonoso/clam_testing2/fonts/fonts.conf
```

**Matplotlib** no lee fontconfig, hay que registrar los TTF a mano:

```python
import glob
from matplotlib import font_manager
import matplotlib
for f in glob.glob("/media/administrador/Storage1/sdonoso/clam_testing2/fonts/barlow/*.ttf"):
    font_manager.fontManager.addfont(f)
matplotlib.rcParams["font.family"] = "Barlow"
```

Verificado el 23-jul: matplotlib ve la familia `Barlow` y renderiza sin warning de
fallback. Los generadores de PNG (`scripts/slot_heatmaps_contraste.py`,
`scripts/clam_vs_mammoth_attention.py`) **todavía no llevan este bloque**: hay que
agregarlo cuando se decida regenerarlos.

## Cómo se bajó

El endpoint `https://fonts.google.com/download?family=Barlow` devuelve **HTML**, no un
zip (es la app JS). Los TTF salen del repo `google/fonts`:

```bash
cd /media/administrador/Storage1/sdonoso/clam_testing2/fonts/barlow
for f in Regular Bold Italic BoldItalic Medium SemiBold Light Black \
         ExtraBold ExtraLight Thin MediumItalic SemiBoldItalic LightItalic \
         BlackItalic ExtraBoldItalic ExtraLightItalic ThinItalic; do
  curl -sL -o "Barlow-$f.ttf" \
    "https://raw.githubusercontent.com/google/fonts/main/ofl/barlow/Barlow-$f.ttf"
done
```

Ojo con el workaround E de `CLAUDE.md`: bajar algo de afuera **se confirma con Ernesto
antes**. Acá lo autorizó el 23-jul.

## Qué NO cubre Barlow

Cuatro glifos del deck no existen en la fuente y caen al fallback de fontconfig
(DejaVu Sans). Comprobado con `fc-list ":family=Barlow:charset=<cp>"`:

| glifo | codepoint | dónde aparece |
|---|---|---|
| `→` | U+2192 | láminas 7, 9, 10, 13, 15, 23, 24 |
| `⟨` `⟩` | U+27E8/9 | lámina 7 |
| `≡` | U+2261 | lámina 22 |
| `‑` (guion duro) | U+2011 | lámina 20 |

**No hay nada que arreglar.** Se miró rasterizado en la 7 y la 22 y la sustitución es
indistinguible (son glifos geométricos), y PowerPoint hará exactamente lo mismo en la
máquina de quien presente. Es el límite real de "todo el deck en Barlow": el resto del
texto sí lo es.

Lo que Barlow **sí** cubre, y conviene no dudar de nuevo: `± × ÷ ² µ · « » ¿ ª Δ − …`
y todos los acentos del castellano.

## Verificación de punta a punta

```bash
S=<scratchpad>
D=.../sprints/B7_sprint7/presentacion_b7
export FONTCONFIG_FILE=/media/administrador/Storage1/sdonoso/clam_testing2/fonts/fonts.conf
libreoffice --headless -env:UserInstallation=file://$S/lo_profile \
  --convert-to pdf --outdir $S/raster "$D/CLAM_Sprint7.pptx"
pdffonts $S/raster/CLAM_Sprint7.pdf
```

Tiene que listar `Barlow-Regular` y `Barlow-Bold` **embebidos** (`emb = yes`). Si en vez
de eso aparecen Liberation, DejaVu o Carlito ocupando el cuerpo del texto, la variable de
entorno no llegó al proceso.

`DejaVuSans` en la lista **no es un defecto**: es el fallback de los cuatro glifos de
arriba. Distinto es verlo en los rótulos de los PNG, donde sí indica que la figura se
generó sin el bloque de matplotlib.

Y vale la advertencia de siempre: el chequeo programático da verde con defectos
visibles. Hay que **mirar las láminas** ([[deck-qa-puntos-ciegos-chequeo]]).
