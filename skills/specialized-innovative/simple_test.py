#!/usr/bin/env python3
"""
专精特新小巨人申报技能简单测试
"""

import sys
import os
import asyncio

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "..", ".."))

print(f"当前目录: {current_dir}")
print(f"Python路径: {sys.path[:3]}")

# 尝试导入
try:
    # 直接导入本地模块
    from skill import SpecializedInnovativeSkill
    print("✅ 成功导入技能类")
    
    # 测试创建实例
    skill = SpecializedInnovativeSkill()
    print(f"✅ 技能创建成功: {skill.name}")
    print(f"✅ 技能描述: {skill.description}")
    
    # 测试欢迎消息
    async def test_welcome():
        context = {
            "query": "专精特新申报",
            "session_id": "test_001"
        }
        result = await skill.execute(context)
        print(f"✅ 欢迎消息测试: {result.success}")
        print(f"   响应内容: {result.content[:80]}...")
    
    asyncio.run(test_welcome())
    
    # 测试服务模块
    try:
        from services.assessment_calculator import AssessmentCalculator
        print("✅ 成功导入评估计算模块")
        
        from services.material_generator import MaterialGenerator
        print("✅ 成功导入材料生成模块")
        
        from services.proof_checker import ProofChecker
        print("✅ 成功导入材料检查模块")
        
        print("\n🎉 所有模块导入成功！")
        
    except ImportError as e:
        print(f"❌ 服务模块导入失败: {e}")
        
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("\n尝试直接导入...")
    
    # 尝试直接导入文件
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("skill", os.path.join(current_dir, "skill.py"))
        skill_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(skill_module)
        print("✅ 直接导入技能文件成功")
    except Exception as e2:
        print(f"❌ 直接导入也失败: {e2}")