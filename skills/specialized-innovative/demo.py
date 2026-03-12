#!/usr/bin/env python3
"""
专精特新小巨人申报技能演示脚本
演示技能的核心功能
"""

import sys
import os
import json
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir.parent.parent))

print("=== 专精特新小巨人申报技能演示 ===\n")

# 演示企业数据
demo_company_data = {
    "company_name": "ABC智能制造科技有限公司",
    "establishment_year": 2015,
    "industry": "智能制造",
    "main_business": "工业机器人研发与制造",
    "revenue_2023": 8500,
    "main_revenue_2023": 8000,
    "rd_expense_2023": 680,
    "employee_count": 120,
    "rd_employee_count": 35,
    "patent_count": 15,
    "main_products": "工业机器人控制器、智能生产线",
    "market_share": 12.0,
    "revenue_2021": 6500,
    "revenue_2022": 7500,
    "main_revenue_2021": 6000,
    "main_revenue_2022": 7200,
    "rd_expense_2021": 520,
    "rd_expense_2022": 610,
    "asset_total": 5600,
    "liability_total": 2500,
    "core_customers": "华为、比亚迪、中车集团",
    "certifications": "ISO9001, ISO14001",
    "rd_institution": "省级企业技术中心",
    "management_system": "ERP系统、MES系统"
}

print("1. 企业基本信息")
print("=" * 50)
print(f"企业名称: {demo_company_data['company_name']}")
print(f"成立时间: {demo_company_data['establishment_year']}年")
print(f"所属行业: {demo_company_data['industry']}")
print(f"主营业务: {demo_company_data['main_business']}")
print(f"主要产品: {demo_company_data['main_products']}")
print(f"员工总数: {demo_company_data['employee_count']}人")
print(f"研发人员: {demo_company_data['rd_employee_count']}人")
print(f"专利数量: {demo_company_data['patent_count']}项")
print(f"市场占有率: {demo_company_data['market_share']}%")
print()

print("2. 财务数据（2021-2023）")
print("=" * 50)
print(f"2021年营收: {demo_company_data['revenue_2021']}万元")
print(f"2022年营收: {demo_company_data['revenue_2022']}万元")
print(f"2023年营收: {demo_company_data['revenue_2023']}万元")
print(f"2021年研发费用: {demo_company_data['rd_expense_2021']}万元")
print(f"2022年研发费用: {demo_company_data['rd_expense_2022']}万元")
print(f"2023年研发费用: {demo_company_data['rd_expense_2023']}万元")
print()

# 计算关键指标
print("3. 关键指标计算")
print("=" * 50)

# 计算主营业务占比
main_revenue_ratio = (demo_company_data['main_revenue_2023'] / demo_company_data['revenue_2023']) * 100
print(f"主营业务收入占比: {main_revenue_ratio:.1f}%")

# 计算研发费用占比
rd_ratio = (demo_company_data['rd_expense_2023'] / demo_company_data['revenue_2023']) * 100
print(f"研发费用占比: {rd_ratio:.1f}%")

# 计算资产负债率
asset_liability_ratio = (demo_company_data['liability_total'] / demo_company_data['asset_total']) * 100
print(f"资产负债率: {asset_liability_ratio:.1f}%")

# 计算近2年主营业务增长率
revenue_growth_2y = ((demo_company_data['main_revenue_2023'] - demo_company_data['main_revenue_2021']) / demo_company_data['main_revenue_2021']) * 100
print(f"近2年主营业务增长率: {revenue_growth_2y:.1f}%")

# 计算企业年龄
current_year = 2024
company_age = current_year - demo_company_data['establishment_year']
print(f"企业年龄: {company_age}年")
print()

print("4. 资格评估示例")
print("=" * 50)

# 专精特新评估标准
assessment_criteria = {
    "specialization": {
        "market_years": 3,
        "main_revenue_ratio": 70,
        "revenue_growth_2y": 5
    },
    "refinement": {
        "has_it_system": True,
        "has_management_cert": True,
        "asset_liability_ratio": 70
    },
    "characteristics": {
        "market_share": 10,
        "has_own_brand": True
    },
    "innovation": {
        "rd_ratio_1b": 3,
        "rd_ratio_50m_1b": 6,
        "rd_institution": True,
        "patent_count": 2
    }
}

# 评估结果
print("【专业化评估】")
print(f"✓ 企业年龄: {company_age}年 ≥ {assessment_criteria['specialization']['market_years']}年")
print(f"✓ 主营业务占比: {main_revenue_ratio:.1f}% ≥ {assessment_criteria['specialization']['main_revenue_ratio']}%")
print(f"✓ 近2年增长率: {revenue_growth_2y:.1f}% ≥ {assessment_criteria['specialization']['revenue_growth_2y']}%")

