"""
专精特新小巨人申报技能主类
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from common.log import logger
from agent.skills.types import Skill, SkillContext, SkillResult


class SpecializedInnovativeSkill(Skill):
    """专精特新小巨人申报技能"""
    
    def __init__(self):
        super().__init__()
        self.name = "专精特新小巨人申报助手"
        self.description = "帮助企业完成专精特新小巨人申报全流程"
        self.version = "1.0.0"
        
        # 初始化模块
        from .services.info_processor import InfoProcessor
        from .services.assessment_calculator import AssessmentCalculator
        from .services.material_generator import MaterialGenerator
        from .services.proof_checker import ProofChecker
        
        self.info_processor = InfoProcessor()
        self.assessment_calculator = AssessmentCalculator()
        self.material_generator = MaterialGenerator()
        self.proof_checker = ProofChecker()
        
        # 工作流状态
        self.workflow_states = {}
        
        logger.info(f"[专精特新] 技能初始化完成: {self.name}")
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """执行技能"""
        try:
            user_input = context.get("query", "").strip()
            session_id = context.get("session_id", "default")
            
            logger.info(f"[专精特新] 收到用户请求: {user_input[:50]}...")
            
            # 检查是否开始申报流程
            if "专精特新" in user_input or "小巨人" in user_input or "申报" in user_input:
                return await self.start_application_flow(context, session_id)
            
            # 检查是否在工作流中
            if session_id in self.workflow_states:
                return await self.continue_workflow(context, session_id)
            
            # 默认回复
            return SkillResult(
                success=True,
                content="我是专精特新小巨人申报助手。请输入'专精特新申报'开始申报流程，或上传企业相关文档。",
                metadata={"action": "greeting"}
            )
            
        except Exception as e:
            logger.error(f"[专精特新] 技能执行错误: {e}")
            return SkillResult(
                success=False,
                content=f"抱歉，处理过程中出现错误: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def start_application_flow(self, context: SkillContext, session_id: str) -> SkillResult:
        """开始申报流程"""
        # 初始化工作流状态
        self.workflow_states[session_id] = {
            "step": "info_collection",
            "data": {},
            "start_time": datetime.now().isoformat(),
            "files": context.get("files", [])
        }
        
        welcome_msg = """欢迎使用专精特新小巨人申报助手！🏢

我将引导您完成专精特新企业申报的全流程。根据技能文件，我可以帮助您完成从信息收集、资格评估、材料生成到材料检查的完整申报流程。

首先，请选择信息提供方式：

**请选择信息收集方式：**

**1. 上传文档**（推荐）：上传企业审计报告、营业执照、专利清单等文档
**2. 批量输入**：一次性提供企业关键信息
**3. 对话引导**：通过问答逐步提供信息

**请回复数字 1、2 或 3 选择方式，或直接上传相关文档。**

**申报流程说明：**
1. 信息收集 → 收集企业基本信息、财务数据、研发情况等
2. 资格评估 → 评估是否符合专精特新申报条件，计算成功率
3. 材料生成 → 生成申报所需的各种文档和材料清单
4. 材料检查 → 检查佐证材料完整性，提供补充建议

