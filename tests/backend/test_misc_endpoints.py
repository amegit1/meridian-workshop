"""
Tests for miscellaneous API endpoints (demand, backlog, spending).
"""
import pytest


class TestDemandEndpoints:
    """Test suite for demand forecast endpoints."""

    def test_get_demand_forecasts(self, client):
        """Test getting demand forecasts."""
        response = client.get("/api/demand")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            forecast = data[0]
            assert "id" in forecast
            assert "item_sku" in forecast
            assert "item_name" in forecast
            assert "current_demand" in forecast
            assert "forecasted_demand" in forecast
            assert "trend" in forecast
            assert "period" in forecast

    def test_demand_forecast_trends(self, client):
        """Test that demand forecasts have valid trend values."""
        response = client.get("/api/demand")
        data = response.json()

        valid_trends = ["increasing", "stable", "decreasing"]

        for forecast in data:
            assert forecast["trend"].lower() in valid_trends

    def test_demand_forecast_values(self, client):
        """Test that demand forecast values are non-negative."""
        response = client.get("/api/demand")
        data = response.json()

        for forecast in data:
            assert forecast["current_demand"] >= 0
            assert forecast["forecasted_demand"] >= 0

    def test_stable_demand_items_exist(self, client):
        """Test that there are stable demand items."""
        response = client.get("/api/demand")
        data = response.json()
        stable_items = [item for item in data if item["trend"].lower() == "stable"]
        assert len(stable_items) >= 1, "Expected at least one stable item"

    def test_demand_forecast_has_expected_skus(self, client):
        """Test that expected SKUs are present in demand forecasts."""
        response = client.get("/api/demand")
        data = response.json()
        skus = [item["item_sku"] for item in data]
        assert "PCB-001" in skus, "Missing PCB-001 in demand forecasts"
        assert "TMP-201" in skus, "Missing TMP-201 in demand forecasts"


class TestBacklogEndpoints:
    """Test suite for backlog endpoints."""

    def test_get_backlog(self, client):
        """Test getting backlog items."""
        response = client.get("/api/backlog")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            backlog_item = data[0]
            assert "id" in backlog_item
            assert "order_id" in backlog_item
            assert "item_sku" in backlog_item
            assert "item_name" in backlog_item
            assert "quantity_needed" in backlog_item
            assert "quantity_available" in backlog_item
            assert "days_delayed" in backlog_item
            assert "priority" in backlog_item

    def test_backlog_priority_values(self, client):
        """Test that backlog items have valid priority values."""
        response = client.get("/api/backlog")
        data = response.json()

        valid_priorities = ["high", "medium", "low"]

        for item in data:
            assert item["priority"].lower() in valid_priorities

    def test_backlog_quantity_logic(self, client):
        """Test that backlog quantities are non-negative."""
        response = client.get("/api/backlog")
        data = response.json()

        for item in data:
            # Quantities should be non-negative
            assert item["quantity_needed"] >= 0
            assert item["quantity_available"] >= 0

    def test_backlog_days_delayed(self, client):
        """Test that days delayed is non-negative."""
        response = client.get("/api/backlog")
        data = response.json()

        for item in data:
            assert item["days_delayed"] >= 0


class TestSpendingEndpoints:
    """Test suite for spending-related endpoints."""

    def test_get_spending_summary(self, client):
        """Test getting spending summary."""
        response = client.get("/api/spending/summary")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)

    def test_get_monthly_spending(self, client):
        """Test getting monthly spending data."""
        response = client.get("/api/spending/monthly")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            month_data = data[0]
            assert "month" in month_data or "period" in month_data

    def test_monthly_spending_has_all_cost_categories(self, client):
        """Test that monthly spending includes all cost categories."""
        response = client.get("/api/spending/monthly")
        data = response.json()

        required_fields = ["procurement", "operational", "labor", "overhead"]

        for month_data in data:
            for field in required_fields:
                assert field in month_data, f"Missing {field} in monthly spending"
                assert isinstance(month_data[field], (int, float))
                assert month_data[field] >= 0

    def test_monthly_spending_has_variety(self, client):
        """Test that monthly spending data has variety (not all the same)."""
        response = client.get("/api/spending/monthly")
        data = response.json()

        # Collect all procurement values
        procurement_values = [month["procurement"] for month in data]

        # Should have at least 3 different values (variety)
        unique_values = set(procurement_values)
        assert len(unique_values) >= 3, \
            "Monthly spending should have variety, not all the same values"

        # Same for other categories
        operational_values = set(month["operational"] for month in data)
        assert len(operational_values) >= 3, \
            "Operational costs should have variety across months"

    def test_get_category_spending(self, client):
        """Test getting spending by category."""
        response = client.get("/api/spending/categories")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            category_data = data[0]
            assert "category" in category_data or "name" in category_data

    def test_get_recent_transactions(self, client):
        """Test getting recent transactions."""
        response = client.get("/api/spending/transactions")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

        # Check structure if data exists
        if len(data) > 0:
            transaction = data[0]
            # Transactions should have some identifying fields
            assert isinstance(transaction, dict)


