---
name: before-after-evidence
description: Prove a bug fix with before/after evidence. Reproduce the bug with the fix temporarily reverted, capture step-by-step screenshots and a screen recording, restore the fix, capture the same flow again, compose a side-by-side comparison image, and post everything to the issue tracker in English. Use Maestro for mobile apps (React Native, Expo, native iOS/Android) and agent-browser for web apps. Use when the user asks to test a fix, show before/after, record evidence, or attach proof to a ticket.
---

# Before/After Evidence

Show that a fix works by running the same scripted flow twice, once without the fix and once with it, and putting the evidence next to each other.

The output is:

- one screenshot per meaningful step, for both runs
- a screen recording of both runs
- one comparison image: a "Before" row above an "After" row, using the same steps
- a comment on the issue tracker with the images, the videos and a short write-up in English

## 1. Pick the driver

| Project type | Signals | Driver |
| --- | --- | --- |
| Mobile | `app.json` / `app.config.*` with Expo, `ios/`, `android/`, React Native deps | Maestro CLI + `xcrun simctl io` (iOS) or `adb screenrecord` (Android) |
| Web | Next.js, Vite, Remix, or any app served on `localhost` | `agent-browser` (screenshots + `record start/stop`) |

If a project has both, use the platform where the bug was reported.

## 2. Prepare

1. Confirm the fix is committed, or at least saved, so you can restore it exactly. Note the commit hash.
2. Make a working folder in the scratchpad, e.g. `$S/evidence/`. Never write evidence into the repo.
3. Make sure the app is already running:
   - **Mobile:** a booted simulator or emulator (`xcrun simctl list devices booted`, `adb devices`) and the dev server (Metro) serving this checkout. Check with `lsof -iTCP:8081 -sTCP:LISTEN` and confirm the process cwd is this repo.
   - **Web:** the dev server is up. Find the URL in the project's scripts or terminal output.
4. Pick the smallest flow that shows the bug, and write down the steps where it becomes visible. Prefer a deterministic flow. For example, type a query one character at a time instead of pasting it.

## 3. Write the flow once, run it twice

Write the flow as a script so both runs do exactly the same thing.

### Mobile (Maestro)

```yaml
# typing.yaml
appId: com.example.app
---
- openLink: myapp://some-screen
- waitForAnimationToEnd
- inputText: "a"
- waitForAnimationToEnd
- takeScreenshot: step01
- inputText: "b"
- waitForAnimationToEnd
- takeScreenshot: step02
```

- Generate long flows with a short script, e.g. one `inputText` + `takeScreenshot` pair per character.
- `takeScreenshot` takes a **bare name**. Pass `--test-output-dir=<dir>` to the run so screenshots go to `<dir>/<timestamp>/<flow>/takeScreenshot/`. Absolute paths and `${VAR}` paths are rejected as "outside this run's output folder".
- Find the `appId` (bundle id / package name) and the deep link scheme in the app config.
- Navigate with deep links (`openLink`) rather than taps where you can. They are faster and more stable.

Relaunch the app before every run (the Maestro equivalent of a hard reload):

```yaml
# relaunch.yaml
appId: com.example.app
---
- launchApp:
    stopApp: true
- extendedWaitUntil:
    visible: "Some text on the first screen"
    timeout: 60000
```

### Web (agent-browser)

```bash
agent-browser open "$URL"
agent-browser record start "$OUT/before.webm" "$URL"
agent-browser snapshot -i              # get @refs, never guess selectors
agent-browser type @e3 "a" && agent-browser screenshot "$OUT/step01.png"
agent-browser type @e3 "b" && agent-browser screenshot "$OUT/step02.png"
agent-browser record stop
```

- Put the steps in a small shell script so the "after" run is identical.
- Take a fresh `snapshot -i` after navigation, because refs change.
- Pass `--headed` if the user wants to watch.
- For logged-in pages, use the project's saved auth state or login skill instead of typing credentials into the flow.
- Do a hard reload, or `open` again, before each run so no stale bundle or state carries over.

## 4. Run "before" (fix reverted)

Revert only the fix in the **working tree**, never in git history:

