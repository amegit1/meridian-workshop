"""Browser tests for the Reports view (R1 remediation coverage)."""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:3000"


class TestReports:

    def test_reports_page_loads(self, page: Page):
        """Reports page loads without errors."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        expect(page.locator(".loading")).not_to_be_visible(timeout=8000)
        assert len(errors) == 0, f"JS errors on Reports: {errors}"

    def test_reports_shows_quarterly_table(self, page: Page):
        """Reports page displays the quarterly performance table."""
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("tbody tr", timeout=8000)
        rows = page.locator("tbody tr")
        expect(rows.first).to_be_visible()

    def test_reports_shows_bar_chart(self, page: Page):
        """Reports page displays the monthly revenue bar chart."""
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        bars = page.locator(".bar")
        expect(bars.first).to_be_visible()

    def test_reports_shows_summary_stats(self, page: Page):
        """Reports page displays summary stat cards."""
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        stat_cards = page.locator(".stat-card")
        expect(stat_cards.first).to_be_visible()

    def test_reports_no_excessive_console_logs(self, page: Page):
        """Reports page does not spam the console (R1 fix verification)."""
        messages = []
        page.on("console", lambda msg: messages.append(msg.text) if msg.type == "log" else None)
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        # Before fix: formatNumber logged on every render — hundreds of messages.
        # After fix: no log messages expected.
        assert len(messages) < 5, f"Excessive console logs ({len(messages)}): {messages[:5]}"

    def test_reports_stat_cards_show_values(self, page: Page):
        """Summary stat card values are non-empty."""
        page.goto(f"{BASE_URL}/reports")
        page.wait_for_load_state("networkidle")
        stat_values = page.locator(".stat-value")
        count = stat_values.count()
        assert count >= 4
        for i in range(count):
            text = stat_values.nth(i).inner_text().strip()
            assert text != "", f"Stat card {i} has empty value"
