# Usability and audit test (guide Step 39; proposal Table 9 "Usability/audit")

Give these tasks to 3–5 people. Start with someone who did not build the dashboard. Do not help them during a task. Write the results in `reports/usability.md` with the table below.

Before the test: the system runs in the lab, and at least one attack scenario has made alerts and one block.
Each person logs in at `http://192.168.50.5:5000` with an account made for them (`tools/create_admin.py`), so the audit log shows who did what.

## Tasks

| # | Task (read it to the person) | Done when |
| --- | --- | --- |
| 1 | "Find the newest alert. Tell me its class, its confidence, its source and destination, and the evidence note." | All five said correctly |
| 2 | "Is this alert only a model prediction, or a confirmed incident? Mark it as a confirmed incident." | Status changed to confirmed |
| 3 | "Which address is blocked now, and why? Unblock it." | The address was removed from the Blocklist page |
| 4 | "Export yesterday's attack events as CSV, only the PortScan class." | A CSV file with only PortScan rows was saved |
| 5 | "Start a device scan of the lab network and tell me which device may be a camera." | The scan finished; the camera was named |
| 6 | "Change the number of repeats needed before a block from 3 to 4." | The Settings page shows 4; the change history shows it |

## Results table (copy to reports/usability.md)

| Person (code, not the name) | Task | Done? (yes/no/with help) | Time (s) | Comments |
| --- | --- | --- | --- | --- |
| P1 | 1 | | | |

## Audit check (every action must be traceable: who, what, when, why)

After the tasks, open the audit log (`GET /api/logs`, or export `type=system_logs`). Check that every action from tasks 2, 3, 4, 5 and 6 is there, with the user name, the time and the reason.

| Task | Audit record found? | Event name in the log |
| --- | --- | --- |
| 2 confirm incident | | INCIDENT_STATUS_CHANGED |
| 3 unblock | | MANUAL_UNBLOCK |
| 4 export | | LOGS_EXPORTED |
| 5 scan | | SCAN_STARTED, SCAN_COMPLETED |
| 6 settings change | | SETTING_CHANGED (and the settings change history) |
