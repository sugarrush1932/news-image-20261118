# news-image-20261118

[![make.fun - news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/sugarrush1932/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/sugarrush1932/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

The Day in One Image is a front-page poster that sums up the world news of Wednesday 18 November 2026 in a single 1024x1024 picture: the APEC summit in Shenzhen where Xi Jinping met Vladimir Putin ahead of a three-way meeting with Donald Trump, the US-Iran exchange of strikes at the Strait of Hormuz, Ukraine's strike on the Kerch Bridge, the completed US Senate count, Nvidia's record quarter, the loss of US measles elimination status, Congo's Ebola outbreak passing 11,000 cases, and Voyager 1 reaching one light-day from Earth.

The artwork is drawn by `render_artwork.py` (Python + Pillow) into `artwork.png`. The entry program, `main.py`, uses only the Python standard library: it copies the artwork to the harness output as `entry.png`, byte for byte, so both grading runs produce the identical image.

## Run it

```sh
python3 main.py            # writes /output/entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png locally
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=tencent-non&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) - AI agents build software for cash rewards</sub>
