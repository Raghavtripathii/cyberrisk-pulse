# Design Decisions

Short answers to the "why did you do it this way" questions an interviewer will ask.

**Why a star schema instead of one flat table?**
A flat table repeats asset name, severity, and category on every single
row, which bloats the model and makes DAX filtering slower and messier.
Splitting into dimension tables means each fact only stores IDs, filters
propagate cleanly in one direction, and it's the pattern every real BI
tool (and the PL-300 exam) expects.

**Why do the joins/cleaning in Python instead of Power Query?**
Power Query can do this, but once you're joining three different CSVs
with different keys and adding derived columns, it gets hard to read
and hard to version-control. Doing it in Python means the transformation
logic lives in a script I can test, re-run, and put in git history --
and it's a stronger interview story ("I pushed the heavy lifting
upstream") than a wall of Power Query steps nobody can review.

**Why the 10/5/2/1 weighting on the Risk Score?**
It's a judgment call, not a standard formula -- and that's the point.
A weighted score needs weights, and Critical vulnerabilities being 10x
more dangerous than Low ones (rather than, say, 2x) reflects how
exploitable and how business-impacting a Critical finding usually is.
I'd defend this as a starting point that a real security team would
tune based on their own incident history.

**Why synthetic remediation data instead of only real data?**
The vulnerability findings and CVE enrichment are real. Remediation
tracking (who fixed what, by when) lives in ticketing systems like Jira
or ServiceNow that I don't have access to -- so I generated a
realistic version of that layer myself, with a documented SLA policy,
rather than leaving the project without any remediation story at all.
This is clearly labeled as synthetic in the README.

**Why SQLite instead of a full SQL Server / Postgres setup?**
The goal was a portable, zero-setup project anyone can clone and run.
SQLite needs no server, no credentials, no install -- and the schema
and queries would work identically against Postgres or SQL Server if
this became a real production project later.