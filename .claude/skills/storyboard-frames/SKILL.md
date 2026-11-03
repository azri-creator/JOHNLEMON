---
name: storyboard-frames
description: >-
  "Storyboard Frames": the review gate every style in this repo goes through before an MP4 is rendered. Once the
  plan is approved and the HyperFrames composition is built, snapshot one still per beat (hook, each headline or
  title, each transition, the signature moment, the CTA or end) and lay the stills out on numbered storyboard
  sheets with the time, the VO line and a note on the visual. The student refines frame by frame ("frame 3 tukar
  warna", "frame 5 tulisan besar sikit"), only the changed frames are re-snapshotted, and the full video is rendered
  only after the student approves the storyboard. Use it for every style job, and whenever someone says
  storyboard, "frame dulu", "nak tengok dulu", "preview dulu" or "jangan render lagi", even if they don't name it.
---

# Storyboard Frames

Rendering a full video takes minutes, and every revision costs another render. A storyboard costs seconds: the stills come from the real composition, so what the student approves is exactly what will render. Fix the look here, and render once at the end.

## Where it sits in every job

1. **Plan:** a beat table and an asset list. Wait for "ok".
2. **Build:** the composition in `work/<project>/` from the style's template.
3. **Storyboard:** follow this skill. Loop until the student approves.
4. **Render:** the MP4, using the style's own render step.

Never render the full MP4 (draft or delivery) before the storyboard is approved. The one exception is a student who explicitly says to skip it ("skip storyboard", "terus render"). Short snapshots for your own checks are fine at any time.

## Steps

1. **Build first.** The composition must pass `npx hyperframes check` with 0 errors. Heavy steps may still be drafts:
   - If the cut-out matte or the final mix is not ready, use the raw footage.
   - Say in the `visual` note that it is a draft ("cut-out belum dibuat").
   - Do the heavy step before the storyboard when the look depends on it. Hero words behind the head are an example.
2. **Choose the frames.** Pick 8–16 frames, one per beat. Use more only for videos longer than 60 s.
   - Always include the hook, every headline or place title, the style's signature moment (map, orbit, machine, chapter card), one frame per transition style, and the CTA or end card.
   - Choose the readable instant: after the entrance has settled, usually the beat start + 0.5–0.8 s. Never mid-blur or mid-wipe.
3. **Write `storyboard/storyboard.json`** in the folder that holds `index.html`:
   ```json
   {"title": "Nama projek", "version": 1,
    "frames": [{"n": 1, "t": 0.8, "line": "Ramai ingat edit video susah", "visual": "Hook: kicker + headline besar, presenter tengah", "changed": false}]}
   ```
   Write `line` and `visual` in Bahasa Melayu, short.
4. **Run the script:**
   ```bash
   python3 .claude/skills/storyboard-frames/scripts/storyboard.py work/<project>
   ```
   (Use `work/<project>/hf` when the style builds in `hf/`.) It writes:
   - `storyboard/frames/NN.png`, one still per frame;
   - `storyboard_v<version>_p<page>.jpg`, the sheets, 12 frames per page;
   - `STORYBOARD.md`, a table of every frame.
5. **Look at every sheet yourself before sending it.** Check for:
   - text overflowing the frame;
   - text hidden by the head;
   - typos in Malay;
   - a logo or name that isn't the student's;
   - captions clashing with titles;
   - empty or black frames.
   Fix what you find, then re-run.
6. **Send the sheets to the student.** On the desktop app or claude.ai/code, show the JPG itself. Then send, in BM:
   > Ni storyboard v1 (N frame). Semak setiap frame. Nak ubah apa, sebut nombor frame, contoh "frame 3 tukar warna kuning" atau "frame 7 tulisan besar sikit". Kalau semua okay, balas **ok storyboard** dan aku terus render video.
7. **Revise in a loop.** For each change:
   1. Edit the composition. Change only what was asked, and keep the rest identical.
   2. Set `"changed": true` on the edited frames and `false` on the others, and add 1 to `version`.
   3. Run `--only 3,7` with the changed frame numbers, so only those frames are re-snapshotted.
   4. Send the new sheet. Changed frames have a yellow border and a "DIUBAH" tag. List the changes in one line per frame.
   5. If a change moves timing, re-snapshot the frames after it as well, and say so.
8. **Approval.** Render the MP4 with the style's render step only after the student says "ok storyboard", "proceed", "render" or similar. Keep the approved sheet next to the video in `output/` (`<project>_storyboard.jpg`) so the final can be compared with it.

## Notes
- The stills come from the same timeline that renders, so there is no separate mock-up to keep in sync.
- One composition rendering several sizes (9:16, 16:9, 1:1): storyboard the first size, and get it approved. Storyboard each later size only when its layout is rebuilt rather than reflowed.
- A student working from a phone sees the sheet JPG in chat. Keep each sheet at 12 frames or fewer so it stays readable on a small screen.
- If `npx hyperframes@0.8.212` fails with ETARGET or differs from the version the style pins, set `HF="npx --yes hyperframes@<version>"`.
