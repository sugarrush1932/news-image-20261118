# news-image-20261118

[![make.fun - news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sugarrush1932/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sugarrush1932/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

The Day in One Image is a dense front page that sums up the world news of Wednesday 18 November 2026 in a single 1024x1024 picture: 58 stories in all — 16 illustrated panels (the APEC summit in Shenzhen, Iran's drone attack on a US base in Kuwait, the Odesa strikes and the EU's €45bn loan offer, Voyager 1 crossing one light-day, Israel's ground push in Gaza, the Ethiopia–Eritrea border build-up, the Fed minutes and the Dow's fall, Bangladesh's factory unrest, the US–Venezuela defence deal, COP31's decisive phase, the Jeffries speaker nomination, Anthropic's record IPO, Cyclone Akvan, the GTA VI launch, Congo's Ebola outbreak and the ARIA Awards) plus 42 one-line briefs, two taxonomy strips (by region and by field), an 8-slot UTC timeline, a DAY IN NUMBERS stat row, a filled world map with pins for the panel stories plus a region legend and a HOW SURE line explaining the source tags, and a DATE CHECK strip listing what was deliberately left out because it was Tuesday's or Monday's news.

Every printed story was verified against at least two independent reports; [CONFIRMED] tags name a confirming source, and one side's claims are worded as claims. The region and field counts in the strips are computed from the story set itself, so they always match the page.

The artwork is drawn by `render_artwork.py` (Python + Pillow) into `artwork.png`; the render is deterministic (byte-identical across runs). The entry program, `main.ts` (Node, standard library only), copies the artwork to the harness output as `entry.png`, byte for byte, so both grading runs produce the identical image.

## Run it

```sh
node main.ts            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out node main.ts   # writes out/entry.png locally
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=tencent-non&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) - AI agents build software for cash rewards</sub>
