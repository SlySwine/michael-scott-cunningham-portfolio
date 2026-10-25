# Michael Scott Cunningham

[michaelscott.me](https://michaelscott.me) is served by GitHub Pages from the root of the main branch.

The approved portfolio source is in `site/`. It uses React, Vinext, and Three.js with Blender-authored models. The root contains the generated static site, so GitHub Pages does not need a server or build workflow.

## Update the site

Use Node.js 22.13 or later:

```sh
cd site
npm ci
npm run publish:static
npx tsc --noEmit
node scripts/verify-diorama.mjs
```

Review and commit both source and generated changes. Preserve `CNAME`, `.nojekyll`, and the Cloudflare Web Analytics integration in `site/app/layout.tsx`.

This release ports approved preview commit `691fddfdf9925e2cc5122877032d2a6bf337cd33` to static hosting, retaining the model toolbar, original name typography, six scenes, approved copy, and contact links.

## Diorama authoring and review

The six scenes are authored in [`site/blender/dioramas.blend`](site/blender/dioramas.blend), with a portable generator in [`site/blender/build_dioramas.py`](site/blender/build_dioramas.py). Each major workstation is a grouped assembly so transitions keep its related objects together. The native file has a separately editable scene for each environment.

From the repository root, with Blender 5.2 and Python with Pillow available:

```sh
blender --background --factory-startup --python site/blender/build_dioramas.py -- --review-angles
python3 site/blender/prepare_review.py
cd site
npm run publish:static
node scripts/verify-diorama.mjs
```

Use `--scene photography` to iterate on one scene, `--no-render` for export only, and `--resolution 880 --samples 24` for faster draft renders. Only a full six-scene build overwrites the native master. The generator writes the source GLBs; the review script creates matching WebP fallback posters.

Review the [before](docs/dioramas/before.jpg), [after](docs/dioramas/after.jpg), [overhead](docs/dioramas/plan.jpg), and [rear](docs/dioramas/rear.jpg) sheets. Per-scene render PNGs and Blender backup files remain local. The geometry checks cover base containment, photo equipment aim, and the repair tool's contact with the bicycle, alongside the existing interaction checks.
