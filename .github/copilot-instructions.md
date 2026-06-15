# Copilot Instructions — Blue Claws Lacrosse · Goalie Season System

## Design Context

### Users
Single user: the head coach. Pulled up on a phone (max-width 560px) at practice, between drill reps, often outdoors in bright sunlight. Needs to scan fast — no time to hunt for information. Zero parent-facing use; this is a coaching tool with authority and directness.

### Brand Personality
**Team**: Blue Claws Lacrosse · Ages 7–9 · goalie program  
**Three words**: Energetic, scrappy, loud  
**Logo signals**: Classic sports crest (blue lobster claw + red lacrosse stick head, bold black outlines) and a hype mascot (cartoonish lacrosse ball character, backwards cap, dripping blue/red paint). Both are bold, graphic, American youth sports.  
**Emotional goal**: The coach should feel equipped and confident. The app should feel like a pro coaching resource.

### Aesthetic Direction
**Theme**: Dark. Coaches use this outdoors in sun — dark reduces glare. Dark is the natural register for sports apps (ESPN, NFL).

**Color palette** (OKLCH — from team identity):
- Primary: Royal blue — `oklch(50% 0.22 262)` — the claw, the team name
- Accent: Red — `oklch(48% 0.20 25)` — lacrosse stick, urgency
- Light text: `oklch(93% 0.015 262)` — blue-tinted near-white
- Background: `oklch(16% 0.025 262)` — deep navy
- Surface (cards): `oklch(21% 0.03 262)` — slightly lifted navy
- Border: `oklch(28% 0.04 262)`

Pod category colors:
- Tracking: Royal blue
- Footwork: Amber/gold — `oklch(72% 0.16 75)`
- Clearing: Red-orange — `oklch(58% 0.22 38)`
- Communication: Teal — `oklch(58% 0.14 185)`

**Typography**:
- Display/headings: **Saira Condensed ExtraBold** — jersey nameplate authority
- Body: **Readex Pro** — readable at 12–14px on dark mobile screens
- Drill code identifiers (A1, B3): **Azeret Mono**

**Anti-patterns to avoid**:
- Do NOT use the old green (#0f1c14) as dominant surface — it's not the team color
- Do NOT use cyan/purple/neon gradients, glassmorphism, or border-left accent stripes
- Do NOT use Inter, DM Sans, or other default AI fonts
- Do NOT use gradient text (background-clip: text)

### Design Principles
1. **Scan speed above all.** Hierarchy must be brutal — one dominant thing per visual zone.
2. **Team colors are load-bearing.** Royal blue and red define sections, states, and identity.
3. **Dense but not cluttered.** Embrace density in drill content; use breathing room in navigation.
4. **Athletic authority, not playful.** Bold, confident, structured — for the coach, not the player.
5. **Every detail earns its place.** No decoration for decoration's sake.
