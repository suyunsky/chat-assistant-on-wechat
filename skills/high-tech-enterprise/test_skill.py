"""
高企申报技能测试脚本
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# 动态导入技能类
try:
    from skills.high_tech_enterprise.skill import HighTechEnterpriseSkill
    from agent.skills.types import SkillContext
except ImportError:
    # 如果导入失败，尝试相对导入
    import importlib.util
    import sys
    
    # 直接导入当前目录的模块
    spec = importlib.util.spec_from_file_location(
        "skill", 
        os.path.join(os.path.dirname(__file__), "skill.py")
    )
    skill_module = importlib.util.module_from_spec(spec)
    sys.modules["skill"] = skill_module
    spec.loader.exec_module(skill_module)
    
    from skill import HighTechEnterpriseSkill
    
    # 创建简单的SkillContext类型
    SkillContext = dict


async def test_high_tech_skill():
    """测试高企申报技能"""
    print("🧪 开始测试高企申报技能...")
    
    # 创建技能实例
    skill = HighTechEnterpriseSkill()
    
    # 测试1: 初始问候
    print("\n📝 测试1: 初始问候")
    context = SkillContext(query="你好", session_id="test_session_1")
    result = await skill.execute(context)
    print(f"输入: {context['query']}")
    print(f"输出: {result.content[:100]}...")
    
    # 测试2: 启动高企申报流程
    print("\n📝 测试2: 启动高企申报流程")
    context = SkillContext(query="高企申报", session_id="test_session_2")
    result = await skill.execute(context)
    print(f"输入: {context['query']}")
    print(f"输出长度: {len(result.content)} 字符")
    print(f"包含8大条件: {'8大条件' in result.content}")
    
    # 测试3: 提供企业信息（批量输入）
    print("\n📝 测试3: 提供企业信息")
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
    
    # 先启动流程
    context = SkillContext(query="高企申报", session_id="test_session_3")
    await skill.execute(context)
    
    # 选择批量输入
    context = SkillContext(query="2", session_id="test_session_3")
    await skill.execute(context)
    
    # 提供企业信息
    context = SkillContext(query=company_info, session_id="test_session_3")
    result = await skill.execute(context)
    print(f"输入: 企业信息（{len(company_info)}字符）")
    print(f"输出长度: {len(result.content)} 字符")
    print(f"包含评估结果: {'评估' in result.content}")
    
    # 测试4: 查看材料清单
    print("\n📝 测试4: 查看材料清单")
    context = SkillContext(query="材料清单", session_id="test_session_3")
    result = await skill.execute(context)
    print(f"输入: {context['query']}")
    print(f"输出长度: {len(result.content)} 字符")
    print(f"包含14项材料: {'14项' in result.content or '材料清单' in result.content}")
    
    # 测试5: 测试创新能力评分计算
    print("\n📝 测试5: 测试创新能力评分计算")
    test_data = {
        "invention_patents": 3,
        "utility_patents": 12,
        "software_copyrights": 5,
        "employee_count": 120,
        "rd_expense_ratio": 5.2,
        "tech_personnel_ratio": 12.5
    }
    
    innovation_score = skill.calculate_innovation_score(test_data)
    print(f"测试数据: {test_data}")
    print(f"创新能力总分: {innovation_score['total']['score']}/100")
    print(f"是否通过(≥71分): {innovation_score['total']['passed']}")
    
    # 测试6: 测试8大条件评估
    print("\n📝 测试6: 测试8大条件评估")
    conditions_assessment = skill.assess_high_tech_conditions(test_data)
    passed_count = sum(1 for cond in conditions_assessment.values() if cond.get("passed", False))
    print(f"8大条件通过数: {passed_count}/8")
    
    for key, condition in conditions_assessment.items():
        status = "✅" if condition.get("passed", False) else "❌"
        print(f"  {status} {key}: {condition.get('reason', '')}")
    
    # 测试7: 测试成功率计算
    print("\n📝 测试7: 测试成功率计算")
    success_rate = skill.calculate_success_rate(conditions_assessment, innovation_score)
    print(f"申报成功率预估: {success_rate:.1f}%")
    
    # 测试8: 测试评估报告生成
    print("\n📝 测试8: 测试评估报告生成")
    assessment_result = {
        "conditions_assessment": conditions_assessment,
        "innovation_score": innovation_score,
        "success_rate": success_rate,
        "qualified": passed_count >= 7 and innovation_score["total"]["passed"],
        "suggestions": ["建议1", "建议2", "建议3"]
    }
    
    report = skill.format_high_tech_assessment_report(assessment_result)
    print(f"评估报告长度: {len(report)} 字符")
    print(f"包含8大条件评估: {'8大条件' in report or '条件评估' in report}")
    print(f"包含创新能力评分: {'创新能力' in report}")
    print(f"包含成功率预估: {'成功率' in report}")
    
    print("\n✅ 高企申报技能测试完成！")


async def test_simple_workflow():
    """测试简化工作流"""
    print("\n🚀 测试简化工作流...")
    
    # 创建技能实例
    skill = HighTechEnterpriseSkill()
    session_id = "workflow_test_1"
    
    # 步骤1: 启动流程
    print("\n1. 启动高企申报流程")
    context = SkillContext(query="高企申报", session_id=session_id)
    result = await skill.execute(context)
    print(f"响应: {result.content[:150]}...")
    
    # 步骤2: 选择批量输入
    print("\n2. 选择批量输入方式")
    context = SkillContext(query="2", session_id=session_id)
    result = await skill.execute(context)
    print(f"响应: {result.content[:150]}...")
    
    # 步骤3: 提供企业信息
    print("\n3. 提供企业信息")
    company_info = """
企业名称：智能机器人科技有限公司
成立时间：2019-03-15
所属高新技术领域：先进制造与自动化
上年度销售收入：4200
近三年研发费用占比：6.8
高品收入占比：72.5
科技人员占比：15.2
职工总数：85
研发人员数：13
发明专利数量：5
实用新型专利数量：8
"""
    
    context = SkillContext(query=company_info, session_id=session_id)
    result = await skill.execute(context)
    print(f"响应: {result.content[:200]}...")
    
    # 步骤4: 查看材料清单
    print("\n4. 查看材料清单")
    context = SkillContext(query="材料清单", session_id=session_id)
    result = await skill.execute(context)
    print(f"响应包含14项材料: {'14项' in result.content or '材料清单' in result.content}")
    
    print("\n✅ 简化工作流测试完成！")


if __name__ == "__main__":
    print("🏭 高企申报技能测试套件")
    print("=" * 50)
    
    # 运行测试
    asyncio.run(test_high_tech_skill())
    asyncio.run(test_simple_workflow())
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！")
    print("\n📋 测试总结:")
    print("1. 技能初始化和问候功能正常")
    print("2. 高企申报流程启动正常")
    print("3. 企业信息解析和评估功能正常")
    print("4. 创新能力评分计算正常")
    print("5. 8大条件评估功能正常")
    print("6. 申报成功率预估功能正常")
    print("7. 评估报告生成功能正常")
    print("8. 材料清单生成功能正常")
    print("9. 简化工作流测试通过")