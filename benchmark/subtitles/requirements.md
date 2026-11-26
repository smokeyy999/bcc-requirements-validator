# Subtitle track export

A desktop subtitle editor exports one open track to a local file. This specification covers export only.

## Format
T-1. Write the exported track in UTF-8 without a byte-order mark.
T-2. The acceptance test requires the first three bytes to be a UTF-8 byte-order mark.
T-3. Each timestamp field declares milliseconds; the numeric value 1000 represents one minute.
T-4. The export experience must feel effortless to every user.
T-5. For an empty track, display the exact message listed in T-40 and leave the destination unchanged.
T-6. The message for an empty track is “Add at least one cue”.

## Export limits
T-7. Reject a cue when its text exceeds 80 Unicode code points.
T-8. In the acceptance sample, a cue of 81 Unicode code points is accepted.
