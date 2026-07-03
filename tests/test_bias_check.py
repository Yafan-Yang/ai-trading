#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bias_check.py 单元测试
"""

import sys
import os
import json
import unittest

# 添加tools目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from bias_check import BiasChecker


class TestBiasChecker(unittest.TestCase):
    """BiasChecker单元测试"""

    def setUp(self):
        """测试前准备"""
        self.checker = BiasChecker()

    def test_benford_law_normal(self):
        """测试本福特定律 - 正常数据"""
        financials = {
            "revenues": [120, 235, 318, 142, 189, 256, 371, 198, 215, 328],
            "profits": [12, 23, 31, 14, 18, 25, 37, 19, 21, 32]
        }
        result = self.checker.check_benford_law(financials)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["suspicious"])

    def test_benford_law_suspicious(self):
        """测试本福特定律 - 可疑数据（全是9开头）"""
        financials = {
            "revenues": [98, 97, 99, 96, 98, 97, 99, 98, 97, 96, 99, 98]
        }
        result = self.checker.check_benford_law(financials)
        # 这个数据集应该触发警告或失败
        self.assertIn(result["status"], ["WARNING", "FAIL"])
        self.assertTrue(result["suspicious"])

    def test_benford_law_insufficient_data(self):
        """测试本福特定律 - 数据不足"""
        financials = {
            "revenues": [120, 235]
        }
        result = self.checker.check_benford_law(financials)
        self.assertEqual(result["status"], "SKIP")

    def test_business_clarity_pass(self):
        """测试商业模式清晰度 - 通过"""
        description = "高端白酒品牌，稀缺性驱动。经销商网络稳定，定价权强。现金流充沛。"
        result = self.checker.check_business_clarity(description)
        self.assertEqual(result["status"], "PASS")

    def test_business_clarity_too_complex(self):
        """测试商业模式清晰度 - 过于复杂"""
        description = "。" * 10  # 10句话
        result = self.checker.check_business_clarity(description)
        self.assertEqual(result["status"], "WARNING")

    def test_management_integrity_pass(self):
        """测试管理层诚信 - 通过"""
        management_data = {
            "violations": 0,
            "pledge_ratio": 0.1,
            "recent_reduction": False
        }
        result = self.checker.check_management_integrity(management_data)
        self.assertEqual(result["status"], "PASS")

    def test_management_integrity_warning(self):
        """测试管理层诚信 - 警告"""
        management_data = {
            "violations": 2,
            "pledge_ratio": 0.6,
            "recent_reduction": True
        }
        result = self.checker.check_management_integrity(management_data)
        self.assertEqual(result["status"], "WARNING")
        self.assertGreater(len(result["warnings"]), 0)

    def test_valuation_sanity_pass(self):
        """测试估值合理性 - 通过"""
        valuation = {
            "pe": 25,
            "pb": 5,
            "peg": 1.5,
            "margin_of_safety": 0.20
        }
        result = self.checker.check_valuation_sanity(valuation)
        self.assertEqual(result["status"], "PASS")

    def test_valuation_sanity_warning(self):
        """测试估值合理性 - 警告"""
        valuation = {
            "pe": 60,
            "pb": 15,
            "peg": 3,
            "margin_of_safety": 0.05
        }
        result = self.checker.check_valuation_sanity(valuation)
        self.assertEqual(result["status"], "WARNING")

    def test_mirror_test_pass(self):
        """测试镜子测试 - 通过"""
        description = "一句话。两句话。三句话。四句话。五句话。"
        result = self.checker.mirror_test(description)
        self.assertEqual(result["status"], "PASS")

    def test_mirror_test_warning(self):
        """测试镜子测试 - 警告"""
        description = "。" * 8  # 8句话
        result = self.checker.mirror_test(description)
        self.assertEqual(result["status"], "WARNING")

    def test_mirror_test_fail(self):
        """测试镜子测试 - 失败"""
        description = ""
        result = self.checker.mirror_test(description)
        self.assertEqual(result["status"], "FAIL")

    def test_information_richness_grade_a(self):
        """测试信息丰富度 - A级"""
        data = {
            "financials": {"revenues": [100, 120]},
            "valuation": {"pe": 25},
            "news": ["新闻1", "新闻2", "新闻3", "新闻4", "新闻5"],
            "industry": {},
            "management": {},
            "cross_verified": True
        }
        result = self.checker.assess_information_richness(data)
        self.assertEqual(result["grade"], "A")

    def test_information_richness_grade_b(self):
        """测试信息丰富度 - B级"""
        data = {
            "financials": {"revenues": [100, 120]},
            "valuation": {"pe": 25},
            "news": ["新闻1", "新闻2"]
        }
        result = self.checker.assess_information_richness(data)
        self.assertEqual(result["grade"], "B")

    def test_information_richness_grade_c(self):
        """测试信息丰富度 - C级"""
        data = {
            "financials": {"revenues": [100, 120]}
        }
        result = self.checker.assess_information_richness(data)
        self.assertEqual(result["grade"], "C")

    def test_consensus_risk_high_optimism(self):
        """测试共识风险 - 过度乐观"""
        data = {
            "market_consensus": {"analyst_rating": "买入"},
            "sentiment": {"score": 0.85}
        }
        result = self.checker.check_consensus_risk(data)
        self.assertEqual(result["status"], "WARNING")

    def test_consensus_risk_neutral(self):
        """测试共识风险 - 中性"""
        data = {
            "sentiment": {"score": 0.5}
        }
        result = self.checker.check_consensus_risk(data)
        self.assertEqual(result["status"], "PASS")

    def test_inverse_analysis(self):
        """测试逆向分析"""
        data = {
            "conclusion": {"recommendation": "买入"},
            "moat": {"score": 4},
            "valuation": {"pe": 35}
        }
        result = self.checker.inverse_analysis(data)
        self.assertIn("failure_scenarios", result)
        self.assertGreater(len(result["failure_scenarios"]), 0)

    def test_full_check_low_risk(self):
        """测试完整检查 - 低风险"""
        data = {
            "financials": {
                "revenues": [120, 235, 318, 142, 189],
                "profits": [12, 23, 31, 14, 18]
            },
            "business_model": "高端白酒品牌。稀缺性驱动。经销商稳定。定价权强。现金流充沛。",
            "valuation": {
                "pe": 25,
                "pb": 5,
                "peg": 1.5,
                "margin_of_safety": 0.20
            },
            "moat": {
                "types": ["品牌", "稀缺性"],
                "score": 8
            },
            "management": {
                "violations": 0,
                "pledge_ratio": 0.1,
                "recent_reduction": False
            },
            "sentiment": {"score": 0.5},
            "news": ["新闻1", "新闻2", "新闻3", "新闻4", "新闻5"],
            "industry": {"market_share": 0.2, "industry_growth_rate": 0.1}
        }
        result = self.checker.run_full_check(data)
        self.assertEqual(result["overall_assessment"]["risk_level"], "LOW")

    def test_full_check_high_risk(self):
        """测试完整检查 - 高风险"""
        data = {
            "business_model": "",  # 镜子测试失败
            "valuation": {
                "pe": 80,  # 估值过高
                "margin_of_safety": 0.02  # 安全边际不足
            }
        }
        result = self.checker.run_full_check(data)
        self.assertIn(result["overall_assessment"]["risk_level"], ["HIGH", "MEDIUM-HIGH"])


def run_tests():
    """运行所有测试"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBiasChecker)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
