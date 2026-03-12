"""
资格评估与指标计算模块
基于专精特新小巨人申报政策要求进行评估
"""

import json
import os
from typing import Dict, Any, List, Tuple
from datetime import datetime

from common.log import logger


class AssessmentCalculator:
    """资格评估计算器"""
    
    def __init__(self):
        # 加载政策规则
        self.rules = self._load_rules()
        logger.info("[专精特新] 评估计算器初始化完成")
    
    def _load_rules(self) -> Dict[str, Any]:
        """加载评估规则"""
        # 这里可以从文件加载，暂时硬编码
        rules = {
            "specialization": {  # 专业化
                "market_years": 3,  # 细分市场≥3年
                "main_revenue_ratio": 70,  # 主营业务占比≥70%
                "revenue_growth_2y": 5,  # 近2年主营业务增长≥5%
            },
            "refinement": {  # 精细化
                "has_it_system": True,  # 有信息系统
                "has_management_cert": True,  # 有管理体系认证
                "asset_liability_ratio": 70,  # 资产负债率≤70%
            },
            "characteristics": {  # 特色化
                "market_share": 10,  # 细分市场占有率≥10%
                "has_own_brand": True,  # 有自主品牌
            },
            "innovation": {  # 创新能力
                "rd_ratio_1b": 3,  # 营收>1亿：研发费用占比≥3%
                "rd_ratio_50m_1b": 6,  # 5000万-1亿：研发费用占比≥6%
                "rd_institution": True,  # 有研发机构
                "patent_count": 2,  # 2项I类知识产权
            },
            "industry_chain": {  # 产业链
                "supplement_shortage": True,  # 补短板
                "fill_blank": True,  # 填空白
                "key_supplier": True,  # 关键供应商
            },
            "other_conditions": {  # 其他条件
                "no_major_accident": True,  # 近3年无重大安全事故
                "provincial_specialized": True,  # 必须是省级专精特新企业
            }
        }
        return rules
    
    async def execute(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行评估计算"""
        try:
            logger.info("[专精特新] 开始资格评估")
            
            # 计算关键指标
            metrics = self._calculate_metrics(company_data)
            
            # 执行资格评估
            assessment = self._assess_qualification(company_data, metrics)
            
            # 生成评估报告
            report = self._generate_assessment_report(assessment, metrics)
            
            result = {
                "qualified": assessment.get("overall_qualified", False),
                "indicators": assessment.get("indicators", {}),
                "metrics": metrics,
                "report": report,
                "suggestions": assessment.get("suggestions", []),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[专精特新] 资格评估完成，结果: {'合格' if result['qualified'] else '不合格'}")
            return result
            
        except Exception as e:
            logger.error(f"[专精特新] 评估计算错误: {e}")
            return {
                "qualified": False,
                "error": str(e),
                "indicators": {},
                "metrics": {},
                "report": f"评估过程中出现错误: {str(e)}",
                "suggestions": ["请检查输入数据的完整性和准确性"]
            }
    
    def _calculate_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """计算关键指标"""
        metrics = {}
        
        # 主营业务占比
        if "main_revenue_2023" in data and "revenue_2023" in data:
            main_revenue = data.get("main_revenue_2023", 0)
            total_revenue = data.get("revenue_2023", 0)
            if total_revenue and total_revenue > 0:
                metrics["main_revenue_ratio"] = (main_revenue / total_revenue) * 100
        
        # 近2年主营业务增长率
        if all(f"main_revenue_{year}" in data for year in [2021, 2022, 2023]):
            try:
                main_2021 = data.get("main_revenue_2021", 0)
                main_2022 = data.get("main_revenue_2022", 0)
                main_2023 = data.get("main_revenue_2023", 0)
                
                if main_2021 > 0 and main_2022 > 0:
                    growth_2022 = ((main_2022 - main_2021) / main_2021) * 100
                    growth_2023 = ((main_2023 - main_2022) / main_2022) * 100
                    metrics["revenue_growth_2y_avg"] = (growth_2022 + growth_2023) / 2
            except:
                pass
        
        # 研发费用占比
        if "rd_expense_2023" in data and "revenue_2023" in data:
            rd_expense = data.get("rd_expense_2023", 0)
            total_revenue = data.get("revenue_2023", 0)
            if total_revenue and total_revenue > 0:
                metrics["rd_expense_ratio"] = (rd_expense / total_revenue) * 100
        
        # 研发人员占比
        if "rd_employee_count" in data and "employee_count" in data:
            rd_employees = data.get("rd_employee_count", 0)
            total_employees = data.get("employee_count", 0)
            if total_employees and total_employees > 0:
                metrics["rd_employee_ratio"] = (rd_employees / total_employees) * 100
        
        # 资产负债率
        if "asset_total" in data and "liability_total" in data:
            assets = data.get("asset_total", 0)
            liabilities = data.get("liability_total", 0)
            if assets and assets > 0:
                metrics["asset_liability_ratio"] = (liabilities / assets) * 100
        
        # 企业年龄（从事细分市场时间）
        if "establishment_year" in data:
            establishment_year = data.get("establishment_year")
            if establishment_year:
                current_year = datetime.now().year
                metrics["company_age"] = current_year - establishment_year
        
        # 市场占有率
        if "market_share" in data:
            metrics["market_share"] = data.get("market_share", 0)
        
        # 专利数量
        if "patent_count" in data:
            metrics["patent_count"] = data.get("patent_count", 0)
        
        return metrics
    
    def _assess_qualification(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估资格"""
        assessment = {
            "indicators": {},
            "suggestions": [],
            "overall_qualified": True
        }
        
        # 1. 专业化评估
        specialization_result = self._assess_specialization(data, metrics)
        assessment["indicators"]["专业化"] = specialization_result
        if not specialization_result.get("passed", False):
            assessment["overall_qualified"] = False
            assessment["suggestions"].extend(specialization_result.get("suggestions", []))
        
        # 2. 精细化评估
        refinement_result = self._assess_refinement(data, metrics)
        assessment["indicators"]["精细化"] = refinement_result
        if not refinement_result.get("passed", False):
            assessment["overall_qualified"] = False
            assessment["suggestions"].extend(refinement_result.get("suggestions", []))
        
        # 3. 特色化评估
        characteristics_result = self._assess_characteristics(data, metrics)
        assessment["indicators"]["特色化"] = characteristics_result
        if not characteristics_result.get("passed", False):
            assessment["overall_qualified"] = False
            assessment["suggestions"].extend(characteristics_result.get("suggestions", []))
        
        # 4. 创新能力评估
        innovation_result = self._assess_innovation(data, metrics)
        assessment["indicators"]["创新能力"] = innovation_result
        if not innovation_result.get("passed", False):
            assessment["overall_qualified"] = False
            assessment["suggestions"].extend(innovation_result.get("suggestions", []))
        
        # 5. 产业链评估
        industry_chain_result = self._assess_industry_chain(data, metrics)
        assessment["indicators"]["产业链"] = industry_chain_result
        if not industry_chain_result.get("passed", False):
            assessment["overall_qualified"] = False
            assessment["suggestions"].extend(industry_chain_result.get("suggestions", []))
        
        # 6. 其他条件评估
        other_conditions_result = self._assess_other_conditions(data, metrics)
        assessment["indicators"]["其他条件"] = other_conditions_result
        if not other_conditions_result.get("passed", False):
            assessment["overall_qualified"] = False
            assessment["suggestions"].extend(other_conditions_result.get("suggestions", []))
        
        return assessment
    
    def _assess_specialization(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估专业化指标"""
        result = {
            "passed": True,
            "checks": [],
            "suggestions": []
        }
        
        rules = self.rules["specialization"]
        
        # 检查1：细分市场≥3年
        company_age = metrics.get("company_age", 0)
        check1 = company_age >= rules["market_years"]
        result["checks"].append({
            "description": f"细分市场≥{rules['market_years']}年",
            "value": f"{company_age}年",
            "passed": check1,
            "required": f"≥{rules['market_years']}年"
        })
        if not check1:
            result["passed"] = False
            result["suggestions"].append(f"企业成立时间{company_age}年，需达到{rules['market_years']}年以上")
        
        # 检查2：主营业务占比≥70%
        main_revenue_ratio = metrics.get("main_revenue_ratio", 0)
        check2 = main_revenue_ratio >= rules["main_revenue_ratio"]
        result["checks"].append({
            "description": f"主营业务占比≥{rules['main_revenue_ratio']}%",
            "value": f"{main_revenue_ratio:.1f}%",
            "passed": check2,
            "required": f"≥{rules['main_revenue_ratio']}%"
        })
        if not check2:
            result["passed"] = False
            result["suggestions"].append(f"主营业务占比{main_revenue_ratio:.1f}%，需达到{rules['main_revenue_ratio']}%以上")
        
        # 检查3：近2年主营业务增长≥5%
        revenue_growth = metrics.get("revenue_growth_2y_avg", 0)
        check3 = revenue_growth >= rules["revenue_growth_2y"]
        result["checks"].append({
            "description": f"近2年主营业务增长≥{rules['revenue_growth_2y']}%",
            "value": f"{revenue_growth:.1f}%",
            "passed": check3,
            "required": f"≥{rules['revenue_growth_2y']}%"
        })
        if not check3:
            result["passed"] = False
            result["suggestions"].append(f"近2年主营业务增长{revenue_growth:.1f}%，需达到{rules['revenue_growth_2y']}%以上")
        
        return result
    
    def _assess_refinement(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估精细化指标"""
        result = {
            "passed": True,
            "checks": [],
            "suggestions": []
        }
        
        rules = self.rules["refinement"]
        
        # 检查1：有信息系统（简化检查）
        has_it_system = data.get("has_it_system", False) or data.get("management_system", "").lower() in ["erp", "crm", "oa"]
        check1 = has_it_system
        result["checks"].append({
            "description": "有信息系统支撑",
            "value": "有" if has_it_system else "无",
            "passed": check1,
            "required": "需要"
        })
        if not check1:
            result["passed"] = False
            result["suggestions"].append("需要建立信息系统（如ERP、CRM、OA等）")
        
        # 检查2：有管理体系认证
        has_management_cert = data.get("has_management_cert", False) or data.get("certifications", "").lower().find("iso") != -1
        check2 = has_management_cert
        result["checks"].append({
            "description": "有管理体系认证",
            "value": "有" if has_management_cert else "无",
            "passed": check2,
            "required": "需要"
        })
        if not check2:
            result["passed"] = False
            result["suggestions"].append("需要获得管理体系认证（如ISO9001等）")
        
        # 检查3：资产负债率≤70%
        asset_liability_ratio = metrics.get("asset_liability_ratio", 0)
        check3 = asset_liability_ratio <= rules["asset_liability_ratio"]
        result["checks"].append({
            "description": f"资产负债率≤{rules['asset_liability_ratio']}%",
            "value": f"{asset_liability_ratio:.1f}%",
            "passed": check3,
            "required": f"≤{rules['asset_liability_ratio']}%"
        })
        if not check3:
            result["passed"] = False
            result["suggestions"].append(f"资产负债率{asset_liability_ratio:.1f}%，需控制在{rules['asset_liability_ratio']}%以下")
        
        return result
    
    def _assess_characteristics(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估特色化指标"""
        result = {
            "passed": True,
            "checks": [],
            "suggestions": []
        }
        
        rules = self.rules["characteristics"]
        
        # 检查1：细分市场占有率≥10%
        market_share = metrics.get("market_share", 0)
        check1 = market_share >= rules["market_share"]
        result["checks"].append({
            "description": f"细分市场占有率≥{rules['market_share']}%",
            "value": f"{market_share:.1f}%",
            "passed": check1,
            "required": f"≥{rules['market_share']}%"
        })
        if not check1:
            result["passed"] = False
            result["suggestions"].append(f"市场占有率{market_share:.1f}%，需达到{rules['market_share']}%以上")
        
        # 检查2：有自主品牌
        has_own_brand = data.get("has_own_brand", False) or data.get("trademark", False)
        check2 = has_own_brand
        result["checks"].append({
            "description": "有自主品牌",
            "value": "有" if has_own_brand else "无",
            "passed": check2,
            "required": "需要"
        })
        if not check2:
            result["passed"] = False
            result["suggestions"].append("需要注册自主品牌商标")
        
        return result
    
    def _assess_innovation(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估创新能力指标"""
        result = {
            "passed": True,
            "checks": [],
            "suggestions": []
        }
        
        rules = self.rules["innovation"]
        revenue_2023 = data.get("revenue_2023", 0)
        
        # 检查1：研发费用占比
        rd_expense_ratio = metrics.get("rd_expense_ratio", 0)
        
        if revenue_2023 > 10000:  # 1亿元以上
            required_ratio = rules["rd_ratio_1b"]
            check1 = rd_expense_ratio >= required_ratio
            description = f"营收>1亿：研发费用占比≥{required_ratio}%"
        elif revenue_2023 >= 5000:  # 5000万-1亿
            required_ratio = rules["rd_ratio_50m_1b"]
            check1 = rd_expense_ratio >= required_ratio
            description = f"营收5000万-1亿：研发费用占比≥{required_ratio}%"
        else:  # 5000万以下
            # 简化处理：使用较高标准
            required_ratio = 6
            check1 = rd_expense_ratio >= required_ratio
            description = f"营收<5000万：研发费用占比建议≥{required_ratio}%"
        
        result["checks"].append({
            "description": description,
            "value": f"{rd_expense_ratio:.1f}%",
            "passed": check1,
            "required": f"≥{required_ratio}%"
        })
        if not check1:
            result["passed"] = False
            result["suggestions"].append(f"研发费用占比{rd_expense_ratio:.1f}%，需达到{required_ratio}%以上")
        
        # 检查2：有研发机构
        has_rd_institution = data.get("rd_institution", False)
        check2 = has_rd_institution
        result["checks"].append({
            "description": "有研发机构",
            "value": "有" if has_rd_institution else "无",
            "passed": check2,
            "required": "需要"
        })
        if not check2:
            result["passed"] = False
            result["suggestions"].append("需要建立研发机构（企业技术中心、工程中心等）")
        
        # 检查3：2项I类知识产权
        patent_count = metrics.get("patent_count", 0)
        check3 = patent_count >= rules["patent_count"]
        result["checks"].append({
            "description": f"拥有{rules['patent_count']}项以上I类知识产权",
            "value": f"{patent_count}项",
            "passed": check3,
            "required": f"≥{rules['patent_count']}项"
        })
        if not check3:
            result["passed"] = False
            result["suggestions"].append(f"专利数量{patent_count}项，需达到{rules['patent_count']}项以上")
        
        return result
    
    def _assess_industry_chain(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估产业链指标"""
        result = {
            "passed": True,
            "checks": [],
            "suggestions": []
        }
        
        rules = self.rules["industry_chain"]
        
        # 检查1：补短板
        supplement_shortage = data.get("supplement_shortage", False)
        check1 = supplement_shortage
        result["checks"].append({
            "description": "在产业链关键领域实现'补短板'",
            "value": "是" if supplement_shortage else "否",
            "passed": check1,
            "required": "需要"
        })
        if not check1:
            result["passed"] = False
            result["suggestions"].append("需要在产业链关键领域实现'补短板'")
        
        # 检查2：填空白
        fill_blank = data.get("fill_blank", False)
        check2 = fill_blank
        result["checks"].append({
            "description": "在产业链关键领域实现'填空白'",
            "value": "是" if fill_blank else "否",
            "passed": check2,
            "required": "需要"
        })
        if not check2:
            result["passed"] = False
            result["suggestions"].append("需要在产业链关键领域实现'填空白'")
        
        # 检查3：关键供应商
        key_supplier = data.get("key_supplier", False) or data.get("core_customers", "")
        check3 = bool(key_supplier)
        result["checks"].append({
            "description": "为国内外知名大企业直接配套",
            "value": "是" if check3 else "否",
            "passed": check3,
            "required": "建议"
        })
        # 这项不是必须的，所以不改变passed状态
        
        return result
    
    def _assess_other_conditions(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """评估其他条件"""
        result = {
            "passed": True,
            "checks": [],
            "suggestions": []
        }
        
        rules = self.rules["other_conditions"]
        
        # 检查1：近3年无重大安全事故
        no_major_accident = data.get("no_major_accident", True)  # 默认假设无事故
        check1 = no_major_accident
        result["checks"].append({
            "description": "近3年无重大安全事故",
            "value": "无" if no_major_accident else "有",
            "passed": check1,
            "required": "必须"
        })
        if not check1:
            result["passed"] = False
            result["suggestions"].append("近3年不能有重大安全事故")
        
        # 检查2：必须是省级专精特新企业
        provincial_specialized = data.get("provincial_specialized", False)
        check2 = provincial_specialized
        result["checks"].append({
            "description": "已获得省级专精特新企业认定",
            "value": "是" if provincial_specialized else "否",
            "passed": check2,
            "required": "必须"
        })
        if not check2:
            result["passed"] = False
            result["suggestions"].append("需要先获得省级专精特新企业认定")
        
        return result
    
    def _generate_assessment_report(self, assessment: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """生成评估报告"""
        report = "【专精特新小巨人申报资格评估报告】\n\n"
        
        # 总体结论
        overall_qualified = assessment.get("overall_qualified", False)
        if overall_qualified:
            report += "✅ 总体评估：符合申报基本条件\n\n"
        else:
            report += "❌ 总体评估：暂不符合申报条件\n\n"
        
        # 各项指标评估结果
        report += "【各项指标评估】\n"
        
        indicators = assessment.get("indicators", {})
        for category, result in indicators.items():
            if result.get("passed", False):
                report += f"✅ {category}：通过\n"
            else:
                report += f"❌ {category}：不通过\n"
                
                # 显示具体检查项
                checks = result.get("checks", [])
                for check in checks:
                    if not check.get("passed", True):
                        report += f"   - {check.get('description', '')}："
                        report += f"当前{check.get('value', '')}，要求{check.get('required', '')}\n"
        
        # 关键指标数据
        report += "\n【关键指标数据】\n"
        
        key_metrics = [
            ("main_revenue_ratio", "主营业务占比"),
            ("revenue_growth_2y_avg", "近2年主营业务增长率"),
            ("rd_expense_ratio", "研发费用占比"),
            ("asset_liability_ratio", "资产负债率"),
            ("market_share", "市场占有率"),
            ("patent_count", "专利数量"),
            ("company_age", "企业年龄")
        ]
        
        for metric_key, metric_name in key_metrics:
            if metric_key in metrics:
                value = metrics[metric_key]
                if isinstance(value, float):
                    report += f"{metric_name}：{value:.1f}%\n"
                else:
                    report += f"{metric_name}：{value}\n"
        
        # 改进建议
        suggestions = assessment.get("suggestions", [])
        if suggestions:
            report += "\n【改进建议】\n"
            for i, suggestion in enumerate(suggestions[:5], 1):
                report += f"{i}. {suggestion}\n"
            
            if len(suggestions) > 5:
                report += f"...等{len(suggestions)}条建议\n"
        
        # 申报成功率估算
        success_rate = self._estimate_success_rate(assessment, metrics)
        report += f"\n【申报成功率估算】\n"
        report += f"基于当前数据，申报成功率约为：{success_rate}%\n"
        
        if success_rate < 60:
            report += "建议：完善相关条件后再申报\n"
        elif success_rate < 80:
            report += "建议：有一定机会，建议补充材料\n"
        else:
            report += "建议：条件较好，建议尽快申报\n"
        
        return report
    
    def _estimate_success_rate(self, assessment: Dict[str, Any], metrics: Dict[str, Any]) -> float:
        """估算申报成功率"""
        indicators = assessment.get("indicators", {})
        
        # 计算通过率
        passed_count = 0
        total_count = 0
        
        for category, result in indicators.items():
            total_count += 1
            if result.get("passed", False):
                passed_count += 1
        
        if total_count == 0:
            return 0.0
        
        # 基础通过率
        base_rate = (passed_count / total_count) * 100
        
        # 根据关键指标调整
        adjustments = 0
        
        # 主营业务占比调整
        main_revenue_ratio = metrics.get("main_revenue_ratio", 0)
        if main_revenue_ratio >= 80:
            adjustments += 5
        elif main_revenue_ratio >= 70:
            adjustments += 0
        else:
            adjustments -= 10
        
        # 研发费用占比调整
        rd_expense_ratio = metrics.get("rd_expense_ratio", 0)
        if rd_expense_ratio >= 8:
            adjustments += 5
        elif rd_expense_ratio >= 5:
            adjustments += 2
        elif rd_expense_ratio < 3:
            adjustments -= 5
        
        # 市场占有率调整
        market_share = metrics.get("market_share", 0)
        if market_share >= 20:
            adjustments += 5
        elif market_share >= 10:
            adjustments += 0
        else:
            adjustments -= 10
        
        # 专利数量调整
        patent_count = metrics.get("patent_count", 0)
        if patent_count >= 10:
            adjustments += 5
        elif patent_count >= 5:
            adjustments += 3
        elif patent_count < 2:
            adjustments -= 5
        
        # 计算最终成功率
        success_rate = base_rate + adjustments
        
        # 限制在0-100范围内
        success_rate = max(0, min(100, success_rate))
        
        return round(success_rate, 1)
