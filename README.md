# 2017 recap — SNH48 stage performance stats (work in progress)

[![code license: MIT](https://img.shields.io/badge/code%20license-MIT-blue.svg?maxAge=2592000)](COPYING)
[![assets license: CC0](https://img.shields.io/badge/assets%20license-CC0-blue.svg?maxAge=2592000)](COPYING)

Current summary (not up-to-date; also stats for 4th Election tiers are apparently nonsense at this moment):

![](https://rawgit.com/SNH48Live/2017-recap/master/images/svg/summary.svg)

A full demo from the master branch can be found at <https://snh48live.org/2017-recap>.

# Usage

Look into `bin`.

# Notes

- SVG to PNG basically requires Chrome/Blink. DOM elements are rendered with slightly different heights/widths in Firefox/Gecko, resulting in clipped images. In Safari the canvas can't even be converted to PNG — it is tainted despite loading a first-party SVG, which I believe is due to [this bug](https://bugs.chromium.org/p/chromium/issues/detail?id=294129). (Chrome suffers from the same bug if the SVG is loaded through an HTTP request from the same origin, but not when the SVG is directly embedded in the HTML.) By the way, I didn't bother to include an `HTMLCanvasElement.toBlob` polyfill. Maybe I should, for Opera/Blink, with which I didn't test.

- I convert SVG to PNG via the browser (`bin/generate --png`). This makes full automation hard; PNG images are download from the browser, and one has to run `bin/collect` to crop and put them in place.

  Sure there are fully automated solutions, but I found none that I was happy with. There's the PhantomJS-based [svg2png](https://github.com/domenic/svg2png) which seemed to the closest, but its canvas scaling is crap (nonexistent), and one has to manually patch it to zoom in on the canvas (the patch is simple, but having to patch an npm package is apparently not considered frictionless development process) — I really need to blow up the canvas 4x to get crispy text rendering, even on latest Chrome, with a `<canvas>` tag, which is the magic behind the current implementation.

  Also, PhantomJS uses a very old WebKit (looking at PhantomJS 2.1.1, it is using WebKit 538.1 from 2014), which comes with its own rendering idiosyncrasies. It doesn't render the same as latest Chrome/Blink, and Chrome/Blink being the dominant web browser (yeah, I refuse to live in a mobile-first world...), I'll take its rendering over that of PhantomJS any other day. PhantomJS doesn't seem to have a bright future anyway; [its (lead) maintainer stepped down citing Headless Chrome last month (April 2017)](https://groups.google.com/forum/#!topic/phantomjs/9aI5d-LDuNE). I haven't checked out Headless Chrome yet. I should at some point.

  Last but not least, `svg2png` performance is shit.

# TODOs

- Populate `data/performances.raw.json` gradually and at the end of the year.
- Grep for the string `TODO` in the code base.

# License

- Code (files outside `images`) are licensed under MIT;
- Assets (files inside `images`) are licensed under CC0.

See [`COPYING`](COPYING) for details.
