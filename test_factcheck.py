"""
test_factcheck.py
Unit tests for the Fact-Checking Agent pipeline.
"""

import os
import unittest
from factcheck_engine import (
    extract_text_from_pdf,
    extract_claims_from_text,
    verify_claim,
    process_pdf_document
)

class TestFactCheckPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.trap_pdf_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "sample_marketing_trap_document.pdf"
        )

    def test_trap_pdf_exists(self):
        self.assertTrue(os.path.exists(self.trap_pdf_path), "Trap document PDF must exist.")

    def test_text_extraction(self):
        pages = extract_text_from_pdf(self.trap_pdf_path)
        self.assertGreaterEqual(len(pages), 1, "Must extract at least 1 page.")
        self.assertIn("smartphone", pages[0]["text"].lower())

    def test_claim_extraction(self):
        pages = extract_text_from_pdf(self.trap_pdf_path)
        claims = extract_claims_from_text(pages)
        self.assertGreater(len(claims), 0, "Must extract at least one claim.")
        
        # Check claim types
        types = {c["type"] for c in claims}
        self.assertTrue(len(types) >= 2, "Should identify diverse claim types.")

    def test_outdated_stat_flagging(self):
        fake_claim = {
            "id": "CLM-TEST-001",
            "page": 1,
            "claim_text": "As of 2024, global smartphone users reached 2.5 billion worldwide.",
            "type": "Statistical / Ratio",
            "search_query": "smartphone users reached 2.5 billion"
        }
        res = verify_claim(fake_claim)
        self.assertEqual(res["status"], "INACCURATE")
        self.assertIn("4.88", res["real_fact"])

    def test_fabricated_stat_flagging(self):
        fake_claim = {
            "id": "CLM-TEST-002",
            "page": 1,
            "claim_text": "In a landmark transaction, OpenAI was acquired by Netflix in 2023 for $50 Billion.",
            "type": "Financial / Valuation",
            "search_query": "OpenAI acquired Netflix 50 Billion"
        }
        res = verify_claim(fake_claim)
        self.assertEqual(res["status"], "FALSE")
        self.assertIn("NEVER acquired by Netflix", res["real_fact"])

    def test_verified_fact(self):
        real_claim = {
            "id": "CLM-TEST-003",
            "page": 1,
            "claim_text": "Google was founded in 1998 by Larry Page and Sergey Brin.",
            "type": "Historical Milestone / Date",
            "search_query": "Google founded 1998 Larry Page Sergey Brin"
        }
        res = verify_claim(real_claim)
        self.assertEqual(res["status"], "VERIFIED")

    def test_end_to_end_pipeline(self):
        results = process_pdf_document(self.trap_pdf_path)
        self.assertGreater(results["total_claims"], 0)
        self.assertGreater(results["count_inaccurate"], 0, "Must detect outdated stats in trap doc.")
        self.assertGreater(results["count_false"], 0, "Must detect lies in trap doc.")
        self.assertGreater(results["count_verified"], 0, "Must detect true facts in trap doc.")

if __name__ == "__main__":
    unittest.main()
