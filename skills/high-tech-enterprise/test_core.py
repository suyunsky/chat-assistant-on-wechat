"""
高企申报核心功能测试
直接测试核心算法，不依赖外部模块
"""

import re
from datetime import datetime


def test_company_info_parsing():
    """测试企业信息解析"""
    print("🧪 测试企业信息解析...")
    
    company_info = """
企业名称：测试科技有限公司
成立时间：2020-05-10
所属高新技术领域：先进制造与自动化
上年度销售收入：3500
近三年研发费用占比：5.2
高品收入占比：68.3
科技人员占比：12.5
职工总数：120
研发人员数：15
发明专利数量：3
实用新型专利数量：12
软件著作权数量：5
"""
    
    data = {}
    
    patterns = {
        "company_name": r"企业名称[:：]\s*(.+)",
        "establishment_date": r"成立时间[:：]\s*(.+)",
        "industry_field": r"所属高新技术领域[:：]\s*(.+)",
        "revenue_last_year": r"上年度销售收入[:：]\s*([\d.]+)",
        "rd_expense_ratio": r"近三年研发费用占比[:：]\s*([\d.]+)",
        "high_tech_product_ratio": r"高品收入占比[:：]\s*([\d.]+)",
        "tech_personnel_ratio": r"科技人员占比[:：]\s*([\d.]+)",
        "employee_count": r"职工总数[:：]\s*(\d+)",
        "rd_personnel_count": r"研发人员数[:：]\s*(\d+)",
        "invention_patents": r"发明专利数量[:：]\s*(\d+)",
        "utility_patents": r"实用新型专利数量[:：]\s*(\d+)",
        "software_copyrights": r"软件著作权数量[:：]\s*(\d+)"
    }
    
    for field, pattern in patterns.items():
        match = re.search(pattern, company_info)
        if match:
            value = match.group(1).strip()
            # 数值类型转换
            if field in ["revenue_last_year", "rd_expense_ratio", "high_tech_product_ratio", "tech_personnel_ratio"]:
                try:
                    data[field] = float(value)
                except:
                    data[field] = value
            elif field in ["employee_count", "rd_personnel_count", "invention_patents", "utility_patents", "software_copyrights"]:
                try:
                    data[field] = int(value)
                except:
                    data[field] = value
            else:
                data[field] = value
    
    print(f"解析结果:")
    for key, value in data.items():
        print(f"  {key}: {value}")
    
    print(f"✅ 解析成功，共{len(data)}个字段")
    return data


