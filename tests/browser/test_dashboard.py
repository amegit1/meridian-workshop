"""Browser tests for the Dashboard view."""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:3000"


class TestDashboard:

    def test_dashboard_loads(self, page: Page):
        """Dashboard page loads without errors."""
        page.goto(BASE_URL)
        expect(page).not_to_have_title("")
        page.wait_for_load_state("networkidle")

    def test_dashboard_has_stat_cards(self, page: Page):
        """Dashboard displays at least one stat card."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        stat_cards = page.locator(".stat-card")
        expect(stat_cards.first).to_be_visible()

    def test_dashboard_nav_links_present(self, page: Page):
        """All main navigation links are present."""
        page.goto(BASE_URL)
        nav = page.locator(".nav-tabs")
        expect(nav).to_be_visible()
        for path in ["/inventory", "/orders", "/reports", "/restocking"]:
            link = page.locator(f'.nav-tabs a[href="{path}"]')
            expect(link).to_be_visible()

    def test_filter_bar_present(self, page: Page):
        """Global filter bar is visible on the dashboard."""
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        filter_bar = page.locator(".filter-bar, [class*='filter']").first
        expect(filter_bar).to_be_visible()

    def test_no_console_errors_on_load(self, page: Page):
        """No unhandled JS errors on dashboard load."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        assert len(errors) == 0, f"Console errors on load: {errors}"
