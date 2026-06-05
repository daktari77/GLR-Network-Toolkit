# Product

## Register

product

## Users

Solo engineer / home-lab owner who built this tool for personal use. Technically fluent: comfortable with terminals, IP addressing, and low-level networking. Opens the app alongside other work to keep an eye on network health. Not reading docs before using it; expects the interface to be self-evident.

## Product Purpose

GLR NetScope is a personal parallel network monitor for Windows. It probes multiple hosts simultaneously via ICMP, TCP, and HTTP, surfaces per-host latency stats and status history, and fires alerts on state changes. The primary surface is the PyQt6 desktop app (Monitor, Network Scanner, Port Scanner, Troubleshoot tabs). Success looks like: open the app, see at a glance which hosts are UP or DOWN, drill into one host when something looks off, and trust the numbers.

## Brand Personality

Bold, technical, reliable. The tool carries operator confidence, not enterprise polish. It is precise and dense — every control and column earns its place. It does not apologize for being a power-user tool.

## Anti-references

- **Overcrowded NOC dashboards**: no blinking-light overload, no red-everywhere severity theater, no badge-on-badge chrome. One authoritative status per host, clear at 10 feet.
- Avoid the generic 2024–2025 SaaS aesthetic: warm cream backgrounds, oversized rounded cards, gradient badges. This is a desktop tool, not a landing page.

## Design Principles

1. **Status is king.** UP/DOWN/UNKNOWN is the loudest visual signal on screen. Everything else — latency numbers, column headers, toolbar buttons — supports it without competing.
2. **Density without noise.** Pack the information in; do not inflate rows or chrome to fill space. But separate clearly: groups, sections, and hierarchy through contrast and spacing, not decorative lines.
3. **Expert trust.** No confirmation dialogs for obvious actions, no tooltips restating what labels already say, no wizard flows for things the user can type. Trust the person running the tool.
4. **Operator-grade stability.** The UI should feel calm under load: no jitter during live updates, no visual jump when a host changes state, no flickering. Motion serves function (a subtle status transition) — not decoration.
5. **One tool, four panels.** The tab structure is the navigation; it should be immediate, not buried. Active panel is always obvious. Cross-panel wiring (send to Port Scanner, send to Traceroute) is a first-class citizen.

## Accessibility & Inclusion

No formal WCAG target. Maintain readable contrast for the operator's own comfort. Keep all controls keyboard-accessible as Qt defaults provide. No motion-sensitivity requirements.