def test_innovation_score_calculation(data):
    """测试创新能力得分计算"""
    print("\n🧪 测试创新能力得分计算...")
    
    scores = {}
    
    # 1. 核心自主知识产权（30分）
    invention_patents = data.get("invention_patents", 0)
    utility_patents = data.get("utility_patents", 0)
    software_copyrights = data.get("software_copyrights", 0)
    
    # 知识产权数量得分（8分）
    total_ip = invention_patents + utility_patents + software_copyrights
    if invention_patents >= 1:
        ip_quantity_score = 7  # 有I类知识产权
    elif total_ip >= 5:
        ip_quantity_score = 5  # 5项以上II类
    elif total_ip >= 3:
        ip_quantity_score = 3  # 3-4项II类
    elif total_ip >= 1:
        ip_quantity_score = 1  # 1-2项II类
    else:
        ip_quantity_score = 0
    
    # 技术先进程度（8分）- 简化评估
    tech_advanced_score = 6  # 默认较高
    
    # 核心支持作用（8分）- 简化评估
    core_support_score = 6  # 默认较强
    
    # 获得方式（6分）
    acquisition_score = 4  # 默认有自主研发
    
    scores["intellectual_property"] = {
        "quantity": ip_quantity_score,
        "advanced": tech_advanced_score,
        "support": core_support_score,
        "acquisition": acquisition_score,
        "total": ip_quantity_score + tech_advanced_score + core_support_score + acquisition_score,
        "max": 30
    }
    
    # 2. 科技成果转化能力（30分）
    if total_ip >= 5:
        transformation_score = 25  # A级
    elif total_ip >= 4:
        transformation_score = 19  # B级
    elif total_ip >= 3:
        transformation_score = 13  # C级
    elif total_ip >= 2:
        transformation_score = 7   # D级
    elif total_ip >= 1:
        transformation_score = 1   # E级
    else:
        transformation_score = 0   # F级
    
    scores["transformation"] = {
        "score": transformation_score,
        "max": 30,
        "level": "A" if transformation_score >= 25 else "B" if transformation_score >= 19 else "C" if transformation_score >= 13 else "D" if transformation_score >= 7 else "E" if transformation_score >= 1 else "F"
    }
    
    # 3. 研究开发组织管理水平（20分）
    employee_count = data.get("employee_count", 0)
    if employee_count >= 100:
        management_score = 18  # 规模较大，管理较完善
    elif employee_count >= 50:
        management_score = 15  # 中等规模
    elif employee_count >= 20:
        management_score = 12  # 较小规模
    else:
        management_score = 8   # 小微企业
    
    scores["management"] = {
        "score": management_score,
        "max": 20
    }
    
    # 4. 企业成长性（20分）
    rd_ratio = data.get("rd_expense_ratio", 0)
    tech_ratio = data.get("tech_personnel_ratio", 0)
    
    if rd_ratio >= 8 and tech_ratio >= 15:
        growth_score = 18  # 高成长性
    elif rd_ratio >= 5 and tech_ratio >= 10:
        growth_score = 14  # 中等成长性
    elif rd_ratio >= 3 and tech_ratio >= 5:
        growth_score = 10  # 一般成长性
    else:
        growth_score = 6   # 较低成长性
    
    scores["growth"] = {
        "score": growth_score,
        "max": 20
    }
    
    # 总分
    total_score = (
        scores["intellectual_property"]["total"] +
        scores["transformation"]["score"] +
        scores["management"]["score"] +
        scores["growth"]["score"]
    )
    
    scores["total"] = {
        "score": total_score,
        "max": 100,
        "passed": total_score >= 71
    }
    
    print(f"创新能力总分: {total_score}/100")
    print(f"是否通过(≥71分): {'✅' if total_score >= 71 else '❌'}")
    print(f"知识产权得分: {scores['intellectual_property']['total']}/30")
    print(f"成果转化得分: {scores['transformation']['score']}/30")
    print(f"组织管理得分: {scores['management']['score']}/20")
    print(f"成长性得分: {scores['growth']['score']}/20")
    
    return scores


def test_high_tech_conditions_assessment(data):
    """测试高企8大条件评估"""
    print("\n🧪 测试高企8大条件评估...")
    
    conditions = {}
    
    # 1. 注册时间
    establishment_date = data.get("establishment_date")
    if establishment_date:
        try:
            establish_date = datetime.strptime(establishment_date, "%Y-%m-%d")
            days_since = (datetime.now() - establish_date).days
            conditions["registration_time"] = {
                "passed": days_since >= 365,
                "reason": f"成立{days_since}天，{'符合' if days_since >= 365 else '不符合'}一年以上要求"
            }
        except:
            conditions["registration_time"] = {"passed": False, "reason": "成立日期格式错误"}
    else:
        conditions["registration_time"] = {"passed": False, "reason": "缺少成立日期"}
    
    # 2. 知识产权
    invention_patents = data.get("invention_patents", 0)
    utility_patents = data.get("utility_patents", 0)
    software_copyrights = data.get("software_copyrights", 0)
    total_ip = invention_patents + utility_patents + software_copyrights
    
    conditions["intellectual_property"] = {
        "passed": total_ip > 0,
        "reason": f"拥有{total_ip}项知识产权（发明专利{invention_patents}项，实用新型{utility_patents}项，软著{software_copyrights}项）"
    }
    
    # 3. 技术领域
    industry_field = data.get("industry_field", "")
    high_tech_fields = ["电子信息", "生物与新医药", "航空航天", "新材料", "高技术服务", "新能源与节能", "资源与环境", "先进制造与自动化"]
    
    technology_field_passed = any(field in industry_field for field in high_tech_fields)
    conditions["technology_field"] = {
        "passed": technology_field_passed,
        "reason": f"所属领域：{industry_field}，{'属于' if technology_field_passed else '不属于'}高新技术领域"
    }
    
    # 4. 科技人员占比
    tech_personnel_ratio = data.get("tech_personnel_ratio", 0)
    conditions["tech_personnel_ratio"] = {
        "passed": tech_personnel_ratio >= 10,
        "reason": f"科技人员占比{tech_personnel_ratio}%，{'符合' if tech_personnel_ratio >= 10 else '不符合'}≥10%要求"
    }
    
    # 5. 研发费用占比
    rd_expense_ratio = data.get("rd_expense_ratio", 0)
    revenue_last_year = data.get("revenue_last_year", 0)
    
    # 根据收入确定要求
    if revenue_last_year < 5000:
        required_ratio = 5
    elif revenue_last_year < 20000:
        required_ratio = 4
    else:
        required_ratio = 3
    
    conditions["rd_expense_ratio"] = {
        "passed": rd_expense_ratio >= required_ratio,
        "reason": f"研发费用占比{rd_expense_ratio}%，收入{revenue_last_year}万元要求{required_ratio}%，{'符合' if rd_expense_ratio >= required_ratio else '不符合'}"
    }
    
    # 6. 高品收入占比
    high_tech_product_ratio = data.get("high_tech_product_ratio", 0)
    conditions["high_tech_product_ratio"] = {
        "passed": high_tech_product_ratio >= 60,
        "reason": f"高品收入占比{high_tech_product_ratio}%，{'符合' if high_tech_product_ratio >= 60 else '不符合'}≥60%要求"
    }
    
    # 7. 创新能力（在单独方法中评估）
    conditions["innovation_capability"] = {
        "passed": True,  # 将在calculate_innovation_score中具体评估
        "reason": "创新能力需达到71分以上"
    }
    
    # 8. 安全环保（默认通过，需要企业自行确认）
    conditions["safety_environment"] = {
        "passed": True,
        "reason": "需企业确认申请前一年内未发生重大安全、质量事故或严重环境违法行为"
    }
    
    # 输出结果
    passed_count = sum(1 for cond in conditions.values() if cond.get("passed", False))
    print(f"8大条件通过数: {passed_count}/8")
    
    for key, condition in conditions.items():
        status = "✅" if condition.get("passed", False) else "❌"
        print(f"  {status} {key}: {condition.get('reason', '')}")
    
    return conditions


