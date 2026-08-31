import unittest

from seo.decision import make_seo_decision
from seo.models import SEOInput


class TestSEODecision(unittest.TestCase):
    def base_input(self, **overrides):
        values = dict(
            product_id="POD-001",
            platform="Etsy",
            market="US",
            language="en",
            demand_score=78,
            competition_score=43,
            buyer_intent_score=91,
            trend_score=72,
            has_search_data=True,
            has_competitor_data=True,
            has_trend_data=True,
            has_price_data=True,
            has_sales_data=False,
        )
        values.update(overrides)
        return SEOInput(**values)

    def test_strong_opportunity_is_test(self):
        result = make_seo_decision(self.base_input())
        self.assertEqual(result.analysis.raw_opportunity_score, 76)
        self.assertEqual(result.analysis.decision, "TEST")
        self.assertEqual(result.analysis.confidence, 0.80)

    def test_trademark_risk_blocks(self):
        result = make_seo_decision(self.base_input(trademark_risk=True))
        self.assertEqual(result.analysis.risk_level, "CRITICAL")
        self.assertEqual(result.analysis.adjusted_score, 0)
        self.assertEqual(result.analysis.decision, "REJECT")

    def test_low_confidence_forces_review(self):
        result = make_seo_decision(self.base_input(
            has_competitor_data=False,
            has_trend_data=False,
            has_price_data=False,
            has_sales_data=False,
        ))
        self.assertEqual(result.analysis.confidence, 0.30)
        self.assertEqual(result.analysis.decision, "REVIEW")

    def test_invalid_score_fails_closed(self):
        with self.assertRaises(ValueError):
            make_seo_decision(self.base_input(demand_score=101))


if __name__ == "__main__":
    unittest.main()