```bash
git diff <base>..HEAD -- <files> | git apply -R    # or remove the changed lines by hand
```

Then:

1. **Reload everything.** Hot reload / fast refresh is not enough. Components that read a prop only on mount, such as list virtualization settings, keep the old behavior until they remount. On mobile, run `relaunch.yaml`. On web, hard-reload or reopen the page.
2. Start the recording:
   - iOS: `xcrun simctl io booted recordVideo --codec=h264 -f "$OUT/before/before.mp4" & REC=$!`
   - Android: `adb shell screenrecord /sdcard/before.mp4 & REC=$!`, then `adb pull` the file afterwards
   - Web: `agent-browser record start ...`
3. Run the flow and save the screenshots to `$OUT/before`.
4. Stop the recording: `kill -INT $REC; wait $REC` (simctl/adb) or `agent-browser record stop`.

Look at the screenshots. **If the bug does not reproduce, stop and tell the user.** The flow, the data or the reload is wrong, and an "after" run would prove nothing.

## 5. Run "after" (fix restored)

```bash
git checkout -- <files>      # back to the committed fix
git status --short <files>   # must be clean
```

Reload everything again and repeat step 4 into `$OUT/after`.

Look at the screenshots. If "after" still shows the bug, first rule out a missed reload, which is the usual cause. If it still fails after a real relaunch, the fix is wrong: say so plainly and investigate. Never post evidence that doesn't support the claim.

## 6. Compose the comparison

Pick the 2–4 steps where the difference is clearest and use the same steps for both rows:

```bash
python3 -I scripts/compose.py \
  --before "$OUT/before/<run>/<flow>/takeScreenshot" \
  --after  "$OUT/after/<run>/<flow>/takeScreenshot" \
  --steps step06 step07 step08 \
  --out "$OUT/before_after.png"
```

`scripts/compose.py` sits next to this file and needs only Pillow. Open the result and check that the bug and the fix are visible at a glance.

## 7. Post to the tracker

Write the comment in **English**, whatever language the conversation is in. Keep it short:

- **Setup:** device or browser, OS, the flow, and that the app was relaunched before each run
- **Before:** what goes wrong and at which step
- **After:** what happens now at the same steps
- **Cause:** one or two sentences, and which file changed
- **Branch or PR** link

Attach the comparison image and both recordings.

**Linear** (`linear` CLI):

```bash
linear auth list    # check which workspace owns the issue
linear issue comment add ISSUE-123 -w <workspace> \
  --body-file "$OUT/comment.md" \
  --attach "$OUT/before_after.png" \
  --attach "$OUT/before/before.mp4" \
  --attach "$OUT/after/after.mp4"
```

- Pass `-w <workspace>` when the CLI default is a different workspace. Otherwise you get "issue not found", and the files may already be uploaded to the wrong workspace by then.
- Use `comment add --attach` and not `issue attach`, so images render inline.

**GitHub** (issue or PR): the CLI can't upload images. Post the write-up with `gh issue comment` / `gh pr comment` and give the user the file paths to drag in, or attach them through the tracker that is linked to the PR.

For any other tracker, use its CLI or MCP. If there is none, hand the files to the user.

## 8. Report back

In the user's language, report:

- whether the bug reproduced before and is gone after
- the link to the posted comment
- anything that went wrong along the way (fallbacks used, uploads to the wrong place)
- confirmation that the working tree is back to the committed fix

Also send the comparison image and recordings to the user directly if the harness supports it.

## Troubleshooting

- **Maestro MCP says "Device became unreachable":** use the `maestro` CLI directly (`maestro --device <udid> test flow.yaml`). It talks to the same simulator.
- **`takeScreenshot` path rejected:** use a bare name plus `--test-output-dir`.
- **"After" looks identical to "before":** the app was not relaunched, or the dev server is serving a different checkout or worktree.
- **The bug only appears with certain data:** note that data in the write-up (account, saved searches, cart contents), so someone else can reproduce it.
- **Recording file is empty:** stop it with SIGINT (`kill -INT`), not SIGKILL, and wait for the process to exit.
