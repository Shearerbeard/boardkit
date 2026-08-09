---
source: https://tailwindcss.com/docs/styling-with-utility-classes
date: 2026-08-09
artifact: doc-excerpt
license: Proprietary (Tailwind Labs Inc.; tailwindcss.com repo states it is not open-source licensed) - short quoted excerpt for internal eval only
note: Overview opening plus the why-not-inline-styles argument; user-named canonical clean technical writing. Fetched from the page's MDX source; JSX example components dropped, HTML code sample and all wording verbatim.
---

## Overview

You style things with Tailwind by combining many single-purpose presentational classes _(utility classes)_ directly in your markup:

```html
<div class="mx-auto flex max-w-sm items-center gap-x-4 rounded-xl bg-white p-6 shadow-lg outline outline-black/5 dark:bg-slate-800 dark:shadow-none dark:-outline-offset-1 dark:outline-white/10">
  <img class="size-12 shrink-0" src="/img/logo.svg" alt="ChitChat Logo" />
  <div>
    <div class="text-xl font-medium text-black dark:text-white">ChitChat</div>
    <p class="text-gray-500 dark:text-gray-400">You have a new message!</p>
  </div>
</div>
```

For example, in the UI above we've used:

- The [display](/docs/display#flex) and [padding](/docs/padding) utilities (`flex`, `shrink-0`, and `p-6`) to control the overall layout
- The [max-width](/docs/max-width) and [margin](/docs/margin) utilities (`max-w-sm` and `mx-auto`) to constrain the card width and center it horizontally
- The [background-color](/docs/background-color), [border-radius](/docs/border-radius), and [box-shadow](/docs/box-shadow) utilities (`bg-white`, `rounded-xl`, and `shadow-lg`) to style the card's appearance
- The [width](/docs/width) and [height](/docs/height) utilities (`size-12`) to set the width and height of the logo image
- The [gap](/docs/gap) utilities (`gap-x-4`) to handle the spacing between the logo and the text
- The [font-size](/docs/font-size), [color](/docs/text-color), and [font-weight](/docs/font-weight) utilities (`text-xl`, `text-black`, `font-medium`, etc.) to style the card text

Styling things this way contradicts a lot of traditional best practices, but once you try it you'll quickly notice some really important benefits:

- **You get things done faster** — you don't spend any time coming up with class names, making decisions about selectors, or switching between HTML and CSS files, so your designs come together very fast.
- **Making changes feels safer** — adding or removing a utility class to an element only ever affects that element, so you never have to worry about accidentally breaking something another page that's using the same CSS.
- **Maintaining old projects is easier** — changing something just means finding that element in your project and changing the classes, not trying to remember how all of that custom CSS works that you haven't touched in six months.
- **Your code is more portable** — since both the structure and styling live in the same place, you can easily copy and paste entire chunks of UI around, even between different projects.
- **Your CSS stops growing** — since utility classes are so reusable, your CSS doesn't continue to grow linearly with every new feature you add to a project.

These benefits make a big difference on small projects, but they are even more valuable for teams working on long-running projects at scale.

### Why not just use inline styles?

A common reaction to this approach is wondering, “isn’t this just inline styles?” and in some ways it is — you’re applying styles directly to elements instead of assigning them a class name and then styling that class.

But using utility classes has many important advantages over inline styles, for example:

- **Designing with constraints** — using inline styles, every value is a magic number. With utilities, you’re choosing styles from a [predefined design system](/docs/theme), which makes it much easier to build visually consistent UIs.
- **Hover, focus, and other states** — inline styles can’t target states like hover or focus, but Tailwind’s [state variants](/docs/hover-focus-and-other-states) make it easy to style those states with utility classes.
- **Media queries** — you can’t use media queries in inline styles, but you can use Tailwind’s [responsive variants](/docs/responsive-design) to build fully responsive interfaces easily.