class TestRestockingEndpoint:
    """Test suite for the restocking recommendations endpoint."""

    def test_get_restocking_recommendations(self, client):
        """Test getting restocking recommendations returns a list."""
        response = client.get("/api/restocking")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_restocking_item_structure(self, client):
        """Test that restocking items have required fields."""
        response = client.get("/api/restocking")
        data = response.json()
        if len(data) > 0:
            item = data[0]
            for field in ["sku", "name", "warehouse", "quantity_on_hand",
                          "reorder_point", "unit_cost", "suggested_qty", "total_cost", "urgency"]:
                assert field in item, f"Missing field: {field}"

    def test_restocking_only_below_reorder_point(self, client):
        """Test that all recommendations are for items below reorder point."""
        response = client.get("/api/restocking")
        data = response.json()
        for item in data:
            assert item["quantity_on_hand"] < item["reorder_point"], (
                f"{item['sku']}: quantity_on_hand {item['quantity_on_hand']} "
                f">= reorder_point {item['reorder_point']}"
            )

    def test_restocking_valid_urgency_values(self, client):
        """Test that urgency values are one of the expected values."""
        response = client.get("/api/restocking")
        data = response.json()
        valid_urgencies = {"critical", "warning", "low"}
        for item in data:
            assert item["urgency"] in valid_urgencies

    def test_restocking_total_cost_is_correct(self, client):
        """Test that total_cost equals suggested_qty * unit_cost."""
        response = client.get("/api/restocking")
        data = response.json()
        for item in data:
            expected = round(item["suggested_qty"] * item["unit_cost"], 2)
            assert abs(item["total_cost"] - expected) < 0.01

    def test_restocking_filter_by_warehouse(self, client):
        """Test filtering restocking recommendations by warehouse."""
        response = client.get("/api/restocking?warehouse=San Francisco")
        assert response.status_code == 200
        data = response.json()
        for item in data:
            assert item["warehouse"] == "San Francisco"

    def test_restocking_sorted_by_urgency(self, client):
        """Test that results are sorted with critical items first."""
        response = client.get("/api/restocking")
        data = response.json()
        if len(data) < 2:
            return
        urgency_order = {"critical": 0, "warning": 1, "low": 2}
        for i in range(len(data) - 1):
            assert urgency_order[data[i]["urgency"]] <= urgency_order[data[i + 1]["urgency"]]


class TestReportsEndpoints:
    """Test suite for reports endpoints."""

    def test_get_quarterly_reports(self, client):
        """Test getting quarterly reports."""
        response = client.get("/api/reports/quarterly")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_quarterly_report_structure(self, client):
        """Test quarterly report item structure."""
        response = client.get("/api/reports/quarterly")
        data = response.json()
        if len(data) > 0:
            q = data[0]
            for field in ["quarter", "total_orders", "total_revenue", "avg_order_value", "fulfillment_rate"]:
                assert field in q

    def test_quarterly_reports_filter_by_warehouse(self, client):
        """Test quarterly reports accept warehouse filter."""
        response = client.get("/api/reports/quarterly?warehouse=London")
        assert response.status_code == 200

    def test_get_monthly_trends(self, client):
        """Test getting monthly trends."""
        response = client.get("/api/reports/monthly-trends")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_monthly_trends_structure(self, client):
        """Test monthly trends item structure."""
        response = client.get("/api/reports/monthly-trends")
        data = response.json()
        if len(data) > 0:
            m = data[0]
            for field in ["month", "order_count", "revenue"]:
                assert field in m

    def test_monthly_trends_sorted_by_month(self, client):
        """Test that monthly trends are sorted chronologically."""
        response = client.get("/api/reports/monthly-trends")
        data = response.json()
        months = [item["month"] for item in data]
        assert months == sorted(months)


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_endpoint(self, client):
        """Test the root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data or "version" in data

    def test_root_endpoint_structure(self, client):
        """Test root endpoint has expected structure."""
        response = client.get("/")
        data = response.json()

        # Should have message and version
        assert "message" in data
        assert "version" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)
