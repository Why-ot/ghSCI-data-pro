# extras

Material that is derived from, or documents, the raw captures in `../../parts/`.

| folder | what it holds |
|---|---|
| `previews/` | one depth and one colour snapshot per unit (`preview_depth.png`, `preview_color.png`), for quick visual triage of a capture without unpacking the archive |
| `pose_logs/` | the arm pose recorded at each capture session (`pose_2026110*.json`) — the re-teach between sessions that Section 6.6 refers to |
| `ghsci_data_provenance/` | the README and SHA-256 of the earlier 2026-11-05 packaging of the same capture, kept so the two deposits can be cross-checked |
| `sci_camera_audit/` | the camera-selection and pre-flight audit of Section 4.1, including the D435 smoke captures |

The previews are regenerated from the frames in `parts/`, so they carry no
information that is not already there; they exist so a reader can see what a unit
looks like without unpacking 1.25 GB.