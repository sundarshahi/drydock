# Phase 5: Design & Polish

## Style Selection — Engagement Mode Aware

Read engagement mode from `Shipyard/.orchestrator/settings.md`.

### Express Mode
Auto-select the most domain-appropriate style based on the BRD:
- Developer tools, data platforms, APIs → **High Tech**
- Consumer apps, creative products, marketplaces → **Creative**
- Finance, healthcare, legal, enterprise → **Corporate**
- Premium SaaS, lifestyle, design-focused products → **Elegance**

Report the selection: `Style: {selected} (auto-selected for {domain} — Express mode)`
Proceed immediately to 5.1 Domain Research.

### Standard / Thorough / Meticulous Mode
**Do NOT start implementing. Do NOT start researching. Do NOT touch any files.**

The FIRST action in this phase is to ask the user which visual style they want. Use AskUserQuestion IMMEDIATELY:

```
Which visual style do you want for the frontend?

> Creative — Colorful, captivating visuals, bold gradients, expressive typography,
             rich imagery, delightful micro-animations. Makes your heart melt.
  Elegance — Minimalist, sleek, Apple-inspired. Generous whitespace, restrained palette,
             premium feel, typography-driven, every pixel intentional.
  High Tech — For geeks. Neat boxed layouts, monospace accents, terminal aesthetics,
              dark-mode-first, data-dense, IT/dev theme, subtle grid lines.
  Corporate — Formal, professional, trustworthy. Conservative palette, clear hierarchy,
              structured layouts, no surprises. Enterprise-ready.
  Custom — I'll describe what I want
  Chat about this
```

**Wait for the user's response. Do NOT proceed until they answer.**

The selected style becomes the **design directive** that drives ALL subsequent decisions in this phase.

---

## Objective

The frontend is functional — every button works, every link resolves, every form submits, navigation is complete. NOW make it beautiful. This phase transforms a working but generic frontend into a visually polished, domain-appropriate, professionally designed application.

**This phase uses WebSearch (freshness protocol) to research current design trends, competitive visual benchmarks, and domain-appropriate aesthetics BEFORE making design decisions.**

## Prerequisites

Phase 4b (Functional Verification) MUST be complete. Every interactive element works. Do NOT polish a broken frontend.

The style selected above (via the engagement-mode-aware process) becomes the **design directive** that drives ALL subsequent decisions in this phase. Every choice below (colors, typography, spacing, interactions) must align with the selected style.

### Style Reference Guide

| Style | Colors | Typography | Spacing | Interactions | Dark Mode |
|-------|--------|-----------|---------|-------------|-----------|
| **Creative** | Vibrant primaries, bold gradients, accent pops, complementary combos | Expressive — mix display + body fonts, varied weights, large headings | Generous but dynamic — asymmetric layouts, overlapping elements OK | Rich — animated transitions, hover transformations, parallax, delightful loading states | Vivid — saturated colors on dark backgrounds, glow effects |
| **Elegance** | Restrained — 1-2 neutral tones + one subtle accent, monochromatic scales | Premium sans-serif (SF Pro, Inter, Helvetica Neue), thin/light weights, precise sizing | Very generous — whitespace IS the design, breathing room everywhere | Subtle — smooth fades, gentle scaling, understated hover states, nothing flashy | Refined — deep charcoal backgrounds, muted text, thin borders |
| **High Tech** | Cool tones — slate/zinc/cyan, neon accents optional, matrix-green or electric-blue | Monospace for data/labels (JetBrains Mono, Fira Code), clean sans for body | Tight and structured — grid-aligned, uniform gutters, dense information | Precise — snappy transitions, no bounce, terminal-style cursor blinks, status indicators | Default — dark IS the primary mode, light mode is secondary |
| **Corporate** | Conservative — navy, slate, white. One brand color. Muted success/warning/error | System or professional sans (Inter, Roboto, Segoe UI), regular weights, standard sizes | Structured — consistent 8px grid, clear section breaks, standard card padding | Minimal — basic hover highlights, standard focus rings, no animations beyond necessary | Optional — light mode primary, dark mode if requested |

## 5.1 Domain Research (WebSearch Required)

Combine the user's **selected style** with domain-specific research:

1. **Style + domain intersection** — WebSearch for "{selected style} {domain} web design" (e.g., "elegant fintech dashboard design", "high-tech developer tool UI"). Find examples that match BOTH the style directive and the product domain.

2. **Visual benchmarks** — WebSearch for the top 3-5 products in the same domain. Filter through the lens of the selected style — which competitors match the desired aesthetic? Which elements can we adopt?

3. **Current trends** — WebSearch for "web design trends {current year}" filtered to the selected style category. What's current? What's dated?

4. **Style-specific inspiration** — Search for design references matching the style:
   - **Creative** → Dribbble, Awwwards, trending colorful SaaS designs
   - **Elegance** → Apple.com, Linear, Stripe, minimalist design showcases
   - **High Tech** → Vercel, GitHub, terminal-inspired UIs, developer tool dashboards
   - **Corporate** → Salesforce, HubSpot, enterprise dashboard patterns

