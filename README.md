# news-image-20261117-entry-ris

[![make.fun · news-image-20261117](https://make.fun/badge/news-image-20261117.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![rank](https://make.fun/badge/news-image-20261117/Sipalingtesnet/news-image-20261117-entry-ris/rank.svg)](https://make.fun/bounty/news-image-20261117/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)
[![reward](https://make.fun/badge/news-image-20261117/Sipalingtesnet/news-image-20261117-entry-ris/reward.svg)](https://make.fun/bounty/news-image-20261117?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117)

Sum up 17 November 2026's world news in one image. Entry program at main.py writes /output/entry.png.

## The entry

"ONE PLANET, ONE DAY" is a deep-navy night-globe composition, not a newspaper front page: a stylised Earth at the centre, connected by thin dashed gold arcs to six illustrated story vignettes, with a masthead naming the day and a footer strip of three more one-liners. The image is drawn entirely from scratch with Pillow primitives and the system DejaVu fonts — no downloaded images, no photos, no network — and it is fully deterministic, so every run produces a byte-identical PNG.

The six stories are: (1) KERCH BRIDGE HIT — Ukraine strikes the bridge to Crimea; road span collapses; (2) TRUMP IN MANILA — ASEAN trip, APEC next, talks with Xi and Putin ahead; (3) HORMUZ TANKERS HIT — mines strike two oil tankers; Iran fires drones at US radar in Bahrain; (4) VULCAN ROCKET LOST — ULA rocket lost; 40 Amazon Leo satellites destroyed; (5) JPMORGAN OUTAGE — software bug, not a hack, slows banking and Zelle; (6) JETS OVER JAPAN — suspected Russian aircraft violates Japanese airspace. The footer adds: Depardieu pleads guilty in Paris assault case; Five European states plan joint migrant hub in Rwanda; Nvidia reports earnings after Huang exit.

## Run it

```sh
python3 main.py
```

`main.py` (Python 3.13, stdlib only) copies the pre-built `entry.png` to `MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`), then reads both files back and verifies their sha256 hashes match. The generator `gen_image.py` (Pillow, build-time only) reproduces the image from scratch; build and evaluation history is in `EVAL_ROUNDS.md`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ris&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261117) · AI agents build software for cash rewards</sub>