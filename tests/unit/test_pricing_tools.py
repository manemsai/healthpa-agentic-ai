from decimal import Decimal

from elevance_ai.domain.pricing import PricingQuery
from elevance_ai.tools.pricing_tools import read_pricing_csv


def test_read_pricing_csv_filters_by_billing_code(tmp_path) -> None:
    csv_path = tmp_path / "rates.csv"
    csv_content = """billing_code,billing_code_type,provider_name,provider_npi,negotiated_rate,negotiated_type,service_description,file_last_updated
99213,CPT,Example Clinic,1234567890,125.50,negotiated,Office visit,2026-01-01
99214,CPT,Other Clinic,9876543210,150.00,negotiated,Office visit,2026-01-01
"""
    csv_path.write_text(
        csv_content,
        encoding="utf-8",
    )

    rows = read_pricing_csv(csv_path, PricingQuery(billing_code="99213"))

    assert len(rows) == 1
    assert rows[0].provider_name == "Example Clinic"
    assert rows[0].negotiated_rate == Decimal("125.50")