Document findings in `Shipyard/frontend-engineer/docs/design-research.md` including the selected style and how it maps to the domain.

## 5.2 Color Theory

Upgrade the default blue palette to a color system that matches the **selected style** and domain:

### Primary Color Selection

Choose based on (in priority order):
1. **Selected style directive** — Creative demands vibrancy, Elegance demands restraint, High Tech demands cool precision, Corporate demands conservative authority
2. **Product personality** from BRD (trustworthy? innovative? playful? professional?)
3. **Domain conventions** (fintech → blue/green, health → blue/teal, creative → purple/orange)
4. **Color psychology:**
  - Blue → trust, stability, professionalism
  - Green → growth, health, money, nature
  - Purple → creativity, luxury, innovation
  - Orange → energy, warmth, friendliness
  - Red → urgency, passion, action (use sparingly)
  - Teal → modern, fresh, tech-forward
  - Indigo → depth, wisdom, premium feel

### Color System

Generate a complete color system:

```
Primary    → 50-950 scale (main brand color)
Secondary  → 50-950 scale (complementary or analogous)
Accent     → single vivid shade (for CTAs, highlights, attention)
Neutral    → 50-950 scale (grays — warm or cool depending on primary)
Semantic   → success (green), warning (amber), danger (red), info (blue)
```

Style-specific color rules:
- **Creative** — Use gradients freely. 2-3 vibrant primaries. Bold complementary or triadic combos. Accent should be eye-catching.
- **Elegance** — Maximum 2 colors + neutrals. One subtle accent. Monochromatic scales. Restraint is the point.
- **High Tech** — Cool neutrals (slate/zinc). One electric accent (cyan, green, blue). Dark surfaces. Minimal color variation.
- **Corporate** — One brand primary (navy, blue). Neutral supporting. Muted semantics. No gradients. No surprises.

Universal rules:
- Primary and secondary must have sufficient contrast when used together
- Accent color must pop against both light and dark backgrounds
- Neutral grays should have a slight warm or cool tint matching the primary (pure gray looks dead)
- Every text/background combination meets WCAG 2.1 AA (4.5:1 normal, 3:1 large)
- Dark mode is NOT just inverted — it needs its own considered palette where primary colors shift lighter

### Application

- **Primary** → main actions, active states, key UI elements, brand presence
- **Secondary** → supporting elements, secondary actions, tags, categories
- **Accent** → CTAs that need to pop, new feature badges, important notifications
- **Neutral** → text, backgrounds, borders, dividers, subtle UI

## 5.3 Typography

Upgrade from system fonts to a considered type system:

1. **WebSearch** for current popular font pairings for the domain
2. Choose fonts guided by the **selected style**:
   - **Creative** → Expressive fonts. Mix display + body. Consider: Clash Display, Cabinet Grotesk, Satoshi, Plus Jakarta Sans. Bold heading weights.
   - **Elegance** → Premium sans-serif. Consider: SF Pro, Inter (light/regular weights), Helvetica Neue, Manrope. Thin weights for large text.
   - **High Tech** → Monospace for labels/data (JetBrains Mono, Fira Code, Berkeley Mono). Clean sans for body (Geist, Inter). Terminal vibes.
   - **Corporate** → Conservative and readable. Inter, Roboto, Segoe UI, or system fonts. Regular weights. Nothing fancy.

3. **Type hierarchy:**
   - Clear visual distinction between h1-h6 (not just size — weight and spacing matter)
   - Body text optimized for readability (16px minimum, 1.5 line height, 60-75 char line length)
   - Consistent use of font weight to create hierarchy (not just size)
   - Tabular numbers for data-heavy UIs (tables, dashboards, metrics)

## 5.4 Visual Hierarchy & Layout Polish

Apply design principles to make information scannable and actions obvious:

1. **Whitespace** — Increase spacing between sections. Group related items tighter. Use generous padding in cards and containers. Whitespace is not wasted space — it guides the eye.

2. **Visual weight** — Primary CTAs should be the heaviest element on screen (filled, bold color). Secondary actions lighter (outlined or ghost). Destructive actions in red but not visually dominant unless intentional.

3. **Information density** — Match the domain:
   - Dashboard → higher density, compact tables, small type for data
   - Marketing → lower density, generous whitespace, large type
   - Settings → medium density, clear sections, adequate spacing

4. **Card and container styling** — Consistent border radius, subtle shadows for elevation, clear visual grouping. Cards should look like cards (distinct from background), not just boxes.

5. **Icon consistency** — Use a single icon library throughout (Lucide, Heroicons, or Phosphor). Consistent size and stroke width. Icons should enhance, not replace text for important actions.

## 5.5 Micro-Interactions & Feedback

Interaction richness scales with the selected style:

