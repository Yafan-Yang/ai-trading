#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""valuation.py 单元测试"""

import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from valuation import dcf, three_scenarios


class TestValuation(unittest.TestCase):

    def test_dcf_hand_verified(self):
        """手工验算案例：FCF=100, 增长10%两年, 折现10%, 永续2%"""
        r = dcf(100, [0.10, 0.10], 0.10, 0.02)
        # Year1 pv=100, Year2 pv=100
        self.assertAlmostEqual(r["forecast_pv"], 200.0, places=1)
        # 终值 = 121*1.02/(0.10-0.02) = 1542.75
        self.assertAlmostEqual(r["terminal_value"], 1542.75, places=1)
        # 终值现值 = 1542.75/1.21 = 1275
        self.assertAlmostEqual(r["terminal_pv"], 1275.0, places=1)
        # 企业价值 = 200 + 1275 = 1475
        self.assertAlmostEqual(r["enterprise_value"], 1475.0, places=1)

    def test_dcf_yearly_breakdown(self):
        """逐年现金流计算正确"""
        r = dcf(100, [0.10, 0.10], 0.10, 0.02)
        self.assertEqual(len(r["yearly"]), 2)
        self.assertAlmostEqual(r["yearly"][0]["fcf"], 110.0, places=1)
        self.assertAlmostEqual(r["yearly"][1]["fcf"], 121.0, places=1)

    def test_dcf_terminal_growth_too_high(self):
        """永续增长率>=折现率应抛异常"""
        with self.assertRaises(ValueError):
            dcf(100, [0.10], 0.05, 0.08)

    def test_dcf_terminal_equals_discount(self):
        """永续增长率==折现率应抛异常（除零风险）"""
        with self.assertRaises(ValueError):
            dcf(100, [0.10], 0.08, 0.08)

    def test_three_scenarios_ordering(self):
        """乐观情景估值应高于悲观情景"""
        scenarios = {
            "optimistic": [0.18, 0.16, 0.14],
            "base": [0.12, 0.10, 0.08],
            "pessimistic": [0.06, 0.05, 0.04],
        }
        r = three_scenarios(1000, scenarios, 0.083, 0.03, shares=100)
        opt = r["scenarios"]["optimistic"]["value_per_share"]
        base = r["scenarios"]["base"]["value_per_share"]
        pess = r["scenarios"]["pessimistic"]["value_per_share"]
        self.assertGreater(opt, base)
        self.assertGreater(base, pess)

    def test_three_scenarios_value_range(self):
        """每股价值区间的 low/high 与情景一致"""
        scenarios = {
            "optimistic": [0.18, 0.16],
            "base": [0.12, 0.10],
            "pessimistic": [0.06, 0.05],
        }
        r = three_scenarios(1000, scenarios, 0.083, 0.03, shares=100)
        rng = r["value_per_share_range"]
        self.assertEqual(rng["high"], r["scenarios"]["optimistic"]["value_per_share"])
        self.assertEqual(rng["low"], r["scenarios"]["pessimistic"]["value_per_share"])

    def test_per_share_calculation(self):
        """每股价值 = 企业价值 / 总股本"""
        r = dcf(100, [0.10, 0.10], 0.10, 0.02)
        scenarios = {"base": [0.10, 0.10]}
        rs = three_scenarios(100, scenarios, 0.10, 0.02, shares=10)
        expected = r["enterprise_value"] / 10
        self.assertAlmostEqual(rs["scenarios"]["base"]["value_per_share"],
                               expected, places=1)

    def test_no_shares_no_per_share(self):
        """不提供股本时不应有每股价值字段"""
        scenarios = {"base": [0.10]}
        r = three_scenarios(100, scenarios, 0.10, 0.02)
        self.assertNotIn("value_per_share", r["scenarios"]["base"])
        self.assertNotIn("value_per_share_range", r)


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestValuation)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite).wasSuccessful()


if __name__ == "__main__":
    sys.exit(0 if run_tests() else 1)
