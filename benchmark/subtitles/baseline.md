# Subtitle track export

A desktop subtitle editor exports one open track to a local file. This specification covers export only.

## Format
T-1. Write the exported track in UTF-8 without a byte-order mark.
T-2. The acceptance test reads the first three bytes; a UTF-8 byte-order mark fails the test.
T-3. Each timestamp field declares milliseconds; the numeric value 1000 represents one second.
T-4. For a track with 100 cues on workstation ST-1, show the completion dialog no later than 2 seconds after the export command.
T-5. For an empty track, display the exact message listed in T-6 and leave the destination unchanged.
T-6. The message for an empty track is “Add at least one cue”.

## Export limits
T-7. Reject a cue when its text exceeds 80 Unicode code points.
T-8. In the acceptance sample, a cue of 81 Unicode code points is rejected.
