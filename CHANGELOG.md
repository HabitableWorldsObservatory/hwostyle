# Changelog

## [1.7.0](https://github.com/HabitableWorldsObservatory/hwostyle/compare/v1.6.0...v1.7.0) (2026-10-20)


### Features

* **colormaps:** Tol image roles, pupil map, gray mask; deprecate high_dynamic_range and envelope ([520c42c](https://github.com/HabitableWorldsObservatory/hwostyle/commit/520c42c3024d3140c4f88a4ac3a9531de832f61f))
* **motifs:** add default motif table and zodi role ([4355cce](https://github.com/HabitableWorldsObservatory/hwostyle/commit/4355cce386bfec3cc417f647a6131cccaf2baa57))
* **palettes:** paper roles on Tol muted, Tol light kept as tol-light ([497a5de](https://github.com/HabitableWorldsObservatory/hwostyle/commit/497a5de4e06d7e996d280a1f358f4d8918a7886d))
* **palettes:** tune role hexes per mode and add label inks and accepted pairs ([089503f](https://github.com/HabitableWorldsObservatory/hwostyle/commit/089503ff8bba66d4fb4c64c33dc925958a88c205))


### Bug Fixes

* **motifs:** accept dark model-negative and retune the paper star to clear the verdict orange ([f466d6b](https://github.com/HabitableWorldsObservatory/hwostyle/commit/f466d6b882c2302ed0e282f755f3d6017a342687))
* **motifs:** accept paper zodi-negative and prior-positive with a marker difference ([2234df0](https://github.com/HabitableWorldsObservatory/hwostyle/commit/2234df014943d85712a67ddec3446262a3482491))
* **motifs:** declare pair scopes, fill dark reference plane, tighten budget test ([5847c27](https://github.com/HabitableWorldsObservatory/hwostyle/commit/5847c277946c6fdc1583157aa9e90445cb64115c))

## [1.6.0](https://github.com/HabitableWorldsObservatory/hwostyle/compare/v1.5.0...v1.6.0) (2026-10-12)


### Features

* **roles:** add positive, negative, prior, posterior, truth roles and statistic colormap ([4c858fe](https://github.com/HabitableWorldsObservatory/hwostyle/commit/4c858fec42adbec3551fdbe43ed80aa1a0786131))

## [1.5.0](https://github.com/HabitableWorldsObservatory/hwostyle/compare/v1.4.0...v1.5.0) (2026-08-24)


### Features

* **colors:** add unsafe_pairs to name colliding palette pairs ([907a9c0](https://github.com/HabitableWorldsObservatory/hwostyle/commit/907a9c0335fd101168004e2fdbe73090c0c19ae1))
* **colors:** simulate color vision deficiency so palette safety is measurable ([6aab2a2](https://github.com/HabitableWorldsObservatory/hwostyle/commit/6aab2a291ebcb085842edd1e8d86291e5bec85a3))

## [1.4.0](https://github.com/HabitableWorldsObservatory/hwostyle/compare/v1.3.0...v1.4.0) (2026-08-12)


### Features

* **style:** brand roles and the opd semantic colormap key ([4e7a70f](https://github.com/HabitableWorldsObservatory/hwostyle/commit/4e7a70fdaa82361a64ce516b634550d70b048f5e))

## [1.3.0](https://github.com/HabitableWorldsObservatory/hwostyle/compare/v1.2.0...v1.3.0) (2026-08-11)


### Features

* **core:** add current_mode() and save_defaults() introspection ([3f624ee](https://github.com/HabitableWorldsObservatory/hwostyle/commit/3f624ee700b72f7fbab21363bedd731dad6db324))

## [1.2.0](https://github.com/HabitableWorldsObservatory/hwostyle/compare/v1.1.0...v1.2.0) (2026-07-29)


### Features

* Updating readout and intensity colormaps ([fbc1cb2](https://github.com/HabitableWorldsObservatory/hwostyle/commit/fbc1cb275075f72886fe1ff75dd78440f54c58c4))

## [1.1.0](https://github.com/CoreySpohn/hwostyle/compare/v1.0.0...v1.1.0) (2026-04-21)


### Features

* Add paper style and refactor into multiple files for matainability ([f74bd8e](https://github.com/CoreySpohn/hwostyle/commit/f74bd8eaf572b0c034e7987e966f3b8debe0b251))


### Bug Fixes

* Add tol-colors as a dependency ([e15bd90](https://github.com/CoreySpohn/hwostyle/commit/e15bd90cfdf1bc96df7af59124e195ca191c4ba4))
* Remove tight layout as default ([e2ca7f4](https://github.com/CoreySpohn/hwostyle/commit/e2ca7f489971ea247ae0867bb827fe95e81fdc10))

## 1.0.0 (2026-03-02)


### Features

* Initial setup ([fa40f01](https://github.com/CoreySpohn/hwostyle/commit/fa40f01a6dc3f3e4d9011ade329011d5f212b852))

## 0.1.0 (Unreleased)

### Features

- Dual-mode style system: `use("dark")` for talks, `use("light")` for papers
- Color palette with 6 named colors (cyan, pink, yellow, green, red, purple)
- Semantic colormap registry (`cmaps.intensity`, `cmaps.residual`, etc.)
- Context managers `dark()` and `light()` that auto-restore previous mode
- Custom brand colormaps: `hwo_intensity`, `hwo_diverging`
