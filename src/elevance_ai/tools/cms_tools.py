"""Tool wrappers for CMS-related operations."""

from __future__ import annotations

from elevance_ai.domain.evidence import Evidence


def cms_disclaimer_evidence() -> Evidence:
    """Return a standard evidence note for CMS/public-source limitations."""

    return Evidence(
        source_type="cms_public_guidance",
        title="CMS Public Coverage Data Scope",
        source_id="cms-public-scope",
        excerpt=(
            "CMS public coverage references can support research, but they do not replace "
            "payer-specific policy, plan benefits, or authorized member verification."
        ),
        source_url="https://www.cms.gov/",
    )
