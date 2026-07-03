#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反偏见检查工具 - 结构化投资决策质量控制

参考芒格的快速否决清单和逆向思维，在最终决策前增加反偏见检查。
"""

import sys
import json
import math
from decimal import Decimal, getcontext
from collections import Counter
from typing import Dict, List, Any, Optional

getcontext().prec = 10


class BiasChecker:
    """结构化反偏见机制"""

    def __init__(self):
        self.rejection_reasons = []
        self.warnings = []
        self.info_richness_score = 0

    def run_full_check(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行完整的反偏见检查

        Args:
            analysis_data: 包含财务数据、分析结论等的字典

        Returns:
            检查结果字典
        """
        results = {
            "quick_rejection": self.quick_rejection_checklist(analysis_data),
            "inverse_analysis": self.inverse_analysis(analysis_data),
            "information_richness": self.assess_information_richness(analysis_data),
            "consensus_check": self.check_consensus_risk(analysis_data),
            "overall_assessment": None,
            "recommendations": []
        }

        # 综合评估
        results["overall_assessment"] = self._assess_overall(results)
        results["recommendations"] = self._generate_recommendations(results)

        return results

    def quick_rejection_checklist(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        8条红线一票否决（参考芒格的投资原则）

        Returns:
            每条红线的检查结果
        """
        checks = {}

        # 1. 财务数据异常（本福特定律）
        financials = data.get("financials", {})
        if financials.get("revenues") or financials.get("profits"):
            checks["财务数据异常"] = self.check_benford_law(financials)
        else:
            checks["财务数据异常"] = {"status": "SKIP", "reason": "无财务数据"}

        # 2. 商业模式难懂（5句话测试）
        business_description = data.get("business_model", "")
        checks["商业模式难懂"] = self.check_business_clarity(business_description)

        # 3. 管理层诚信问题
        management_data = data.get("management", {})
        checks["管理层诚信问题"] = self.check_management_integrity(management_data)

        # 4. 行业天花板明显
        industry_data = data.get("industry", {})
        checks["行业天花板明显"] = self.check_industry_ceiling(industry_data)

        # 5. 护城河不清晰
        moat_data = data.get("moat", {})
        checks["护城河不清晰"] = self.check_moat(moat_data)

        # 6. 估值过度乐观
        valuation = data.get("valuation", {})
        checks["估值过度乐观"] = self.check_valuation_sanity(valuation)

        # 7. 与市场共识一致
        consensus = data.get("market_consensus", {})
        checks["与市场共识一致"] = self.check_consensus_alignment(consensus)

        # 8. 5句话说不清楚（镜子测试）
        checks["镜子测试失败"] = self.mirror_test(business_description)

        return checks

    def check_benford_law(self, financials: Dict[str, Any]) -> Dict[str, Any]:
        """
        本福特定律检测：首位数字分布检测财报造假

        正常的财务数字首位数字应符合对数分布：
        1出现约30%，2出现约18%，9出现约5%
        """
        numbers = []

        # 收集财务数字
        for key in ["revenues", "profits", "assets", "cash_flows"]:
            if key in financials and isinstance(financials[key], list):
                numbers.extend([abs(float(x)) for x in financials[key] if x and float(x) != 0])

        if len(numbers) < 10:
            return {
                "status": "SKIP",
                "reason": "数据点不足（需要至少10个数据点）",
                "suspicious": False
            }

        # 提取首位数字
        first_digits = []
        for n in numbers:
            if n > 0:
                # 转为字符串并取第一个非零数字
                n_str = f"{n:.10e}".split('e')[0].replace('.', '').replace('-', '')
                first_digit = int(n_str[0]) if n_str[0] != '0' else int(n_str[1])
                if 1 <= first_digit <= 9:
                    first_digits.append(first_digit)

        if len(first_digits) < 10:
            return {
                "status": "SKIP",
                "reason": "有效数据点不足",
                "suspicious": False
            }

        # 统计观察频率
        observed = Counter(first_digits)
        n_total = len(first_digits)

        # 本福特定律期望分布
        expected = {d: math.log10(1 + 1/d) for d in range(1, 10)}

        # 卡方检验
        chi_square = 0
        for d in range(1, 10):
            observed_count = observed.get(d, 0)
            expected_count = n_total * expected[d]
            if expected_count > 0:
                chi_square += (observed_count - expected_count) ** 2 / expected_count

        # 自由度=8，显著性水平0.05，临界值≈15.51
        # 显著性水平0.01，临界值≈20.09
        suspicious = chi_square > 15.51
        highly_suspicious = chi_square > 20.09

        status = "FAIL" if highly_suspicious else ("WARNING" if suspicious else "PASS")

        return {
            "status": status,
            "chi_square": round(chi_square, 2),
            "threshold": 15.51,
            "suspicious": suspicious,
            "highly_suspicious": highly_suspicious,
            "message": "财务数据首位数字分布异常，可能存在人为修饰" if suspicious else "通过本福特定律检验",
            "observed_distribution": dict(observed),
            "sample_size": n_total
        }

    def check_business_clarity(self, description: str) -> Dict[str, Any]:
        """商业模式是否清晰（字数和复杂度检查）"""
        if not description:
            return {
                "status": "SKIP",
                "reason": "无商业模式描述"
            }

        # 简单检查：5句话约200-400字
        word_count = len(description)
        sentence_count = description.count('。') + description.count('.') + description.count('！') + description.count('?')

        if sentence_count > 8:
            status = "WARNING"
            message = f"商业模式描述过于复杂（{sentence_count}句话），可能说不清楚"
        elif word_count > 500:
            status = "WARNING"
            message = f"商业模式描述过长（{word_count}字），不够简洁"
        else:
            status = "PASS"
            message = "商业模式描述简洁清晰"

        return {
            "status": status,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "message": message
        }

    def check_management_integrity(self, management_data: Dict[str, Any]) -> Dict[str, Any]:
        """管理层诚信检查"""
        if not management_data:
            return {
                "status": "SKIP",
                "reason": "无管理层数据"
            }

        warnings = []

        # 检查历史违规
        if management_data.get("violations", 0) > 0:
            warnings.append(f"历史违规{management_data['violations']}次")

        # 检查股权质押比例
        pledge_ratio = management_data.get("pledge_ratio", 0)
        if pledge_ratio > 0.5:
            warnings.append(f"股权质押比例过高（{pledge_ratio*100:.1f}%）")

        # 检查减持
        if management_data.get("recent_reduction", False):
            warnings.append("近期有管理层减持行为")

        if warnings:
            return {
                "status": "WARNING",
                "warnings": warnings,
                "message": "管理层存在诚信风险"
            }
        else:
            return {
                "status": "PASS",
                "message": "未发现管理层诚信问题"
            }

    def check_industry_ceiling(self, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        """行业天花板检查"""
        if not industry_data:
            return {
                "status": "SKIP",
                "reason": "无行业数据"
            }

        # 检查市场份额
        market_share = industry_data.get("market_share", 0)
        if market_share > 0.4:
            return {
                "status": "WARNING",
                "market_share": market_share,
                "message": f"市场份额已达{market_share*100:.1f}%，增长空间有限"
            }

        # 检查行业增长率
        growth_rate = industry_data.get("industry_growth_rate", 0)
        if growth_rate < 0.05:
            return {
                "status": "WARNING",
                "growth_rate": growth_rate,
                "message": f"行业增长率仅{growth_rate*100:.1f}%，可能已进入成熟期"
            }

        return {
            "status": "PASS",
            "message": "行业仍有增长空间"
        }

    def check_moat(self, moat_data: Dict[str, Any]) -> Dict[str, Any]:
        """护城河检查"""
        if not moat_data:
            return {
                "status": "WARNING",
                "reason": "未评估护城河",
                "message": "护城河不清晰，需要补充分析"
            }

        # 检查护城河类型
        moat_types = moat_data.get("types", [])
        moat_score = moat_data.get("score", 0)

        if not moat_types:
            return {
                "status": "WARNING",
                "message": "未识别出明确的护城河类型"
            }

        if moat_score < 5:
            return {
                "status": "WARNING",
                "score": moat_score,
                "message": f"护城河较弱（评分{moat_score}/10）"
            }

        return {
            "status": "PASS",
            "types": moat_types,
            "score": moat_score,
            "message": "护城河清晰"
        }

    def check_valuation_sanity(self, valuation: Dict[str, Any]) -> Dict[str, Any]:
        """估值合理性检查"""
        if not valuation:
            return {
                "status": "SKIP",
                "reason": "无估值数据"
            }

        warnings = []

        # 检查PE
        pe = valuation.get("pe")
        if pe and pe > 50:
            warnings.append(f"PE过高（{pe:.1f}）")

        # 检查PB
        pb = valuation.get("pb")
        if pb and pb > 10:
            warnings.append(f"PB过高（{pb:.1f}）")

        # 检查PEG
        peg = valuation.get("peg")
        if peg and peg > 2:
            warnings.append(f"PEG过高（{peg:.1f}），增速不匹配估值")

        # 检查安全边际
        margin_of_safety = valuation.get("margin_of_safety", 0)
        if margin_of_safety < 0.15:
            warnings.append(f"安全边际不足（{margin_of_safety*100:.1f}%）")

        if warnings:
            return {
                "status": "WARNING",
                "warnings": warnings,
                "message": "估值可能过度乐观"
            }
        else:
            return {
                "status": "PASS",
                "message": "估值合理"
            }

    def check_consensus_alignment(self, consensus: Dict[str, Any]) -> Dict[str, Any]:
        """与市场共识一致性检查"""
        if not consensus:
            return {
                "status": "SKIP",
                "reason": "无市场共识数据"
            }

        # 检查机构评级
        analyst_rating = consensus.get("analyst_rating", "")
        if analyst_rating in ["强烈推荐", "买入", "Strong Buy", "Buy"]:
            return {
                "status": "WARNING",
                "rating": analyst_rating,
                "message": "与市场共识高度一致，需要独立思考为何跟随"
            }

        return {
            "status": "PASS",
            "message": "与市场共识有差异，体现独立判断"
        }

    def mirror_test(self, description: str) -> Dict[str, Any]:
        """
        镜子测试：能否用5句话说清楚这是什么生意

        参考段永平的投资原则：说不清楚的生意不投
        """
        if not description:
            return {
                "status": "FAIL",
                "reason": "无商业模式描述",
                "message": "❌ 镜子测试失败：无法清晰描述商业模式"
            }

        # 简单启发式检查
        sentence_count = description.count('。') + description.count('.')

        if sentence_count > 7:
            return {
                "status": "WARNING",
                "sentence_count": sentence_count,
                "message": f"⚠️ 镜子测试存疑：需要{sentence_count}句话才能说清楚"
            }
        elif 3 <= sentence_count <= 5:
            return {
                "status": "PASS",
                "sentence_count": sentence_count,
                "message": "✅ 镜子测试通过：商业模式简洁清晰"
            }
        else:
            return {
                "status": "PASS",
                "sentence_count": sentence_count,
                "message": "✅ 镜子测试通过"
            }

    def inverse_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        逆向检验：如果这个股票会失败，原因是什么？

        强制思考失败场景，避免过度乐观
        """
        conclusion = data.get("conclusion", {})
        recommendation = conclusion.get("recommendation", "")

        # 基于现有数据推断失败场景
        failure_scenarios = []

        # 1. 竞争风险
        moat = data.get("moat", {})
        if not moat or moat.get("score", 0) < 6:
            failure_scenarios.append({
                "scenario": "竞争对手攻破护城河",
                "probability": "中等",
                "impact": "估值腰斩",
                "trigger": "护城河较弱，新技术或新模式出现"
            })

        # 2. 估值风险
        valuation = data.get("valuation", {})
        if valuation.get("pe", 0) > 30:
            failure_scenarios.append({
                "scenario": "估值泡沫破裂",
                "probability": "中高",
                "impact": "回调30-50%",
                "trigger": "盈利不及预期或市场风格切换"
            })

        # 3. 行业周期风险
        industry = data.get("industry", {})
        if industry.get("cyclical", False):
            failure_scenarios.append({
                "scenario": "行业下行周期",
                "probability": "周期性",
                "impact": "业绩大幅下滑",
                "trigger": "宏观经济衰退或政策调控"
            })

        # 4. 管理层风险
        management = data.get("management", {})
        if management.get("violations", 0) > 0:
            failure_scenarios.append({
                "scenario": "管理层道德风险",
                "probability": "低但致命",
                "impact": "股价归零",
                "trigger": "财务造假或重大违规"
            })

        # 如果没有识别出失败场景，给出通用风险
        if not failure_scenarios:
            failure_scenarios = [
                {
                    "scenario": "黑天鹅事件",
                    "probability": "低",
                    "impact": "不可预测",
                    "trigger": "行业政策突变、不可抗力事件"
                }
            ]

        return {
            "failure_scenarios": failure_scenarios,
            "worst_case": "最坏情况下可能损失50%+本金",
            "mitigation": "建议设置止损位，控制单一标的仓位<15%"
        }

    def assess_information_richness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        信息丰富度评级：A/B/C

        A级：财报完整+多源验证+行业报告
        B级：公开数据完整
        C级：数据稀缺，仅供参考
        """
        score = 0
        details = []

        # 检查数据完整性
        if data.get("financials"):
            score += 3
            details.append("✅ 财务数据完整")
        else:
            details.append("❌ 缺少财务数据")

        if data.get("valuation"):
            score += 2
            details.append("✅ 估值数据完整")
        else:
            details.append("❌ 缺少估值数据")

        if data.get("news") and len(data["news"]) >= 5:
            score += 2
            details.append(f"✅ 新闻数据丰富（{len(data['news'])}条）")
        else:
            details.append("⚠️ 新闻数据较少")

        if data.get("industry"):
            score += 1
            details.append("✅ 行业数据完整")

        if data.get("management"):
            score += 1
            details.append("✅ 管理层数据完整")

        if data.get("cross_verified", False):
            score += 1
            details.append("✅ 数据已交叉验证")

        # 评级
        if score >= 8:
            grade = "A"
            message = "信息丰富度A级：数据完整且多源验证，可作为重仓依据"
        elif score >= 5:
            grade = "B"
            message = "信息丰富度B级：公开数据完整，可作为配置参考"
        else:
            grade = "C"
            message = "信息丰富度C级：数据稀缺，仅供参考，不建议重仓"

        return {
            "grade": grade,
            "score": score,
            "max_score": 10,
            "message": message,
            "details": details
        }

    def check_consensus_risk(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        反共识检查：如果和市场共识完全一致，需要说明为什么敢跟随

        避免"群体思维"陷阱
        """
        consensus = data.get("market_consensus", {})

        if not consensus:
            return {
                "status": "PASS",
                "message": "无市场共识数据，判断独立"
            }

        # 检查情绪极端程度
        sentiment_score = data.get("sentiment", {}).get("score", 0.5)

        if sentiment_score > 0.8:
            return {
                "status": "WARNING",
                "sentiment": sentiment_score,
                "message": "⚠️ 市场情绪过度乐观（{:.0%}），警惕羊群效应".format(sentiment_score),
                "suggestion": "建议等待回调或分批建仓"
            }
        elif sentiment_score < 0.2:
            return {
                "status": "WARNING",
                "sentiment": sentiment_score,
                "message": "⚠️ 市场情绪过度悲观（{:.0%}），可能存在错杀机会".format(sentiment_score),
                "suggestion": "如基本面未恶化，可考虑逆向布局"
            }
        else:
            return {
                "status": "PASS",
                "message": "市场情绪中性，共识风险较低"
            }

    def _assess_overall(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """综合评估所有检查结果"""
        quick_rejection = results["quick_rejection"]
        info_richness = results["information_richness"]

        # 统计红线触发数量
        fail_count = sum(1 for v in quick_rejection.values()
                        if isinstance(v, dict) and v.get("status") == "FAIL")
        warning_count = sum(1 for v in quick_rejection.values()
                           if isinstance(v, dict) and v.get("status") == "WARNING")

        if fail_count > 0:
            risk_level = "HIGH"
            message = f"⛔ 高风险：触发{fail_count}条红线，不建议投资"
        elif warning_count >= 3:
            risk_level = "MEDIUM-HIGH"
            message = f"⚠️ 中高风险：触发{warning_count}个警告，需谨慎评估"
        elif warning_count > 0:
            risk_level = "MEDIUM"
            message = f"⚠️ 中等风险：触发{warning_count}个警告，可考虑但需控制仓位"
        else:
            risk_level = "LOW"
            message = "✅ 低风险：通过所有快速否决检查"

        return {
            "risk_level": risk_level,
            "fail_count": fail_count,
            "warning_count": warning_count,
            "information_grade": info_richness["grade"],
            "message": message
        }

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """基于检查结果生成操作建议"""
        recommendations = []
        overall = results["overall_assessment"]
        info_richness = results["information_richness"]

        # 风险等级建议
        if overall["risk_level"] == "HIGH":
            recommendations.append("🚫 强烈建议：观望或放弃，等待更好标的")
            recommendations.append("📊 如果坚持投资，仓位不超过3%")
        elif overall["risk_level"] == "MEDIUM-HIGH":
            recommendations.append("⚠️ 建议：谨慎投资，深入研究警告项")
            recommendations.append("📊 推荐仓位：3-5%（试探性建仓）")
        elif overall["risk_level"] == "MEDIUM":
            recommendations.append("✅ 建议：可以投资，但需控制仓位")
            recommendations.append("📊 推荐仓位：5-10%")
        else:
            recommendations.append("✅ 建议：通过质量检查，可作为核心持仓")
            recommendations.append("📊 推荐仓位：10-15%（根据个人风险偏好）")

        # 信息丰富度建议
        if info_richness["grade"] == "C":
            recommendations.append("📉 信息丰富度不足，建议补充研究后再决策")
        elif info_richness["grade"] == "B":
            recommendations.append("📊 信息丰富度尚可，建议关注后续财报和新闻")
        else:
            recommendations.append("📈 信息丰富度优秀，数据支持充分")

        # 逆向分析建议
        failure_scenarios = results["inverse_analysis"]["failure_scenarios"]
        if failure_scenarios:
            recommendations.append(f"🔍 警惕{len(failure_scenarios)}个潜在失败场景，建议设置止损")

        return recommendations


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="反偏见检查工具")
    parser.add_argument("--data", type=str, help="JSON格式的分析数据文件路径")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")

    args = parser.parse_args()

    if args.data:
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        # 示例数据
        data = {
            "financials": {
                "revenues": [100, 120, 150, 180, 200],
                "profits": [20, 25, 30, 36, 40]
            },
            "business_model": "高端白酒品牌，稀缺性驱动，经销商网络稳定，定价权强，现金流充沛。",
            "valuation": {
                "pe": 28.5,
                "pb": 8.2,
                "peg": 1.9,
                "margin_of_safety": 0.10
            },
            "moat": {
                "types": ["品牌", "稀缺性"],
                "score": 8
            },
            "sentiment": {
                "score": 0.72
            }
        }

    checker = BiasChecker()
    results = checker.run_full_check(data)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        # 格式化输出
        print("\n" + "="*60)
        print("🔍 反偏见检查报告")
        print("="*60)

        print("\n【快速否决检查】")
        for check_name, result in results["quick_rejection"].items():
            if isinstance(result, dict):
                status = result.get("status", "UNKNOWN")
                message = result.get("message", result.get("reason", ""))
                icon = "✅" if status == "PASS" else ("⚠️" if status == "WARNING" else ("❌" if status == "FAIL" else "⏭️"))
                print(f"{icon} {check_name}: {message}")

        print("\n【逆向分析 - 失败场景】")
        for scenario in results["inverse_analysis"]["failure_scenarios"]:
            print(f"  • {scenario['scenario']}")
            print(f"    概率: {scenario['probability']} | 影响: {scenario['impact']}")

        print("\n【信息丰富度评级】")
        info = results["information_richness"]
        print(f"  等级: {info['grade']} ({info['score']}/{info['max_score']})")
        print(f"  {info['message']}")

        print("\n【综合评估】")
        overall = results["overall_assessment"]
        print(f"  风险等级: {overall['risk_level']}")
        print(f"  {overall['message']}")

        print("\n【操作建议】")
        for rec in results["recommendations"]:
            print(f"  {rec}")

        print("\n" + "="*60)


if __name__ == "__main__":
    main()
