# Brand Studio design bundle

This directory contains the approved Odysseus **Brand Studio / Full White-Label** design specification and its three TDD implementation plans.

Status: **approved design and implementation plans, not implemented code**.

Contained documents after extraction:

- `docs/superpowers/specs/2026-08-17-brand-studio-white-label-design.md`
- `docs/superpowers/plans/2026-08-17-brand-studio-core-runtime.md`
- `docs/superpowers/plans/2026-08-17-brand-studio-assets-admin.md`
- `docs/superpowers/plans/2026-08-17-brand-studio-system-integration.md`

## Verify bundle chunks

```bash
cd design/brand-studio
sha256sum -c SHA256SUMS
```

## Reconstruct and extract the Markdown bundle

```bash
cat BRAND-STUDIO-DESIGN-AND-PLANS.part-* \
  | base64 -d \
  | gzip -dc \
  > BRAND-STUDIO-DESIGN-AND-PLANS.md
```

The decoded Markdown bundle SHA-256 is:

```text
bada64a80372d4b288315fb7dc16f31ac88a6ed6ffdbb7a8b2186be65228b4bd
```

The combined encoded bundle SHA-256 is:

```text
da5797a2abc60cc8b6f3a59bbab8a6654fdeba9e634c20a9359c354d100ed818
```

Brand Studio is planned as a standalone admin program with versioned publishing, secure asset processing, structured design tokens, local fonts, authenticated draft preview sessions, granular branding permissions, global-now/multi-brand-ready resolution, and system-wide white-label application.
