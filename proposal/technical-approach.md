# Technical Approach

**RFP Reference:** MC-2026-0417

---

## Our approach to scoping

Before writing this section, we reviewed the source code and the previous vendor's handoff notes included in the RFP package. The handoff is thin — stack details and a file map, but no explanation of the known defects or the design decisions behind them. We treat that as a finding in itself: the previous vendor did not leave Meridian in a position to maintain or extend this system independently.

Our technical approach is organized around the four required items in §3.1, followed by our position on the desired items in §3.2.

---

## R1 — Reports Module Remediation

The handoff notes acknowledge that "Reports module was in progress; not all filters wired up." The RFP references at least eight logged issues spanning filter behavior, internationalization gaps, and inconsistent data patterns.

Our approach:
- Perform a full audit of `client/src/views/Reports.vue` and the backend endpoints it consumes, mapping every defect against the filter system architecture (`useFilters.js`, `api.js`, `main.py`)
- Fix filter wiring so that all four filter dimensions (Time Period, Warehouse, Category, Order Status) behave consistently and propagate correctly to the API
- Resolve i18n gaps so that all user-visible strings in the Reports view are covered by the locale system already in place
- Normalize any API response inconsistencies so the frontend receives predictable data shapes
- Validate each fix against the browser test suite we deliver under R3

**Assumption:** We will treat the RFP's "at least eight issues" as a floor, not a ceiling. Any additional defects discovered during the audit are in scope.

---

## R2 — Restocking Recommendations

This is the primary new capability. The Restocking view will:

- Present a list of SKUs that are below their reorder threshold, ranked by urgency (days of stock remaining based on current demand forecast)
- Allow the operator to enter a budget ceiling; the system will generate a recommended purchase order list that maximizes coverage within that budget
- Show per-SKU detail: current stock, demand forecast, suggested order quantity, unit cost, and total cost
- Follow the existing Vue 3 Composition API patterns used in the rest of the application, using the same filter bar and warehouse selector already in use on other views

**Assumption:** We will derive reorder thresholds from the existing inventory and demand forecast data already present in `server/data/`. No new data sources are required. If Meridian has supplier lead time data they want incorporated, that would be a scope addition.

**Assumption:** "Budget ceiling" is an operator-entered value per session, not a persisted system setting.

---

## R3 — Automated Browser Testing

The absence of test coverage is the primary reason Meridian IT has blocked changes. We will establish end-to-end test coverage using the Playwright testing framework, covering:

- Dashboard load and key metric display
- Inventory view filtering (by warehouse, category)
- Orders view filtering (by status, time period)
- Reports view — all filter combinations that were defective prior to R1 remediation
- Restocking view — budget input and recommendation generation (delivered with R2)

Tests will run against the local development server and be committed to the repository so Meridian IT can run them independently. We will provide a brief README explaining how to run them.

**Assumption:** Coverage of "critical flows" means the primary read paths for each view, plus the filter interactions that were previously broken. We are not including authentication flows in the initial test suite as the current system has no authentication layer.

---

## R4 — Architecture Documentation

We will produce a current-state architecture overview as an HTML document suitable for handoff to Meridian IT. It will cover:

- System components and their relationships (frontend, backend, data layer)
- Data flow through the filter system
- API surface and endpoint reference
- Known limitations of the current architecture (no database, no auth) with notes on what a future vendor would need to address to productionize

This document will be generated after we have completed R1 and R2, so it reflects the final delivered state.

---

## D1–D3 — Desired Items

**D1 (UI modernization):** We can refresh the visual design within the existing component structure. We would want to align on a specific direction with Tanaka's team before starting — "current standards" is undefined in the RFP. We propose a brief design review session at the start of the engagement.

**D2 (Internationalization):** The i18n infrastructure (`useI18n.js`, `locales/en.js`, `locales/ja.js`) already exists. Extending it to remaining views is straightforward once R1 is complete, as we will have already audited string coverage across the application.

**D3 (Dark mode):** Achievable by adding a theme toggle to the existing CSS variable system. Low implementation risk; we'd recommend prototyping on a separate branch before merging.

---

## Open questions / assumptions logged

| # | Question | Assumption used in this proposal |
|---|---|---|
| 1 | What does "current standards" mean for D1 (UI modernization)? | We will align with Meridian on a design direction before starting D1 |
| 2 | Which flows are "critical" for R3 test coverage? | Primary read paths for each view + all previously broken filter interactions |
| 3 | Is there a budget ceiling? | None stated; we have structured pricing to be transparent (see Pricing section) |
| 4 | Are there exactly eight Reports defects, or more? | We treat the number as a floor; full audit is in scope |
| 5 | Should Restocking incorporate supplier lead times? | Not in scope unless Meridian provides data |
