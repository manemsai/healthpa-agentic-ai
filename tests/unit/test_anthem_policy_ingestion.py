from elevance_ai.ingestion.anthem_policies import AnthemPolicyIngestionClient


def test_parse_index_html_discovers_policy_links() -> None:
    html = """
    <html>
      <body>
        <a href="/policies/mp-123.html">Medical Policy SURG-001 Knee Arthroscopy</a>
        <a href="/providers/manual">Provider Manual</a>
        <a href="/guidelines/gl-55.html">Clinical UM Guideline CARD-002 Cardiac Imaging</a>
      </body>
    </html>
    """

    client = AnthemPolicyIngestionClient(
        market="IN",
        line_of_business="COMMERCIAL",
        base_url="https://example.org",
    )

    entries = client.parse_index_html(html, source_url="https://example.org/index")

    assert len(entries) == 2
    assert entries[0].policy_id == "SURG-001"
    assert entries[0].url == "https://example.org/policies/mp-123.html"
    assert entries[1].source_type == "clinical_um_guideline"


def test_parse_index_html_finds_embedded_policy_urls() -> None:
    html = """
    <html>
      <body>
        <script>
          window.__INITIAL_STATE__ = {"policies":["https://www.anthem.com/medpolicies/abc/active/mp_pw_a044145.html"]};
        </script>
      </body>
    </html>
    """

    client = AnthemPolicyIngestionClient(
        market="IN",
        line_of_business="COMMERCIAL",
        base_url="https://example.org",
    )

    entries = client.parse_index_html(html, source_url="https://example.org/index")

    assert len(entries) == 1
    assert entries[0].policy_id == "A044145"


def test_parse_policy_html_normalizes_document() -> None:
    html = """
    <html>
      <body>
        <main>
          <h1>Medical Policy SURG-001 Knee Arthroscopy</h1>
          <p>Effective Date: January 15, 2026</p>
          <p>Last Reviewed: February 1, 2026</p>
          <h2>Overview</h2>
          <p>Prior authorization may be required for outpatient surgery.</p>
          <h2>Criteria</h2>
          <p>Medical necessity must be documented.</p>
        </main>
      </body>
    </html>
    """

    client = AnthemPolicyIngestionClient(
        market="IN",
        line_of_business="COMMERCIAL",
        base_url="https://example.org",
    )

    document = client.parse_policy_html(
        html,
        source_url="https://example.org/policies/surg-001",
        fallback_title="Fallback title",
        fallback_policy_id="FALLBACK-001",
    )

    assert document.policy_id == "SURG-001"
    assert document.title == "Medical Policy SURG-001 Knee Arthroscopy"
    assert document.effective_date is not None
    assert document.last_reviewed_date is not None
    assert "prior_authorization" in document.tags
    assert "medical_necessity" in document.tags
    assert document.section_titles == ["Medical Policy SURG-001 Knee Arthroscopy", "Overview", "Criteria"]
