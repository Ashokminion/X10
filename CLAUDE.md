<!-- intraview-workspace-start[v0.9.21] -->
## Intraview Tour Builder

The Intraview extension enables interactive code tours and contextual feedback collection.

### CLI Commands

VS Code (or Cursor/Windsurf) must be open with this workspace loaded. Verify the connection before creating tours with `~/.intraview/bin/intraview status`.

```bash
~/.intraview/bin/intraview tour create --question "How does auth work?"
~/.intraview/bin/intraview tour list
~/.intraview/bin/intraview tour validate <workflow_id>
~/.intraview/bin/intraview nav next
~/.intraview/bin/intraview feedback add --file src/auth.js --line 42 --text "Fix this"
~/.intraview/bin/intraview --help
```

### Use Cases

- **Code Tours**: Create guided walkthroughs of codebases for onboarding, code review, or learning
- **Alignment & Feedback**: Capture structured feedback on code or architectural plans
- **Batched Audits**: Collect and export user feedback across multiple files for review sessions

### Feedback Collection

Users can provide feedback in two ways:

1. **Tour Feedback**: Inline feedback during code tours (automatically captured)
2. **Standalone Feedback**: Select code and use "Intraview: Add Feedback" context menu
   - **Keyboard**: CMD+H (Mac) or CTRL+H (Windows/Linux)
   - **Context Menu**: Right-click selected code → "Intraview: Add Feedback"

Feedback includes file context (path, line, snippet) and can be exported.
<!-- intraview-workspace-end -->
