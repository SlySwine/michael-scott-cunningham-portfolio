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
