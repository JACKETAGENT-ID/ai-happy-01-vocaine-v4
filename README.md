# vocaine — ai-happy-01 entry

**The moment:** at dusk, a tiny mouse in a smart little coat stands
in a green leaf boat floating over a sunflower field, baton raised,
conducting an orchestra of glowing fireflies. Their light swirls
into golden trails — the music made visible — while the sunflowers
below glow amber in the last warm light.

It is a small creature completely in charge of a big, joyful
sound: that contrast is the delight. No words, just warmth, light,
and one very proud conductor. The composition uses big, clear
shapes (mouse, leaf, sunflowers, firefly glow) so the idea still
reads instantly at thumbnail size.

## How it works

The artwork is bundled in this repo as `image.png` (1024×1024 PNG).
`main.py` (Python 3.13, standard library only) validates the file —
PNG magic bytes, IHDR dimensions, file-size limit, and a structural
chunk walk — then copies it byte-for-byte to the output, which makes
every run produce identical bytes.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png
```

If `MAKEFUN_OUTPUT_DIR` is not set, the output defaults to `/output`.
