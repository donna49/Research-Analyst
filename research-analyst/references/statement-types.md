# Statement types

Every prior statement in the ledger gets one type. The type decides what evidence matters when it is
compared with later facts. Classification is descriptive; whether a statement is actionable is the
lawyer's call.

| Type | Looks like | What to collect |
|---|---|---|
| **Historical or present fact** | "Revenue grew 12%", "the facility is operating normally", "we have no knowledge of any investigation" | Facts that existed on the statement date contradicting it |
| **Forward-looking** | Guidance, targets, "we expect", "we anticipate", timelines | The exact cautionary language attached, whether it was specific to the risk that occurred or generic; facts known at the time that undercut the projection |
| **Opinion or belief** | "We believe the claims are without merit", "we do not expect a material adverse effect" | Whether the speaker actually held the view; facts in their possession that conflict with it; what the opinion implied about how it was formed |
| **Risk factor written as hypothetical** | "If X occurs, our results could be harmed" | Whether X had already occurred, or was under way, when the risk factor was filed |
| **Reassurance about a known issue** | "The disruption is temporary and immaterial", "we have resolved the issue" | What happened next; internal or external evidence available at the time |
| **Omission** | Silence on a fact a reasonable investor would want, especially after speaking on the topic | Evidence the fact existed and was known; whether the company spoke on the same topic, making the silence relevant |
| **Puffery / generic optimism** | "Industry-leading", "well positioned", "strong momentum" | Record, but weight low unless tied to a specific verifiable claim |

Ledger codes (`statement_type`): `fact`, `forward-looking`, `opinion`, `risk-hypothetical`,
`reassurance`, `omission`, `puffery` (same order as the table).

## Wording-change tracking (from InvestSkill 10k-digest "promise tracker" and financial-report-analyst risk-factor diff)

For the issue under study, line up every version of the relevant passage across consecutive filings
and calls. For each change record: date, what was added, removed or softened, and any event between
the two versions. Track hedging escalation:
standard (`we believe`, `we expect`) → heightened (`we cannot assure`, `there can be no assurance`) →
near-crisis (`substantial doubt`, `material uncertainty`).

A reassurance that disappears without explanation is itself a data point.