**您希望从哪种方式开始？**"""
        
        return SkillResult(
            success=True,
            content=welcome_msg,
            metadata={
                "action": "start_flow",
                "session_id": session_id,
                "step": "info_collection",
                "options": ["1", "2", "3"]
            }
        )
    
    async def continue_workflow(self, context: SkillContext, session_id: str) -> SkillResult:
        """继续工作流"""
        state = self.workflow_states[session_id]
        current_step = state["step"]
        user_input = context.get("query", "").strip()
        files = context.get("files", [])
        
        logger.info(f"[专精特新] 继续工作流，步骤: {current_step}, 输入: {user_input[:50]}...")
        
        # 更新文件列表
        if files:
            state["files"].extend(files)
        
        # 根据当前步骤处理
        if current_step == "info_collection":
            return await self.handle_info_collection(state, user_input, files, session_id)
        elif current_step == "assessment":
            return await self.handle_assessment(state, user_input, session_id)
        elif current_step == "material_generation":
            return await self.handle_material_generation(state, user_input, session_id)
        elif current_step == "proof_checking":
            return await self.handle_proof_checking(state, user_input, session_id)
        elif current_step == "completion":
            return await self.handle_completion(state, user_input, session_id)
        else:
            return SkillResult(
                success=False,
                content="工作流状态异常，请重新开始。",
                metadata={"error": "invalid_step"}
            )
    
    async def handle_info_collection(self, state: Dict, user_input: str, files: List, session_id: str) -> SkillResult:
        """处理信息收集"""
        try:
            # 处理用户选择或输入
            if user_input in ["1", "上传文档"]:
                if files:
                    # 从文档提取信息
                    extracted_data = await self.info_processor.extract_from_documents(files)
                    state["data"].update(extracted_data)
                    
                    # 检查完整性
                    completeness = self.info_processor.check_completeness(state["data"])
                    
                    if completeness >= 80:
                        # 进入下一阶段
                        state["step"] = "assessment"
                        msg = f"已从文档提取信息，完整性{completeness}%。\n\n开始进行资格评估..."
                    else:
                        # 需要补充信息
                        missing = self.info_processor.get_missing_fields(state["data"])
                        questions = self.info_processor.generate_questions(missing, state["data"])
                        
                        msg = f"已从文档提取部分信息，完整性{completeness}%。\n\n请补充以下信息：\n"
                        for i, q in enumerate(questions[:3], 1):
                            msg += f"{i}. {q}\n"
                        
                        if len(questions) > 3:
                            msg += f"...等{len(questions)}个问题"
                
                else:
                    msg = "请上传企业相关文档（审计报告、营业执照、专利清单等）。"
                    
            elif user_input in ["2", "批量输入"]:
                msg = "请一次性提供企业关键信息，格式如：\n企业名称：XXX\n成立时间：XXXX年\n主营业务：XXX\n年营收：XXX万元\n..."
                state["info_mode"] = "batch_input"
                
            elif user_input in ["3", "对话引导"]:
                msg = "好的，我将通过问答引导您提供信息。\n\n首先，请问企业全称是什么？"
                state["info_mode"] = "conversation"
                state["conversation_step"] = 0
                
            elif state.get("info_mode") == "batch_input" and user_input:
                # 解析批量输入
                parsed_data = await self.info_processor.parse_text_input(user_input)
                state["data"].update(parsed_data)
                
                completeness = self.info_processor.check_completeness(state["data"])
                if completeness >= 70:
                    state["step"] = "assessment"
                    msg = f"信息接收完成，完整性{completeness}%。\n\n开始进行资格评估..."
                else:
                    missing = self.info_processor.get_missing_fields(state["data"])
                    questions = self.info_processor.generate_questions(missing, state["data"])
                    
                    msg = f"信息接收部分完成，完整性{completeness}%。\n\n请补充：\n"
                    for i, q in enumerate(questions[:3], 1):
                        msg += f"{i}. {q}\n"
                        
            elif state.get("info_mode") == "conversation" and user_input:
                # 对话引导处理
                conversation_result = await self.info_processor.handle_conversation(
                    user_input, state.get("conversation_step", 0), state["data"]
                )
                
                state["data"].update(conversation_result.get("extracted_data", {}))
                state["conversation_step"] = conversation_result.get("next_step", 0)
                
                if conversation_result.get("completed", False):
                    state["step"] = "assessment"
                    msg = "信息收集完成！\n\n开始进行资格评估..."
                else:
                    msg = conversation_result.get("next_question", "请继续提供信息。")
                    
            else:
                msg = "请选择信息提供方式：1.上传文档 2.批量输入 3.对话引导"
            
            # 保存状态
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "info_collection",
                    "step": state["step"],
                    "session_id": session_id,
                    "completeness": state["data"].get("completeness", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"[专精特新] 信息收集错误: {e}")
            return SkillResult(
                success=False,
                content=f"信息处理出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_assessment(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理资格评估"""
        try:
            company_data = state["data"]
            
            # 执行评估
            assessment_result = await self.assessment_calculator.execute(company_data)
            
            # 更新状态
            state["assessment"] = assessment_result
            state["step"] = "material_generation"
            
            # 生成评估报告
            report = self.format_assessment_report(assessment_result)
            
            msg = f"资格评估完成！\n\n{report}\n\n开始生成申报材料..."
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "assessment_complete",
                    "step": state["step"],
                    "session_id": session_id,
                    "assessment_result": assessment_result
                }
            )
            
        except Exception as e:
            logger.error(f"[专精特新] 资格评估错误: {e}")
            return SkillResult(
                success=False,
                content=f"资格评估出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_material_generation(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理材料生成"""
        try:
            company_data = state["data"]
            assessment = state.get("assessment", {})
            
            # 生成材料
            materials = await self.material_generator.execute(company_data, assessment)
            
            # 更新状态
            state["materials"] = materials
            state["step"] = "proof_checking"
            
            msg = "申报材料生成完成！\n\n开始检查佐证材料..."
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "materials_generated",
                    "step": state["step"],
                    "session_id": session_id,
                    "materials_count": len(materials)
                }
            )
            
        except Exception as e:
            logger.error(f"[专精特新] 材料生成错误: {e}")
            return SkillResult(
                success=False,
                content=f"材料生成出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_proof_checking(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理佐证材料检查"""
        try:
            company_data = state["data"]
            materials = state.get("materials", {})
            uploaded_files = state.get("files", [])
            
            # 检查材料
            check_result = await self.proof_checker.execute(materials, uploaded_files, company_data)
            
            # 更新状态
            state["proof_check"] = check_result
            state["step"] = "completion"
            
            # 生成检查报告
            report = self.format_proof_check_report(check_result)
            
            msg = f"佐证材料检查完成！\n\n{report}\n\n申报流程完成！"
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "workflow_complete",
                    "step": state["step"],
                    "session_id": session_id,
                    "check_result": check_result
                }
            )
            
        except Exception as e:
            logger.error(f"[专精特新] 材料检查错误: {e}")
            return SkillResult(
                success=False,
                content=f"材料检查出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_completion(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理完成阶段"""
        # 生成最终输出
        final_output = await self.generate_final_output(state)
        
        company_name = final_output.get("company_name", "未知公司")
        output_dir = final_output.get("output_dir", "")
        folder_structure = final_output.get("folder_structure", {})
        
        # 获取相对路径（相对于项目根目录）
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        relative_dir = os.path.relpath(output_dir, project_root) if output_dir else ""
        
        msg = f"🎉 申报流程已完成！\n\n"
        msg += f"**已为「{company_name}」创建专属申报文件夹**\n\n"
        
        msg += "**📁 文件夹结构：**\n"
        msg += f"`{relative_dir}/`\n"
        msg += "├── 公司基本信息.json          # 公司基本信息\n"
        msg += "├── 文件夹结构说明.txt        # 文件夹结构说明\n"
        msg += "├── 原始文档/                 # 上传的原始文档 ({folder_structure.get('原始文档', 0)}个文件)\n"
        msg += "├── 评估报告/                 # 资格评估相关文件 ({folder_structure.get('评估报告', 0)}个文件)\n"
        msg += "├── 生成材料/                 # 生成的申报材料 ({folder_structure.get('生成材料', 0)}个文件)\n"
        msg += "├── 佐证材料/                 # 材料检查报告 ({folder_structure.get('佐证材料', 0)}个文件)\n"
        msg += "└── 最终申报包/               # 最终申报材料包 ({folder_structure.get('最终申报包', 0)}个文件)\n\n"
        
        msg += "**📄 包含内容：**\n"
        msg += "1. 公司基本信息文件\n"
        msg += "2. 专精特新小巨人资格评估报告\n"
        msg += "3. 申报材料清单和模板\n"
        msg += "4. 佐证材料检查报告\n"
        msg += "5. 原始上传文档备份\n"
        msg += "6. 最终申报材料包\n\n"
        
        msg += "**💡 使用说明：**\n"
        msg += "1. 检查「佐证材料」中的缺失材料清单\n"
        msg += "2. 根据「生成材料」中的清单准备完整材料\n"
        msg += "3. 参考「最终申报包」中的说明完成申报\n"
        msg += "4. 所有材料已按类别整理，便于查找和管理\n\n"
        
        msg += "**🔧 后续操作：**\n"
        msg += "• 输入'查看详情'查看具体文件内容\n"
        msg += "• 输入'重新开始'为其他公司开始新的申报\n"
        msg += "• 输入'导出材料'导出申报材料包\n"
        msg += "• 所有文件已保存在专属文件夹中，便于后续查阅\n"
        
        return SkillResult(
            success=True,
            content=msg,
            metadata={
                "action": "final_output",
                "session_id": session_id,
                "company_name": company_name,
                "output_dir": output_dir,
                "relative_dir": relative_dir,
                "folder_structure": folder_structure,
                "output_files": final_output.get("files", [])
            }
        )
    
    def format_assessment_report(self, assessment_result: Dict) -> str:
        """格式化评估报告"""
        report = "【资格评估结果】\n\n"
        
        if assessment_result.get("qualified", False):
            report += "✅ 符合申报基本条件\n\n"
        else:
            report += "❌ 暂不符合申报条件\n\n"
        
        # 各项指标
        indicators = assessment_result.get("indicators", {})
        for category, result in indicators.items():
            if result.get("passed", False):
                report += f"✅ {category}: 通过\n"
            else:
                report += f"❌ {category}: 不通过 - {result.get('reason', '')}\n"
        
        # 建议
        suggestions = assessment_result.get("suggestions", [])
        if suggestions:
            report += "\n【改进建议】\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                report += f"{i}. {suggestion}\n"
        
        return report
    
    def format_proof_check_report(self, check_result: Dict) -> str:
        """格式化材料检查报告"""
        report = "【佐证材料检查结果】\n\n"
        
        completeness = check_result.get("completeness", 0)
        report += f"材料完整性: {completeness}%\n\n"
        
        existing = check_result.get("existing", [])
        missing = check_result.get("missing", [])
        
        if existing:
            report += "✅ 已有材料：\n"
            for material in existing[:5]:
                report += f"  • {material}\n"
            if len(existing) > 5:
                report += f"  等{len(existing)}项\n"
        
        if missing:
            report += "\n❌ 缺失材料：\n"
            for material in missing[:5]:
                report += f"  • {material}\n"
            if len(missing) > 5:
                report += f"  等{len(missing)}项\n"
        
        return report
    
    async def generate_final_output(self, state: Dict) -> Dict:
        """生成最终输出"""
        # 获取公司名称，用于创建文件夹
        company_data = state.get("data", {})
        company_name = company_data.get("company_name", "未知公司")
        
        # 清理公司名称，移除非法字符
        import re
        safe_company_name = re.sub(r'[<>:"/\\|?*]', '_', company_name)
        safe_company_name = safe_company_name.strip()[:50]  # 限制长度
        
        # 创建公司专属文件夹
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f"./output/specialized_innovative/{safe_company_name}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建子文件夹结构
        subdirs = ["原始文档", "评估报告", "生成材料", "佐证材料", "最终申报包"]
        for subdir in subdirs:
            os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
        
        output_files = []
        
        # 1. 保存公司基本信息（保存为txt格式）
        company_info_path = os.path.join(output_dir, "公司基本信息.txt")
        with open(company_info_path, 'w', encoding='utf-8') as f:
            f.write(f"公司基本信息\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"公司名称: {company_name}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            
            # 格式化输出公司信息
            for key, value in company_data.items():
                if isinstance(value, dict):
                    f.write(f"{key}:\n")
                    for sub_key, sub_value in value.items():
                        f.write(f"  {sub_key}: {sub_value}\n")
                elif isinstance(value, list):
                    f.write(f"{key}:\n")
                    for item in value:
                        f.write(f"  • {item}\n")
                else:
                    f.write(f"{key}: {value}\n")
                f.write("\n")
        
        output_files.append(company_info_path)
        
        # 2. 保存评估报告（只保存txt格式，不保存JSON）
        if "assessment" in state:
            # 生成可读的评估报告文本
            txt_report_path = os.path.join(output_dir, "评估报告", "资格评估报告.txt")
            with open(txt_report_path, 'w', encoding='utf-8') as f:
                f.write(f"专精特新小巨人申报资格评估报告\n")
                f.write(f"公司名称: {company_name}\n")
                f.write(f"评估时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write(f"{'='*50}\n\n")
                
                assessment = state["assessment"]
                if assessment.get("qualified", False):
                    f.write("✅ 符合申报基本条件\n\n")
                else:
                    f.write("❌ 暂不符合申报条件\n\n")
                
                # 各项指标
                indicators = assessment.get("indicators", {})
                for category, result in indicators.items():
                    if result.get("passed", False):
                        f.write(f"✅ {category}: 通过\n")
                    else:
                        f.write(f"❌ {category}: 不通过 - {result.get('reason', '')}\n")
                
                # 建议
                suggestions = assessment.get("suggestions", [])
                if suggestions:
                    f.write("\n【改进建议】\n")
                    for i, suggestion in enumerate(suggestions, 1):
                        f.write(f"{i}. {suggestion}\n")
                
                # 添加评估详情
                f.write(f"\n{'='*50}\n")
                f.write("评估详情:\n")
                for key, value in assessment.items():
                    if key not in ["qualified", "indicators", "suggestions"]:
                        if isinstance(value, dict):
                            f.write(f"{key}:\n")
                            for sub_key, sub_value in value.items():
                                f.write(f"  {sub_key}: {sub_value}\n")
                        elif isinstance(value, list):
                            f.write(f"{key}:\n")
                            for item in value:
                                f.write(f"  • {item}\n")
                        else:
                            f.write(f"{key}: {value}\n")
            
            output_files.append(txt_report_path)
        
        # 3. 保存生成的材料（只保存txt格式，不保存JSON）
        if "materials" in state:
            # 生成材料清单文本
            txt_materials_path = os.path.join(output_dir, "生成材料", "申报材料清单.txt")
            with open(txt_materials_path, 'w', encoding='utf-8') as f:
                f.write(f"专精特新小巨人申报材料清单\n")
                f.write(f"公司名称: {company_name}\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write(f"{'='*50}\n\n")
                
                materials = state["materials"]
                for category, items in materials.items():
                    f.write(f"【{category}】\n")
                    if isinstance(items, list):
                        for item in items:
                            f.write(f"  • {item}\n")
                    elif isinstance(items, dict):
                        for key, value in items.items():
                            f.write(f"  • {key}: {value}\n")
                    f.write("\n")
            
            output_files.append(txt_materials_path)
        
        # 4. 保存检查结果（只保存txt格式，不保存JSON）
        if "proof_check" in state:
            # 生成检查报告文本
            txt_check_path = os.path.join(output_dir, "佐证材料", "材料检查报告.txt")
            with open(txt_check_path, 'w', encoding='utf-8') as f:
                f.write(f"佐证材料检查报告\n")
                f.write(f"公司名称: {company_name}\n")
                f.write(f"检查时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
                f.write(f"{'='*50}\n\n")
                
                check_result = state["proof_check"]
                completeness = check_result.get("completeness", 0)
                f.write(f"材料完整性: {completeness}%\n\n")
                
                existing = check_result.get("existing", [])
                missing = check_result.get("missing", [])
                
                if existing:
                    f.write("✅ 已有材料：\n")
                    for material in existing:
                        f.write(f"  • {material}\n")
                
                if missing:
                    f.write("\n❌ 缺失材料：\n")
                    for material in missing:
                        f.write(f"  • {material}\n")
                
                # 添加检查详情
                f.write(f"\n{'='*50}\n")
                f.write("检查详情:\n")
                for key, value in check_result.items():
                    if key not in ["completeness", "existing", "missing"]:
                        if isinstance(value, dict):
                            f.write(f"{key}:\n")
                            for sub_key, sub_value in value.items():
                                f.write(f"  {sub_key}: {sub_value}\n")
                        elif isinstance(value, list):
                            f.write(f"{key}:\n")
                            for item in value:
                                f.write(f"  • {item}\n")
                        else:
                            f.write(f"{key}: {value}\n")
            
            output_files.append(txt_check_path)
        
        # 5. 复制上传的文件到原始文档文件夹
        uploaded_files = state.get("files", [])
        for file_info in uploaded_files:
            if isinstance(file_info, dict) and "file_path" in file_info:
                import shutil
                try:
                    src_path = file_info["file_path"]
                    if os.path.exists(src_path):
                        filename = os.path.basename(src_path)
                        dest_path = os.path.join(output_dir, "原始文档", filename)
                        shutil.copy2(src_path, dest_path)
                        output_files.append(dest_path)
                except Exception as e:
                    logger.warning(f"[专精特新] 复制文件失败: {e}")
        
        # 6. 创建最终申报包
        final_package_dir = os.path.join(output_dir, "最终申报包")
        
        # 创建申报包说明
        readme_path = os.path.join(final_package_dir, "申报包说明.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"专精特新小巨人申报材料包\n")
            f.write(f"公司名称: {company_name}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            f.write("本申报包包含以下内容：\n")
            f.write("1. 公司基本信息\n")
            f.write("2. 资格评估报告\n")
            f.write("3. 申报材料清单\n")
            f.write("4. 佐证材料检查报告\n")
            f.write("5. 原始上传文档\n")
            f.write("6. 最终申报材料\n\n")
            f.write("请按照以下步骤完成申报：\n")
            f.write("1. 检查缺失材料并补充\n")
            f.write("2. 根据材料清单准备完整材料\n")
            f.write("3. 提交至相关政府部门\n")
            f.write("4. 跟进申报进度\n")
        
        output_files.append(readme_path)
        
        # 7. 创建文件夹结构说明
        structure_path = os.path.join(output_dir, "文件夹结构说明.txt")
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write(f"文件夹结构说明\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"{output_dir}/\n")
            f.write(f"├── 公司基本信息.txt          # 公司基本信息\n")
            f.write(f"├── 文件夹结构说明.txt        # 本文件\n")
            f.write(f"├── 原始文档/                 # 上传的原始文档\n")
            f.write(f"├── 评估报告/                 # 资格评估相关文件\n")
            f.write(f"├── 生成材料/                 # 生成的申报材料\n")
            f.write(f"├── 佐证材料/                 # 材料检查报告\n")
            f.write(f"└── 最终申报包/               # 最终申报材料包\n")
        
        output_files.append(structure_path)
        
        logger.info(f"[专精特新] 为{company_name}创建申报文件夹: {output_dir}")
        
        return {
            "output_dir": output_dir,
            "company_name": company_name,
            "files": output_files,
            "folder_structure": {
                "原始文档": len(uploaded_files),
                "评估报告": 1 if "assessment" in state else 0,
                "生成材料": 1 if "materials" in state else 0,
                "佐证材料": 1 if "proof_check" in state else 0,
                "最终申报包": 1
            },
            "summary": {
                "company_data": company_data,
                "assessment": state.get("assessment", {}),
                "materials": state.get("materials", {}),
                "proof_check": state.get("proof_check", {})
            }
        }
    
    def cleanup_session(self, session_id: str):
        """清理会话状态"""
        if session_id in self.workflow_states:
            del self.workflow_states
