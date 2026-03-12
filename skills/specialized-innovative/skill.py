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
        
        msg = "申报流程已完成！\n\n已生成完整的申报材料包，包括：\n"
        msg += "1. 专精特新小巨人申请书\n"
        msg += "2. 佐证材料清单\n"
        msg += "3. 申报成功率评估报告\n"
        msg += "4. 缺失材料提示清单\n"
        msg += "5. 企业2000字介绍文档\n"
        msg += "6. 市场占有率说明文档\n\n"
        msg += "请输入'重新开始'开始新的申报，或'查看详情'查看具体内容。"
        
        return SkillResult(
            success=True,
            content=msg,
            metadata={
                "action": "final_output",
                "session_id": session_id,
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
        # 这里可以生成文件并返回文件路径
        # 简化版本：返回结构化数据
        
        output_dir = f"./output/specialized_innovative/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = []
        
        # 保存评估报告
        if "assessment" in state:
            report_path = os.path.join(output_dir, "assessment_report.json")
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(state["assessment"], f, ensure_ascii=False, indent=2)
            output_files.append(report_path)
        
        # 保存材料
        if "materials" in state:
            materials_path = os.path.join(output_dir, "generated_materials.json")
            with open(materials_path, 'w', encoding='utf-8') as f:
                json.dump(state["materials"], f, ensure_ascii=False, indent=2)
            output_files.append(materials_path)
        
        # 保存检查结果
        if "proof_check" in state:
            check_path = os.path.join(output_dir, "proof_check_result.json")
            with open(check_path, 'w', encoding='utf-8') as f:
                json.dump(state["proof_check"], f, ensure_ascii=False, indent=2)
            output_files.append(check_path)
        
        return {
            "output_dir": output_dir,
            "files": output_files,
            "summary": {
                "company_data": state.get("data", {}),
                "assessment": state.get("assessment", {}),
                "materials": state.get("materials", {}),
                "proof_check": state.get("proof_check", {})
            }
        }
    
    def cleanup_session(self, session_id: str):
        """清理会话状态"""
        if session_id in self.workflow_states:
            del self.workflow_states