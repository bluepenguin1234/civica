# Civica Scoring Roadmap

## Suggested Weight Changes (v2 — not yet implemented)

| Pillar            | Current | Suggested | Change | Reason |
|-------------------|---------|-----------|--------|--------|
| Fiscal Health     | 30%     | 28%       | -2%    | Still the anchor — small trim to fund Safety increase |
| Schools           | 15%     | 20%       | +5%    | Research puts schools at 15–25% of price variation between towns |
| Safety            | 5%      | 12%       | +7%    | Top-2 buyer priority — 5% is indefensibly low |
| Tax Efficiency    | 15%     | 15%       | —      | Keep — core differentiator |
| Economic Momentum | 10%     | 8%        | -2%    | Buyers feel this indirectly through prices already |
| Operational Quality| 10%    | 8%        | -2%    | Solid signal but hard to explain to buyers |
| Infrastructure    | 10%     | 6%        | -4%    | Over-weighted relative to actual buyer priorities |
| Climate Resilience| 5%      | 3%        | -2%    | Forward-thinking but not yet priced by most buyers |

## To implement
- Build dynamic score computation from data fields (scores are currently hardcoded manually)
- Once dynamic: weight changes above will automatically recalculate all town scores
- Re-audit scores after dynamic computation — expect some towns to shift 3–8 points
