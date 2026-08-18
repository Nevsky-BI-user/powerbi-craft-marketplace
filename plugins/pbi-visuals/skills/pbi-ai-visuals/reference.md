# pbi-ai-visuals — Theme Property Reference

> Every card/property below was extracted programmatically from
> `docs/research/reportThemeSchema-2.155.json` (`definitions/visual-*`) — titles and
> descriptions are the schema's own UI strings, not invented. Verify against the actual
> `reportThemeSchema-2.1xx` shipped with the target Power BI version before writing values;
> if it differs, the schema wins. All five features also inherit the global `"*"` defaults
> (background/border/title/dropShadow/visualHeader — DESIGN-TOKENS.md §6) — do not
> re-declare those per visual (antipattern A7).
>
> Color/font properties omit `type` in the schema (they resolve to fill/font-size union
> types) — encode them per DESIGN-TOKENS §1.7 (`ThemeDataColor` preferred, plain hex only for
> colors genuinely absent from the theme).

---

## 1. `decompositionTreeVisual` — Decomposition tree

| Card | Property | Title | Notes |
|---|---|---|---|
| `analysis` | `aiEnabled` | Enable AI splits | Shows AI option when choosing a column to drill into |
| `analysis` | `aiMode` | Analysis type | AI splits find absolute high/low values or the most-standout ones |
| `categoryLabels` | `categoryLabelBold/Italic/Underline`, `categoryLabelFontColor/FontFamily/FontSize` | — | Row category text |
| `dataBars` | `axisStart`, `axisEnd` | Start / End | Optional manual scale bounds |
| `dataBars` | `dataBarColor`, `positiveBarColor`, `negativeBarColor`, `dataBarBackgroundColor` | — | Bar fill by sign; background = unoccupied bar area |
| `dataBars` | `dataBarScalingType` | Scale to | How the bar's fill % is computed |
| `dataBars` | `dataBarWidthPercent` | Size | Bar thickness |
| `dataLabels` | `dataLabelDisplayUnits`, `dataLabelPrecision` | Display units / decimal places | K/M/B formatting |
| `dataLabels` | `dataLabelBold/Italic/Underline`, `dataLabelFontColor/FontFamily/FontSize` | — | Value text |
| `general` | `formatString` | — | Number format applied to the analyzed measure |
| `insights` | `isAINode` | — | Marks a node as an AI-suggested split (not the retired "Quick insights" feature — different thing entirely) |
| `levelHeader` | `levelTitleFontColor/FontFamily/FontSize/Bold/Italic/Underline` | Title font | Column/level header |
| `levelHeader` | `levelSubtitleFontColor/FontFamily/FontSize/Bold/Italic/Underline`, `showSubtitles` | Subtitle font | e.g. field name under the level title |
| `levelHeader` | `levelHeaderBackgroundColor` | Color | Header background per level |
| `tree` | `accentColor` | Selected line | Primary accent — the *selected* drill path |
| `tree` | `connectorDefaultColor` | Unselected line | Deselected connector color |
| `tree` | `connectorType` | Style | Shape of connecting lines |
| `tree` | `barsPerLevel`, `effectiveBarsPerLevel` | Max bars shown | Scroll threshold per level |
| `tree` | `density` | Density | How tightly data bars cluster |
| `tree` | `defaultClickAction` | Default action | Clicking an intermediate node filters vs collapses the tree |
| `tree` | `responsiveLayout` | Responsive | Adapts to container resize |

## 2. `keyDriversVisual` — Key influencers

| Card | Property | Title | Notes |
|---|---|---|---|
| `keyDrivers` | `allowKeyDrivers` | Enable key influencers | Toggles the "What influences" analysis |
| `keyDrivers` | `allowKeyDriversCounting` | Enable counts | Estimated data-point counts per influencer |
| `keyDrivers` | `countType` | Count type | Counts relative to max influencer vs absolute |
| `keyDrivers` | `allowProfiles` | Enable segments | Toggles the "Find segments" analysis |
| `keyDrivers` | `selectedAnalysis`, `selectedNumericAnalysis`, `selectedSort`, `targetValue`, `numericTargetSelectedKind` | — | Analysis/target state; exact enum literals not documented in schema — capture from a real saved visual rather than inventing string values (BRIEF F2) |
| `keyDriversDrillVisual` | `defaultColor`, `referenceLineColor` | — | Drill-in detail scatter (per-influencer breakdown view) |
| `keyInfluencersVisual` | `canvasColor` | Background color | Whole-visual canvas |
| `keyInfluencersVisual` | `primaryColor`, `primaryFontColor` | Primary accent / text | The dominant influencer bar + its label |
| `keyInfluencersVisual` | `secondaryColor`, `secondaryFontColor` | Secondary accent / text | Supporting influencers |
| `keyInfluencersVisual` | `fontColor` | Font color | Base text |

