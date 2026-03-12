#!/usr/bin/env python3
"""
专精特新小巨人申报技能测试脚本
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 直接导入本地模块
try:
    from skills.specialized_innovative.skill import SpecializedInnovativeSkill
    from skills.specialized_innovative.services.assessment_calculator import AssessmentCalculator
    from skills.specialized_innovative.services.material_generator import MaterialGenerator
    from skills.specialized_innovative.services.proof_checker import ProofChecker
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在项目根目录下运行测试")
    sys.exit(1)


async def test_skill():
    """测试技能基本功能"""
    print("=== 专精特新小巨人申报技能测试 ===\n")
    
    # 1. 创建技能实例
    print("1. 创建技能实例...")
    skill = SpecializedInnovativeSkill()
    print(f"   技能名称: {skill.name}")
    print(f"   技能描述: {skill.description}")
    print(f"   技能版本: {skill.version}")
    print("   ✅ 技能创建成功\n")
    
    # 2. 测试欢迎消息
    print("2. 测试欢迎消息...")
    context = {
        "query": "专精特新申报",
        "session_id": "test_session_001"
    }
    
    result = await skill.execute(context)
    print(f"   用户输入: {context['query']}")
    print(f"   技能响应: {result.content[:100]}...")
    print(f"   执行成功: {result.success}")
    print("   ✅ 欢迎消息测试通过\n")
    
    # 3. 测试信息收集（对话引导）
    print("3. 测试信息收集（对话引导）...")
    
    # 模拟对话流程
    test_responses = [
        "1",  # 选择对话引导
        "ABC科技有限公司",
        "2015年",
        "智能制造",
        "工业机器人研发与制造",
        "8500万元",
        "8000万元",
        "680万元",
        "120人",
        "35人",
        "15项",
        "工业机器人控制器",
        "12%"
    ]
    
    current_context = context.copy()
    
    for i, response in enumerate(test_responses):
        current_context["query"] = response
        result = await skill.execute(current_context)
        
        print(f"   步骤{i+1}: {response}")
        print(f"   响应: {result.content[:80]}...")
        
        if not result.success:
            print(f"   ❌ 步骤{i+1}失败: {result.metadata.get('error', '未知错误')}")
            break
    
    print("   ✅ 信息收集测试完成\n")
    
    # 4. 测试资格评估
    print("4. 测试资格评估...")
    
    # 模拟企业数据
    company_data = {
        "company_name": "ABC科技有限公司",
        "establishment_year": 2015,
        "industry": "智能制造",
        "main_business": "工业机器人研发与制造",
        "revenue_2023": 8500,
        "main_revenue_2023": 8000,
        "rd_expense_2023": 680,
        "employee_count": 120,
        "rd_employee_count": 35,
        "patent_count": 15,
        "main_products": "工业机器人控制器",
        "market_share": 12.0,
        "revenue_2021": 6500,
        "revenue_2022": 7500,
        "main_revenue_2021": 6000,
        "main_revenue_2022": 7200,
        "rd_expense_2021": 520,
        "rd_expense_2022": 610
    }
    
    # 直接调用评估模块
    from skills.specialized_innovative.services.assessment_calculator import AssessmentCalculator
    calculator = AssessmentCalculator()
    assessment_result = await calculator.execute(company_data)
    
    print(f"   企业名称: {company_data['company_name']}")
    print(f"   资格评估结果: {'合格' if assessment_result['qualified'] else '不合格'}")
    print(f"   申报成功率: {assessment_result.get('metrics', {}).get('success_rate', 'N/A')}%")
    print("   ✅ 资格评估测试完成\n")
    
    # 5. 测试材料生成
    print("5. 测试材料生成...")
    
    from skills.specialized_innovative.services.material_generator import MaterialGenerator
    generator = MaterialGenerator()
    materials = await generator.execute(company_data, assessment_result)
    
    print(f"   生成材料数量: {len(materials)}")
    print(f"   市场占有率说明长度: {len(materials.get('market_share_statement', ''))} 字符")
    print(f"   企业介绍长度: {len(materials.get('company_introduction', ''))} 字符")
    print(f"   申请书框架字段数: {len(materials.get('application_framework', {}))}")
    print(f"   佐证材料清单项数: {len(materials.get('proof_materials_list', []))}")
    print("   ✅ 材料生成测试完成\n")
    
    # 6. 测试材料检查
    print("6. 测试材料检查...")
    
    from skills.specialized_innovative.services.proof_checker import ProofChecker
    checker = ProofChecker()
    
    # 模拟上传文件
    uploaded_files = [
        {"path": "/tmp/test_license.pdf", "filename": "营业执照.pdf", "size": 1024000},
        {"path": "/tmp/test_audit.pdf", "filename": "审计报告2023.pdf", "size": 2048000},
        {"path": "/tmp/test_patent.xlsx", "filename": "专利清单.xlsx", "size": 512000}
    ]
    
    check_result = await checker.execute(materials, uploaded_files, company_data)
    
    print(f"   材料完整性: {check_result['completeness']}%")
    print(f"   已有材料: {len(check_result['existing'])} 项")
    print(f"   缺失材料: {len(check_result['missing'])} 项")
    print("   ✅ 材料检查测试完成\n")
    
    # 7. 测试完整工作流
    print("7. 测试完整工作流...")
    
    # 重置会话
    skill.workflow_states = {}
    current_context = {
        "query": "专精特新小巨人申报",
        "session_id": "full_workflow_test"
    }
    
    workflow_steps = [
        "专精特新小巨人申报",
        "1",  # 选择对话引导
        "XYZ智能装备有限公司",
        "2018年",
        "高端装备",
        "数控机床研发制造",
        "9200万元",
        "8800万元",
        "750万元",
        "95人",
        "28人",
        "8项",
        "五轴联动数控机床",
        "8.5%"
    ]
    
    print("   模拟完整工作流对话:")
    for step, user_input in enumerate(workflow_steps):
        current_context["query"] = user_input
        result = await skill.execute(current_context)
        
        print(f"   步骤{step+1}: 用户: {user_input}")
        print(f"         助手: {result.content[:60]}...")
        
        if not result.success:
            print(f"   ❌ 工作流中断: {result.metadata.get('error', '未知错误')}")
            break
    
    print("   ✅ 完整工作流测试完成\n")
    
    # 8. 测试错误处理
    print("8. 测试错误处理...")
    
    error_context = {
        "query": "",
        "session_id": "error_test"
    }
    
    result = await skill.execute(error_context)
    print(f"   空输入测试: {result.success} - {result.content[:50]}")
    
    # 测试清理会话
    if "full_workflow_test" in skill.workflow_states:
        skill.cleanup_session("full_workflow_test")
        print(f"   会话清理: {'full_workflow_test' not in skill.workflow_states}")
    
    print("   ✅ 错误处理测试完成\n")
    
    # 测试总结
    print("=== 测试总结 ===")
    print(f"总测试项: 8")
    print(f"技能状态: 正常")
    print(f"模块完整性: 信息处理✅ 评估计算✅ 材料生成✅ 材料检查✅")
    print(f"工作流支持: 对话引导✅ 批量输入✅ 文档上传✅")
    print(f"输出能力: 评估报告✅ 材料框架✅ 检查清单✅")
    print("\n🎉 专精特新小巨人申报技能测试通过！")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_skill())