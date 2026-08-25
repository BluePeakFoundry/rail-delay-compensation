import unittest

from rail_core import RailScenario, assess, reimbursement_rate_for_delay


class RailCoreTests(unittest.TestCase):
    def base(self, **overrides):
        data = dict(
            disruption_type="delay",
            ticket_price_eur=120.0,
            arrival_delay_minutes=90,
            journey_within_eu_or_operator_eu=True,
            informed_before_purchase=False,
            delay_due_to_passenger=False,
            exceptional_circumstances=False,
            accepted_refund_or_reroute=False,
        )
        data.update(overrides)
        return RailScenario(**data)

    def test_reimbursement_thresholds(self):
        self.assertEqual(reimbursement_rate_for_delay(59), 0.0)
        self.assertEqual(reimbursement_rate_for_delay(60), 0.25)
        self.assertEqual(reimbursement_rate_for_delay(119), 0.25)
        self.assertEqual(reimbursement_rate_for_delay(120), 0.50)

    def test_25_percent_for_60_to_119_minutes(self):
        a = assess(self.base(arrival_delay_minutes=90, ticket_price_eur=120.0))
        self.assertTrue(a.eligible)
        self.assertEqual(a.estimated_reimbursement_eur, 30.0)

    def test_50_percent_for_120_plus_minutes(self):
        a = assess(self.base(arrival_delay_minutes=150, ticket_price_eur=80.0))
        self.assertTrue(a.eligible)
        self.assertEqual(a.estimated_reimbursement_eur, 40.0)
        self.assertEqual(a.reimbursement_rate, 0.5)

    def test_no_compensation_under_60_minutes(self):
        a = assess(self.base(arrival_delay_minutes=45))
        self.assertFalse(a.eligible)
        self.assertEqual(a.estimated_reimbursement_eur, 0.0)
        self.assertEqual(a.status, "retraso_insuficiente")

    def test_blockers_exclude_estimate(self):
        for field in ["informed_before_purchase", "delay_due_to_passenger", "exceptional_circumstances"]:
            a = assess(self.base(**{field: True}))
            self.assertFalse(a.eligible)
            self.assertEqual(a.estimated_reimbursement_eur, 0.0)

    def test_out_of_scope(self):
        a = assess(self.base(journey_within_eu_or_operator_eu=False))
        self.assertFalse(a.eligible)
        self.assertEqual(a.status, "fuera_de_alcance")

    def test_invalid_values(self):
        with self.assertRaises(ValueError):
            reimbursement_rate_for_delay(-1)
        with self.assertRaises(ValueError):
            assess(self.base(disruption_type="missed_connection"))
        with self.assertRaises(ValueError):
            assess(self.base(ticket_price_eur=0))


if __name__ == "__main__":
    unittest.main()