**Design note:** never claim Key influencers "proves" a cause — it ranks statistical
association only. Needs enough rows (hundreds+) and at least 2 independent fields with real
variability; a target with near-zero variance yields meaningless output.

## 3. `aiNarratives` — Smart narrative (Copilot narrative)

| Card | Property | Title | Notes |
|---|---|---|---|
| `text` | `fontColor`, `fontFamily`, `fontSize`, `textAlignment` | — | Body text of the generated narrative |
| `summary` | `autoRefresh` | Auto refresh | Re-summarize automatically as filters/data change |
| `narrativeSelection` | `dismissSelectionScreen` | — | Skip the "choose a summary type" first-run screen |
| `userPrompt` | `text`, `useAllVisuals`, `useCurrentLocale`, `selectedVisualsJson` | — | Copilot-driven custom-prompt narrative — requires Copilot capacity/license, distinct from the classic non-Copilot dynamic-value narrative |

**Design note:** classic Smart narrative binds dynamic values to other visuals on the page —
those links break silently if the source visual is deleted or renamed (wiring mechanics →
`powerbi-visuals`). The rendered sentence depends on live data; it cannot be verified headless,
only that the visual object and theme keys are well-formed.

## 4. `qnaVisual` — Q&A visual

| Card | Property | Title | Notes |
|---|---|---|---|
| `inputBox` | `questionFontColor/FontFamily/FontSize/Bold/Italic/Underline` | Question font | Text the user types |
| `inputBox` | `background`, `hoverColor` | Background / Hover | Field background; dropdown hover highlight |
| `inputBox` | `acceptedColor`, `errorColor`, `warningColor` | Underline colors | Understood / not-understood / unsure word spans |
| `inputBox` | `restatementFontColor/FontFamily/FontSize` | Restatement font | Shown only when the query needed reinterpretation |
| `inputBox` | `commitButtonBackgroundColor` | Submit button background | |
| `suggestions` | `show` | Show | Suggested-question chips |
| `suggestions` | `cardBackground`, `cardFontColor/FontFamily/FontSize/Bold/Italic/Underline` | Card font/background | Each suggestion chip |
| `suggestions` | `headerFontColor/FontFamily/FontSize/Bold/Italic/Underline` | Header font | "Suggestions" label |
| `hiddenProperties` | `savedUtterance` | — | Persisted last question (state, not styling) |

**Design note:** NL match quality depends entirely on model curation — hidden technical
fields, "Teach Q&A", and field synonyms (outside this skill's scope; a modeling task). Without
that curation, ship curated suggested questions instead of a blank box, and flag recognized
phrasing as unverifiable headless.

## 5. Anomaly detection — `lineChart` → `anomalyDetection` card (NOT a standalone visual key)

| Property | Title | Notes |
|---|---|---|
| `show` | Show | Enables the analytics-pane feature on this line chart |
| `confidenceBandShow`, `confidenceBandColor`, `confidenceBandStyle` | Confidence band | Range of "normal" values; anything outside it is flagged |
| `markerShow`, `markerColor`, `markerShape`, `markerShapeSize`, `markerRotation`, `markerTransparency` | Marker | The anomaly point itself |
| `markerBorderShow`, `markerBorderColor`, `markerBorderColorMatchFill`, `markerBorderWidth`, `markerBorderTransparency` | Marker border | |
| `isAnomalyHighlighted` | — | Highlight state flag |
| `displayName` | Name | Label for this anomaly series in the legend |
| `BatchStart`, `BatchEnd`, `CategoryValue`, `Value`, `ExpectedLow`, `ExpectedHigh`, `ExpectedValue` | — | Data-bound fields of the detected anomaly, not theme styling |

**Design note:** available on `lineChart` only, not bar/column/area. Needs a reasonably long,
regular-interval series (sparse or irregular series degrade detection); sensitivity is a
detection-quality trade-off (fewer false positives ↔ more missed anomalies), tune per series,
don't leave at default without checking results. Pair `markerShape` with color — never flag
anomalies by color alone (DESIGN-TOKENS §1.3, WCAG non-text contrast).

---

## Known-wrong keys (do not emit)

| Wrong | Right | Why |
|---|---|---|
| `smartNarrative` | `aiNarratives` | Not a real schema key |
| `anomalyDetection` as a top-level `visualStyles` entry | `visualStyles.lineChart.*.anomalyDetection` | It is a card of `lineChart`, not a visual type |
| `decompositionTree` | `decompositionTreeVisual` | Missing suffix |
| `keyInfluencers` (as the visual key) | `keyDriversVisual` (the visual); `keyInfluencersVisual` is one of its *cards* | Easy to conflate visual key with card name |
| `qna` | `qnaVisual` | Missing suffix |
