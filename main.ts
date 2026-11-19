// main.ts - the entry program for news-image-20261118 (agent-fun/program/v1).
//
// The artwork ships in the repository as artwork.png, drawn by
// render_artwork.py. This program copies it, byte for byte, to
// entry.png in the output directory ($MAKEFUN_OUTPUT_DIR in the
// grader's container, /output otherwise), so both grading runs write
// the same bytes. Node standard library only; no network.
//
// The previous entry program was a Python main.py: it verified the
// artwork and copied it through a temp file, and the site's dev grade
// failed its run (run_completes) in about 240 ms even though the same
// code exits 0 under a faithful local simulation of the grader's
// docker invocation. This rewrite stays on the competition's primary
// runtime (node22, the runtime of the kit's starter and scorer) and
// keeps the runtime surface as small as possible: one read, one
// write, no verification that can fail on good bytes, no temp files.

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

// Find artwork.png without trusting any one staging convention: the
// directory this script itself lives in first (the repository root in
// the grader, where /bot is a read-only mount of the snapshot), then
// the tree the harness names in $MAKEFUN_BOT_DIR, then /bot outright.
// The bytes are the committed artwork (sha256
// 263c0f7291a8351b635dcb7124fd3eb75b9ab07114371ddb6e07e1822a751468);
// they are written out exactly as read, so the run cannot fail on a
// content check - the only hard failure left is no readable copy
// anywhere, which no fallback could rescue anyway.
function readArtwork() {
  const here = dirname(fileURLToPath(import.meta.url));
  const candidates = [join(here, 'artwork.png')];
  if (process.env.MAKEFUN_BOT_DIR) candidates.push(join(process.env.MAKEFUN_BOT_DIR, 'artwork.png'));
  candidates.push('/bot/artwork.png');
  let lastError;
  for (const candidate of candidates) {
    try {
      return readFileSync(candidate);
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError;
}

const data = readArtwork();

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
writeFileSync(join(outDir, 'entry.png'), data);
