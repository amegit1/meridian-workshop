"""Browser tests for the Restocking view (R2 new feature coverage)."""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:3000"


class TestRestocking:

    def test_restocking_page_loads(self, page: Page):
        """Restocking page loads without errors."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/restocking")
        page.wait_for_load_state("networkidle")
        expect(page.locator(".loading")).not_to_be_visible(timeout=8000)
        assert len(errors) == 0, f"JS errors on Restocking: {errors}"

    def test_restocking_shows_budget_input(self, page: Page):
        """Restocking page shows the budget input field."""
        page.goto(f"{BASE_URL}/restocking")
        page.wait_for_load_state("networkidle")
        budget_input = page.locator(".budget-input")
        expect(budget_input).to_be_visible()

    def test_restocking_shows_items_table(self, page: Page):
        """Restocking page shows a table of items below reorder point."""
        page.goto(f"{BASE_URL}/restocking")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("tbody tr", timeout=8000)
        rows = page.locator("tbody tr")
        expect(rows.first).to_be_visible()

    def test_restocking_budget_filters_recommendations(self, page: Page):
        """Entering a budget shows recommended items with checkmarks."""
        page.goto(f"{BASE_URL}/restocking")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("tbody tr", timeout=8000)

        budget_input = page.locator(".budget-input")
        budget_input.fill("50000")
        page.wait_for_timeout(500)

        # With a budget set, recommended column with checkmarks should appear
        checks = page.locator(".check")
        expect(checks.first).to_be_visible()

    def test_restocking_shows_urgency_badges(self, page: Page):
        """Restocking table shows urgency badges (critical/warning/low)."""
        page.goto(f"{BASE_URL}/restocking")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector(".badge", timeout=8000)
        badges = page.locator(".badge")
        expect(badges.first).to_be_visible()

    def test_restocking_shows_summary_stats(self, page: Page):
        """Restocking page shows summary stat cards."""
        page.goto(f"{BASE_URL}/restocking")
        page.wait_for_load_state("networkidle")
        stat_cards = page.locator(".stat-card")
        expect(stat_cards.first).to_be_visible()

    def test_restocking_accessible_from_nav(self, page: Page):
        """Restocking view is accessible via the navigation bar."""
        page.goto(BASE_URL)
        restocking_link = page.locator('.nav-tabs a[href="/restocking"]')
        expect(restocking_link).to_be_visible()
        restocking_link.click()
        page.wait_for_load_state("networkidle")
        expect(page).to_have_url(f"{BASE_URL}/restocking")