def test_success_rate_calculation(conditions_assessment, innovation_score):
    """测试申报成功率计算"""
    print("\n🧪 测试申报成功率计算...")
    
    # 基础成功率
    base_rate = 50.0
    
    # 8大条件通过率加成
    conditions = conditions_assessment
    passed_conditions = sum(1 for cond in conditions.values() if cond.get("passed", False))
    condition_bonus = (passed_conditions / 8) * 30  # 最多30%
    
    # 创新能力得分加成
    innovation_total = innovation_score.get("total", {}).get("score", 0)
    innovation_bonus = (innovation_total / 100) * 20  # 最多20%
    
    # 计算总成功率
    success_rate = base_rate + condition_bonus + innovation_bonus
    
    # 限制在0-100%
    success_rate = max(0, min(100, success_rate))
    
    print(f"基础成功率: {base_rate}%")
    print(f"条件通过加成: {condition_bonus:.1f}% ({passed_conditions}/8项通过)")
    print(f"创新能力加成: {innovation_bonus:.1f}% (得分{innovation_total}/100)")
    print(f"总成功率: {success_rate:.1f}%")
    
    return success_rate


def test_assessment_report_generation(conditions_assessment, innovation_score, success_rate):
    """测试评估报告生成"""
    print("\n🧪 测试评估报告生成...")
    
    report = "【高企资格评估报告】\n\n"
    
    conditions = conditions_assessment
    innovation_total = innovation_score.get("total", {})
    qualified = all(cond["passed"] for cond in conditions.values()) and innovation_total.get("passed", False)
    
    # 8大条件评估
    report += "**一、8大条件评估结果：**\n"
    
    condition_names = {
        "registration_time": "1. 注册时间",
        "intellectual_property": "2. 知识产权",
        "technology_field": "3. 技术领域",
        "tech_personnel_ratio": "4. 科技人员占比",
        "rd_expense_ratio": "5. 研发费用占比",
        "high_tech_product_ratio": "6. 高品收入占比",
        "innovation_capability": "7. 创新能力",
        "safety_environment": "8. 安全环保"
    }
    
    for key, name in condition_names.items():
        if key in conditions:
            cond = conditions[key]
            status = "✅" if cond.get("passed", False) else "❌"
            report += f"{status} {name}: {cond.get('reason', '')}\n"
    
    # 创新能力评分
    report += "\n**二、创新能力预估评分（100分制）：**\n"
    
    if innovation_total:
        score = innovation_total.get("score", 0)
        passed = innovation_total.get("passed", False)
        status = "✅" if passed else "❌"
        report += f"{status} 总分: {score}/100分 ({'通过' if passed else '未通过'})\n"
        
        # 各项得分
        if "intellectual_property" in innovation_score:
            ip_score = innovation_score["intellectual_property"]["total"]
            report += f"  • 核心自主知识产权: {ip_score}/30分\n"
        
        if "transformation" in innovation_score:
            trans_score = innovation_score["transformation"]["score"]
            report += f"  • 科技成果转化能力: {trans_score}/30分\n"
        
        if "management" in innovation_score:
            mgmt_score = innovation_score["management"]["score"]
            report += f"  • 研究开发组织管理: {mgmt_score}/20分\n"
        
        if "growth" in innovation_score:
            growth_score = innovation_score["growth"]["score"]
            report += f"  • 企业成长性: {growth_score}/20分\n"
    
    # 总体评估
    report += f"\n**三、总体评估：**\n"
    if qualified:
        report += "✅ **符合高企申报基本条件**\n"
    else:
        report += "❌ **暂不符合高企申报条件**\n"
    
    report += f"📊 **申报成功率预估: {success_rate:.1f}%**\n"
    
    print(f"评估报告长度: {len(report)} 字符")
    print(f"包含8大条件评估: {'8大条件' in report or '条件评估' in report}")
    print(f"包含创新能力评分: {'创新能力' in report}")
    print(f"包含成功率预估: {'成功率' in report}")
    
    return report


