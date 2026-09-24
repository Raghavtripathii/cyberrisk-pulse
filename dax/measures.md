# DAX Measures for CyberRisk Pulse

How to use this: in Power BI Desktop, right-click `fact_vulnerabilities`
in the Fields pane -> **New Measure**, then paste one of these in. Do
this once per measure below. Explanation in plain English sits above
each one so you can actually defend it in an interview, not just copy it.

---

### 1. Open Findings
In plain English: how many vulnerabilities are still unfixed right now.
```
Open Findings =
CALCULATE(
    COUNTROWS(fact_vulnerabilities),
    fact_vulnerabilities[status] = "Open"
)
```

### 2. Closed Findings
```
Closed Findings =
CALCULATE(
    COUNTROWS(fact_vulnerabilities),
    fact_vulnerabilities[status] = "Remediated"
)
```

### 3. Mean Time to Remediate (days)
In plain English: on average, how many days does it take the team to
fix something once it's found. Only counts findings that are actually
closed -- an open finding hasn't been "remediated" yet, so it shouldn't
drag the average down or up.
```
Mean Time to Remediate (days) =
AVERAGEX(
    FILTER(fact_vulnerabilities, fact_vulnerabilities[status] = "Remediated"),
    DATEDIFF(fact_vulnerabilities[date_found], fact_vulnerabilities[date_closed], DAY)
)
```

### 4. SLA Compliance %
In plain English: of everything we've closed, what percentage did we
close before the deadline we promised. This is the number a CISO reports
upward -- it says whether the team is actually keeping its promises.
```
SLA Compliance % =
VAR ClosedOnTime =
    CALCULATE(
        COUNTROWS(fact_vulnerabilities),
        fact_vulnerabilities[status] = "Remediated",
        fact_vulnerabilities[date_closed] <= fact_vulnerabilities[sla_due_date]
    )
VAR TotalClosed = [Closed Findings]
RETURN
    DIVIDE(ClosedOnTime, TotalClosed)
```

### 5. Overdue Critical Count
In plain English: right now, today, how many Critical findings have
blown past their deadline and are still open. This is the number that
should worry a security manager the most.
```
Overdue Critical Count =
CALCULATE(
    COUNTROWS(fact_vulnerabilities),
    fact_vulnerabilities[status] = "Open",
    RELATED(dim_severity[severity]) = "Critical",
    fact_vulnerabilities[sla_due_date] < TODAY()
)
```

### 6. Risk Score (weighted)
In plain English: a single number that represents total risk exposure
right now, weighting Critical findings much higher than Low ones. This
is a metric I designed myself, not a built-in Power BI thing -- the
weights (10/5/2/1) are a documented assumption, adjust them if you want
to argue for a different weighting scheme.
```
Risk Score (weighted) =
VAR CriticalOpen = CALCULATE([Open Findings], dim_severity[severity] = "Critical")
VAR HighOpen     = CALCULATE([Open Findings], dim_severity[severity] = "High")
VAR MediumOpen   = CALCULATE([Open Findings], dim_severity[severity] = "Medium")
VAR LowOpen      = CALCULATE([Open Findings], dim_severity[severity] = "Low")
RETURN
    (CriticalOpen * 10) + (HighOpen * 5) + (MediumOpen * 2) + (LowOpen * 1)
```

### 7. Risk Score MoM % Change
In plain English: is our risk score going up or down compared to last
month. This is the "time intelligence" DAX that shows up in every
Power BI job description.
```
Risk Score MoM % Change =
VAR CurrentMonth = [Risk Score (weighted)]
VAR PreviousMonth =
    CALCULATE(
        [Risk Score (weighted)],
        DATEADD(dim_date[date], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth)
```

### 8. Aging Bucket (calculated column, not a measure)
In plain English: groups every open finding into a bucket based on how
long it's been sitting unfixed, so you can build a backlog-aging chart.
Add this as a **New Column** on `fact_vulnerabilities`, not a measure.
```
Aging Bucket =
VAR DaysOpen = DATEDIFF(fact_vulnerabilities[date_found], TODAY(), DAY)
RETURN
    SWITCH(
        TRUE(),
        fact_vulnerabilities[status] = "Remediated", "Closed",
        DaysOpen <= 7, "0-7 days",
        DaysOpen <= 30, "8-30 days",
        DaysOpen <= 90, "31-90 days",
        "90+ days"
    )
```