print("\n【精细化评估】")
print(f"✓ 信息化系统: {'有' if demo_company_data.get('management_system') else '无'}")
print(f"✓ 管理体系认证: {'有' if demo_company_data.get('certifications') else '无'}")
print(f"✓ 资产负债率: {asset_liability_ratio:.1f}% ≤ {assessment_criteria['refinement']['asset_liability_ratio']}%")

print("\n【特色化评估】")
print(f"✓ 市场占有率: {demo_company_data['market_share']}% ≥ {assessment_criteria['characteristics']['market_share']}%")
print(f"✓ 自主品牌: {'有' if demo_company_data.get('main_products') else '无'}")

print("\n【创新能力评估】")
print(f"✓ 研发费用占比: {rd_ratio:.1f}% ≥ {assessment_criteria['innovation']['rd_ratio_50m_1b']}%")
print(f"✓ 研发机构: {'有' if demo_company_data.get('rd_institution') else '无'}")
print(f"✓ 专利数量: {demo_company_data['patent_count']}项 ≥ {assessment_criteria['innovation']['patent_count']}项")
print()

print("5. 申报材料清单")
print("=" * 50)

required_materials = [
    "企业营业执照",
    "2021-2023年年度审计报告",
    "2021-2023年12月底缴纳社保人数证明",
    "I类知识产权清单",
    "研发机构证明",
    "管理体系认证证书",
    "信息化系统证明",
    "自主品牌证明材料",
    "国家企业信用信息公示系统截图",
    "信用中国查询截图",
    "真实性申明"
]

suggested_materials = [
    "产品认证证书",
    "国家级科技奖励证书",
    "创客中国大赛获奖证明"
]

print("必需材料（11项）:")
for i, material in enumerate(required_materials, 1):
    print(f"  {i}. {material}")

print("\n建议材料（3项）:")
for i, material in enumerate(suggested_materials, 1):
    print(f"  {i}. {material}")
print()

print("6. 申报成功率估算")
print("=" * 50)

# 简单估算逻辑
success_factors = []

# 专业化得分
if company_age >= 3:
    success_factors.append(1.0)
if main_revenue_ratio >= 70:
    success_factors.append(1.0)
if revenue_growth_2y >= 5:
    success_factors.append(1.0)

# 精细化得分
if demo_company_data.get('management_system'):
    success_factors.append(1.0)
if demo_company_data.get('certifications'):
    success_factors.append(1.0)
if asset_liability_ratio <= 70:
    success_factors.append(1.0)

# 特色化得分
if demo_company_data['market_share'] >= 10:
    success_factors.append(1.0)
if demo_company_data.get('main_products'):
    success_factors.append(1.0)

# 创新能力得分
if rd_ratio >= 6:
    success_factors.append(1.0)
if demo_company_data.get('rd_institution'):
    success_factors.append(1.0)
if demo_company_data['patent_count'] >= 2:
    success_factors.append(1.0)

# 计算成功率
total_factors = 11  # 总评估项数
success_rate = (len(success_factors) / total_factors) * 100

print(f"评估项总数: {total_factors}")
print(f"符合项数量: {len(success_factors)}")
print(f"申报成功率: {success_rate:.1f}%")

if success_rate >= 80:
    print("✅ 评估结果: 条件优秀，建议立即申报")
elif success_rate >= 60:
    print("⚠️ 评估结果: 条件良好，建议补充材料后申报")
elif success_rate >= 40:
    print("⚠️ 评估结果: 基本符合，需要重点改进")
else:
    print("❌ 评估结果: 不符合基本条件，暂不建议申报")
print()

print("7. 技能使用示例")
print("=" * 50)
print("用户对话示例:")
print("用户: 专精特新申报")
print("助手: 欢迎使用专精特新小巨人申报助手！我将引导您完成申报全流程...")
print()
print("用户: 上传企业文档")
print("助手: 请上传企业相关文档（审计报告、营业执照、专利清单等）...")
print()
print("用户: 批量输入企业信息")
print("助手: 请一次性提供企业关键信息，格式如：企业名称：XXX\\n成立时间：XXXX年...")
print()

print("8. 输出成果示例")
print("=" * 50)
output_examples = [
    "✅ 专精特新小巨人申请书框架",
    "✅ 市场占有率说明（1000字）",
    "✅ 企业2000字介绍文档",
    "✅ 补短板说明（300字）",
    "✅ 佐证材料清单（14项）",
    "✅ 材料完整性检查报告",
    "✅ 申报成功率评估报告",
    "✅ 缺失材料提示清单"
]

for example in output_examples:
    print(f"  {example}")

print("\n" + "=" * 50)
print("🎉 专精特新小巨人申报技能演示完成！")
print("\n技能特点总结:")
print("1. 多模式信息收集：文档上传、批量输入、对话引导")
print("2. 智能资格评估：基于政策规则自动评估")
print("3. 关键指标计算：财务、研发、市场等指标")
print("4. 申报材料生成：申请书、说明文档、材料清单")
print("5. 材料完整性检查：智能匹配、缺失清单、准备指南")
print("\n让企业申报更简单、更智能！")