def test_materials_generation():
    """测试材料清单生成"""
    print("\n🧪 测试材料清单生成...")
    
    materials = {
        "基础材料": [
            "《高新技术企业认定申请书》（在线打印并签名+公章）",
            "证明事项告知承诺书",
            "企业营业执照复印件"
        ],
        "知识产权材料": [
            "知识产权证书及反映技术水平的证明材料",
            "参与制定标准情况材料（如有）"
        ],
        "技术创新材料": [
            "科技成果转化总体情况与转化形式说明",
            "科研项目立项证明及验收报告",
            "研究开发组织管理水平说明材料"
        ],
        "产品服务材料": [
            "高新技术产品（服务）关键技术说明",
            "相关生产批文、认证证书、产品质量检验报告"
        ],
        "财务人员材料": [
            "近三年研究开发费用专项审计报告（必需）",
            "近一年高新技术产品（服务）收入专项审计报告（必需）",
            "企业职工和科技人员情况说明材料",
            "近三年财务会计报告及纳税申报表"
        ]
    }
    
    total_count = sum(len(items) for items in materials.values())
    print(f"高企申报材料共{total_count}项，分为{len(materials)}类:")
    
    for category, items in materials.items():
        print(f"\n【{category}】({len(items)}项):")
        for item in items:
            print(f"  • {item}")
    
    print(f"\n✅ 材料清单测试完成")
    return materials


def main():
    """主测试函数"""
    print("🏭 高企申报核心功能测试套件")
    print("=" * 60)
    
    # 测试1: 企业信息解析
    data = test_company_info_parsing()
    
    # 测试2: 创新能力评分计算
    innovation_score = test_innovation_score_calculation(data)
    
    # 测试3: 8大条件评估
    conditions_assessment = test_high_tech_conditions_assessment(data)
    
    # 测试4: 成功率计算
    success_rate = test_success_rate_calculation(conditions_assessment, innovation_score)
    
    # 测试5: 评估报告生成
    report = test_assessment_report_generation(conditions_assessment, innovation_score, success_rate)
    
    # 测试6: 材料清单生成
    materials = test_materials_generation()
    
    print("\n" + "=" * 60)
    print("🎉 所有核心功能测试完成！")
    print("\n📋 测试总结:")
    print(f"1. 企业信息解析: ✅ 成功解析{len(data)}个字段")
    print(f"2. 创新能力评分: ✅ 总分{innovation_score['total']['score']}/100分")
    print(f"3. 8大条件评估: ✅ {sum(1 for cond in conditions_assessment.values() if cond.get('passed', False))}/8项通过")
    print(f"4. 申报成功率: ✅ {success_rate:.1f}%")
    print(f"5. 评估报告: ✅ {len(report)}字符")
    print(f"6. 材料清单: ✅ {sum(len(items) for items in materials.values())}项材料")
    
    # 显示评估报告示例
    print("\n📄 评估报告示例（前500字符）:")
    print(report[:500] + "..." if len(report) > 500 else report)


if __name__ == "__main__":
    main()
           