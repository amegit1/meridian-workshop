# Timeline

**RFP Reference:** MC-2026-0417
**Proposed start:** Week of May 18, 2026 (assuming award by May 12)

---

## Phased delivery plan

| Phase | Weeks | Deliverables |
|---|---|---|
| Phase 1 — Foundation | Weeks 1–2 | Architecture review (R4 draft), Reports audit, automated test scaffold (R3) |
| Phase 2 — Remediation | Weeks 3–4 | Reports module fully fixed (R1), test suite covering all repaired flows (R3) |
| Phase 3 — Restocking | Weeks 5–6 | Restocking view live (R2), test coverage extended to new feature |
| Phase 4 — Closeout | Week 7 | Architecture documentation final (R4), desired items if in scope, PR review and handoff |

**Total engagement: 7 weeks.** All required items (R1–R4) delivered by end of Week 7.

---

## Phase detail

### Phase 1 — Foundation (Weeks 1–2)

The first two weeks are about getting oriented and establishing the safety net before touching anything.

- Review codebase, validate handoff notes against actual code
- Produce architecture diagram (R4 first draft — useful for internal alignment)
- Audit all defects in Reports module, document findings
- Stand up Playwright test infrastructure, write first tests against stable views (Dashboard, Inventory, Orders)
- Kickoff call with Tanaka's team to confirm Restocking requirements

**Milestone:** Reports defect list signed off by Meridian. Test suite running in CI.

### Phase 2 — Remediation (Weeks 3–4)

With the defect list confirmed and tests in place, we fix.

- Resolve all Reports defects (R1): filter wiring, i18n gaps, API inconsistencies
- Extend test coverage to Reports view (R3)
- Begin Restocking backend work (data model, API endpoint)

**Milestone:** Reports module passes all tests. Meridian IT approves deployment of R1 fixes.

### Phase 3 — Restocking (Weeks 5–6)

- Build Restocking frontend view (R2): budget input, recommendations table, per-SKU detail
- Wire to backend endpoint
- Extend test coverage to Restocking view (R3)
- User acceptance testing with Tanaka's team

**Milestone:** Restocking view accepted by R. Tanaka.

### Phase 4 — Closeout (Week 7)

- Finalize architecture documentation (R4) to reflect delivered state
- Deliver any desired items (D1–D3) if contracted
- Final PR, code review, handoff to Meridian IT
- Knowledge transfer session

**Milestone:** All deliverables accepted. Repository handed over.

---

## Notes on timeline risk

- **IT approval** is the most likely source of delay. We have structured Phase 1 to produce the test scaffold early, so IT can validate our approach before we are deep into remediation.
- **Restocking requirements** may shift after the kickoff call with Tanaka's team. We have buffered Phase 3 with one week of flex.
- **Desired items (D1–D3)** are not included in this timeline. If contracted, we would extend by 1–2 weeks depending on scope.
