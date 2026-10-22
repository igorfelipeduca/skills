# skills

Agent skills I use across projects. They work with Claude Code, Codex, Cursor and the other agents supported by [`skills`](https://github.com/vercel-labs/skills).

## Install

Requires Node.js 22.20 or later.

Install for your user, so the skill is available in every project:

```bash
npx skills add igorfelipeduca/skills -g
```

Install a single skill for Claude Code only:

```bash
npx skills add igorfelipeduca/skills --skill before-after-evidence -a claude-code -g
```

Leave out `-g` to install into the current project instead.

Keep it up to date:

```bash
npx skills update
```

## Skills

### `before-after-evidence`

Proves a bug fix with before/after evidence:

1. Reverts the fix in the working tree and reproduces the bug while recording the screen and taking a screenshot at each step.
2. Restores the fix and runs the same flow again.
3. Composes a "Before" / "After" comparison image.
4. Posts the image and both recordings to the issue tracker (Linear, GitHub…) with a short write-up in English.

| Project type | Driver |
| --- | --- |
| Mobile (React Native, Expo, native iOS/Android) | [Maestro](https://maestro.dev) CLI, plus `xcrun simctl` / `adb` for the recording |
| Web | [agent-browser](https://github.com/vercel-labs/agent-browser) for screenshots and video |

Requirements: the driver for your platform, Python 3 with Pillow (for the comparison image), and the CLI for your tracker (for example [`linear`](https://github.com/schpet/linear-cli) or `gh`).

To use it, ask your agent something like "test this fix and post before/after evidence to the ticket".

## License

MIT
