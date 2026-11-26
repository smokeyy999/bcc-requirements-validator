# Evening radio schedule

This synthetic specification concerns one studio display. It uses local studio time on a single day. Recording, audio playback and transmission are outside its scope.

## Display rules

- S-1. The display reads the schedule below from top to bottom. Each start is inclusive and each end is exclusive.
- S-2. When the clock lies outside all listed intervals, the current programme field displays the exact text "Off air".
- S-3. If two intervals contain the current time, the display uses the earlier row in the schedule.

| Programme | Start | End |
|---|---|---|
| The Reading Room | 18:00 | 18:30 |
| Sound Archive | 18:30 | 19:00 |
| Studio Notes | 18:45 | 19:15 |

## Acceptance

At 18:29 the field reads "The Reading Room". At 18:30 it reads "Sound Archive". At 18:50 it reads "Studio Notes". At 19:15 it reads "Off air".
