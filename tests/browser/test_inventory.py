"""Browser tests for the Inventory view."""
import pytest
from playwright.sync_api import Page, expect


BASE_URL = "http://localhost:3000"


class TestInventory:

    def test_inventory_page_loads(self, page: Page):
        """Inventory page loads and shows data."""
        page.goto(f"{BASE_URL}/inventory")
        page.wait_for_load_state("networkidle")
        expect(page.locator(".loading")).not_to_be_visible(timeout=5000)

    def test_inventory_shows_table(self, page: Page):
        """Inventory page shows a table with rows."""
        page.goto(f"{BASE_URL}/inventory")
        page.wait_for_load_state("networkidle")
        rows = page.locator("tbody tr")
        expect(rows.first).to_be_visible()

    def test_inventory_no_errors(self, page: Page):
        """No unhandled JS errors on inventory page."""
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.goto(f"{BASE_URL}/inventory")
        page.wait_for_load_state("networkidle")
        assert len(errors) == 0, f"JS errors: {errors}"