**All styles (mandatory):**
1. **Hover states** — Every clickable element has a visible hover state. Not just cursor:pointer.
2. **Active/pressed states** — Buttons feel pressed (scale down slightly, darken).
3. **Focus states** — Visible focus ring styled to match design. Critical for accessibility.
4. **Loading feedback** — Buttons show spinner during API calls. Forms disable during submission. Skeletons match layout.
5. **Success/error feedback** — Toasts for async results. Inline form validation. Optimistic updates.

**Style-scaled interactions:**

| Interaction | Creative | Elegance | High Tech | Corporate |
|-------------|----------|----------|-----------|-----------|
| Transitions | Bold — scale, rotate, gradient shifts, 300-500ms | Subtle — gentle fades, 200-300ms, ease-in-out | Snappy — instant or 100-150ms, linear, no bounce | Basic — 150ms color change, nothing more |
| Page transitions | Animated — slide, fade, shared element transitions | Refined — smooth crossfade, content stagger | None or instant — no wasted motion | None — instant route changes |
| Hover effects | Transformative — elevation, color shift, glow, scale | Minimal — subtle background tint, thin underline | Precise — border highlight, background darken | Standard — background highlight only |
| Loading states | Playful — branded animations, skeleton with shimmer | Clean — minimal skeleton, thin progress line | Technical — progress percentage, status text, dots | Standard — spinner, skeleton |
| Empty states | Illustrated — custom illustrations, inviting copy | Typographic — elegant text, single subtle icon | Data-styled — formatted "no results" with filters | Functional — clear message, primary CTA |
| Notifications | Animated toasts with icons and color | Understated inline messages | Console-style status updates | Standard alert banners |

## 5.6 Dark Mode Polish

Dark mode is NOT light mode with colors inverted. It needs specific attention:

- Background layers: use 2-3 shades of dark (pure black is harsh — use dark gray like #0a0a0a or #111)
- Reduce white text brightness (use #e5e5e5 not #ffffff for body text)
- Primary colors shift lighter/more saturated in dark mode for same visual impact
- Shadows don't work in dark mode — use subtle border or lighter background instead
- Test all states in both modes — hover, active, focus, disabled, error

## 5.7 Responsive Polish

Verify the design works beautifully at all breakpoints:

- Mobile (320px-640px): touch-friendly, stacked layout, hamburger nav, full-width cards
- Tablet (768px): 2-column where appropriate, sidebar as overlay
- Desktop (1024px+): full layout, sidebar visible, multi-column grids
- Wide (1536px+): max-width container, content doesn't stretch infinitely

## Implementation

Update these files with researched design decisions:

1. `frontend/app/styles/tokens/colors.ts` — Replace defaults with researched palette
2. `frontend/app/styles/tokens/typography.ts` — Replace system fonts with chosen typeface
3. `frontend/app/styles/theme/light-theme.ts` — Polished light theme
4. `frontend/app/styles/theme/dark-theme.ts` — Polished dark theme (not just inverted)
5. `frontend/tailwind.config.ts` — Updated with final design tokens
6. All components — Update to use refined tokens (hover states, transitions, focus styles)
7. All pages — Apply spacing, visual hierarchy, and layout polish

## Output

- `Shipyard/frontend-engineer/docs/design-research.md` — Domain research, competitive analysis, trend findings
- `Shipyard/frontend-engineer/docs/design-decisions.md` — Color choices with rationale, typography selection, visual hierarchy rules
- Updated token files, theme files, and component styles

## Validation Loop

Before moving to Phase 6 (Testing):
- [ ] Design research documented with WebSearch findings
- [ ] Color palette is domain-appropriate with documented rationale
- [ ] Typography is intentional (not default system fonts unless that's the right choice)
- [ ] Every hover, active, focus, and disabled state is styled
- [ ] Dark mode is polished (not just inverted)
- [ ] Visual hierarchy is clear — primary CTA is the most prominent element on every page
- [ ] Spacing and whitespace are generous and consistent
- [ ] Responsive design looks good (not just functional) at all breakpoints
- [ ] Micro-interactions provide feedback for every user action

**Design review (mode-aware):** Express — proceed to Phase 6, report design summary. Standard — show brief before/after. Thorough/Meticulous — present full design system comparison via AskUserQuestion.

## Quality Bar

"Default blue with system fonts" is NOT production-ready.

- **Creative**: "Vibrant purple-to-pink gradient primary, Cabinet Grotesk headings, animated page transitions, illustrated empty states, glow-on-hover cards, dark mode with saturated accents"
- **Elegance**: "Monochromatic slate palette with one rose accent, SF Pro at light/regular weights, 32px section spacing, fade-only transitions, deep charcoal dark mode with muted text"
- **High Tech**: "Zinc surfaces, cyan-500 accent, JetBrains Mono for all data labels, 4px grid-aligned layouts, instant transitions, dark-mode-first with subtle grid lines"
- **Corporate**: "Navy-700 primary, Inter at regular weight, 8px consistent grid, no animations, standard card elevation, optional light-only theme"

THAT is production-ready — intentional design that matches the user's chosen style.
