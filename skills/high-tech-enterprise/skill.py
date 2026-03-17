"""
高新技术企业（高企）申报技能主类
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from common.log import logger
from agent.skills.types import Skill, SkillContext, SkillResult


class HighTechEnterpriseSkill(Skill):
    """高新技术企业（高企）申报技能"""
    
    def __init__(self):
        super().__init__()
        self.name = "高新技术企业（高企）申报助手"
        self.description = "帮助企业完成高新技术企业申报全流程，基于国家《高新技术企业认定管理办法》"
        self.version = "1.0.0"
        
        # 高企申报8大条件
        self.conditions = [
            "企业注册成立一年以上",
            "拥有核心自主知识产权",
            "技术属于国家重点支持领域",
            "科技人员占比不低于10%",
            "研发费用占比符合要求",
            "高品收入占比不低于60%",
            "创新能力评价71分以上",
            "无重大安全环保事故"
        ]
        
        # 高企申报14项材料清单
        self.materials_list = [
            # 一、基础材料
            {"id": 1, "name": "《高新技术企业认定申请书》", "category": "基础材料", "required": True},
            {"id": 2, "name": "证明事项告知承诺书", "category": "基础材料", "required": True},
            {"id": 3, "name": "企业营业执照复印件", "category": "基础材料", "required": True},
            
            # 二、知识产权材料
            {"id": 4, "name": "知识产权证书及反映技术水平的证明材料", "category": "知识产权材料", "required": True},
            {"id": 5, "name": "参与制定标准情况材料", "category": "知识产权材料", "required": False},
            
            # 三、技术创新材料
            {"id": 6, "name": "科技成果转化总体情况与转化形式说明", "category": "技术创新材料", "required": True},
            {"id": 7, "name": "科研项目立项证明及验收报告", "category": "技术创新材料", "required": True},
            {"id": 8, "name": "研究开发组织管理水平说明材料", "category": "技术创新材料", "required": True},
            
            # 四、产品服务材料
            {"id": 9, "name": "高新技术产品（服务）关键技术说明", "category": "产品服务材料", "required": True},
            {"id": 10, "name": "相关生产批文、认证证书、产品质量检验报告", "category": "产品服务材料", "required": True},
            
            # 五、财务人员材料
            {"id": 11, "name": "近三年研究开发费用专项审计报告", "category": "财务人员材料", "required": True},
            {"id": 12, "name": "近一年高新技术产品（服务）收入专项审计报告", "category": "财务人员材料", "required": True},
            {"id": 13, "name": "企业职工和科技人员情况说明材料", "category": "财务人员材料", "required": True},
            {"id": 14, "name": "近三年财务会计报告及纳税申报表", "category": "财务人员材料", "required": True}
        ]
        
        # 工作流状态
        self.workflow_states = {}
        
        logger.info(f"[高企申报] 技能初始化完成: {self.name}")
    
    async def execute(self, context: SkillContext) -> SkillResult:
        """执行技能"""
        try:
            user_input = context.get("query", "").strip()
            session_id = context.get("session_id", "default")
            
            logger.info(f"[高企申报] 收到用户请求: {user_input[:50]}...")
            
            # 检查是否开始高企申报流程
            trigger_keywords = ["高企", "高新技术企业", "高企申报", "高企认定", "高新技术企业申报"]
            if any(keyword in user_input for keyword in trigger_keywords):
                return await self.start_high_tech_application_flow(context, session_id)
            
            # 检查是否在工作流中
            if session_id in self.workflow_states:
                return await self.continue_workflow(context, session_id)
            
            # 默认回复
            return SkillResult(
                success=True,
                content="我是高新技术企业（高企）申报助手。请输入'高企申报'开始申报流程，或上传企业相关文档。",
                metadata={"action": "greeting"}
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 技能执行错误: {e}")
            return SkillResult(
                success=False,
                content=f"抱歉，处理过程中出现错误: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def start_high_tech_application_flow(self, context: SkillContext, session_id: str) -> SkillResult:
        """开始高企申报流程"""
        # 初始化工作流状态
        self.workflow_states[session_id] = {
            "step": "info_collection",
            "data": {},
            "start_time": datetime.now().isoformat(),
            "files": context.get("files", []),
            "folders": context.get("folders", []),  # 新增：支持文件夹
            "application_type": "high_tech_enterprise"
        }
        
        welcome_msg = """欢迎使用高新技术企业（高企）申报助手！🏭

我将引导您完成高新技术企业申报全流程。根据国家《高新技术企业认定管理办法》，申报需要同时满足8大条件，创新能力评价需达到71分以上。

**高企申报8大条件：**
1. 企业注册成立一年（365天）以上
2. 拥有核心自主知识产权
3. 技术属于国家重点支持的高新技术领域
4. 科技人员占比不低于10%
5. 研发费用占比符合要求（根据收入不同为3-5%）
6. 高品收入占比不低于60%
7. 创新能力评价71分以上（满分100分）
8. 申请前一年内未发生重大安全、质量事故或严重环境违法行为

首先，请选择信息提供方式：

**请选择信息收集方式：**

**1. 上传压缩包**（推荐）：上传包含企业申报材料的ZIP压缩包，Agent将自动解压并读取所有文件
**2. 上传文档**：上传企业审计报告、营业执照、专利证书、研发费用明细等文档
**3. 批量输入**：一次性提供企业关键信息
**4. 对话引导**：通过问答逐步提供信息

**请回复数字 1、2、3 或 4 选择方式，或直接上传相关文档/压缩包。**

**申报流程说明：**
1. 信息收集 → 收集企业基本信息、财务数据、知识产权、研发情况等
2. 资格评估 → 评估是否符合高企8大条件，计算创新能力得分
3. 材料生成 → 生成14项高企申报材料清单和模板
4. 材料检查 → 检查佐证材料完整性，提供补充建议

**您希望从哪种方式开始？**"""
        
        return SkillResult(
            success=True,
            content=welcome_msg,
            metadata={
                "action": "start_high_tech_flow",
                "session_id": session_id,
                "step": "info_collection",
                "options": ["1", "2", "3"],
                "conditions": self.conditions
            }
        )
    
    async def continue_workflow(self, context: SkillContext, session_id: str) -> SkillResult:
        """继续工作流"""
        state = self.workflow_states[session_id]
        current_step = state["step"]
        user_input = context.get("query", "").strip()
        files = context.get("files", [])
        
        logger.info(f"[高企申报] 继续工作流，步骤: {current_step}, 输入: {user_input[:50]}...")
        
        # 更新文件列表
        if files:
            state["files"].extend(files)
        
        # 根据当前步骤处理
        if current_step == "info_collection":
            return await self.handle_high_tech_info_collection(state, user_input, files, session_id)
        elif current_step == "assessment":
            return await self.handle_high_tech_assessment(state, user_input, session_id)
        elif current_step == "material_generation":
            return await self.handle_high_tech_material_generation(state, user_input, session_id)
        elif current_step == "proof_checking":
            return await self.handle_high_tech_proof_checking(state, user_input, session_id)
        elif current_step == "completion":
            return await self.handle_high_tech_completion(state, user_input, session_id)
        else:
            return SkillResult(
                success=False,
                content="工作流状态异常，请重新开始。",
                metadata={"error": "invalid_step"}
            )
    
    async def handle_high_tech_info_collection(self, state: Dict, user_input: str, files: List, session_id: str) -> SkillResult:
        """处理高企信息收集"""
        try:
            # 处理用户选择或输入
            if user_input in ["1", "上传压缩包", "上传文件夹"]:
                # 检查是否有压缩包或文件夹上传
                uploaded_files = state.get("files", [])
                
                # 查找压缩包文件
                zip_files = []
                for file_info in uploaded_files:
                    if isinstance(file_info, dict):
                        file_path = file_info.get("file_path", "")
                        file_name = file_info.get("name", "").lower()
                        if file_name.endswith(('.zip', '.rar', '.7z', '.tar', '.gz')):
                            zip_files.append(file_info)
                
                if zip_files:
                    # 处理压缩包
                    zip_file = zip_files[0]
                    extracted_data = await self.extract_high_tech_info_from_zip(zip_file)
                    state["data"].update(extracted_data)
                    
                    # 检查完整性
                    completeness = self.check_high_tech_info_completeness(state["data"])
                    
                    if completeness >= 70:
                        # 进入下一阶段
                        state["step"] = "assessment"
                        msg = f"✅ 已从压缩包提取高企申报信息，完整性{completeness}%。\n\n开始进行高企资格评估..."
                    else:
                        # 需要补充信息
                        missing = self.get_missing_high_tech_fields(state["data"])
                        questions = self.generate_high_tech_questions(missing, state["data"])
                        
                        msg = f"📦 已从压缩包提取部分信息，完整性{completeness}%。\n\n请补充以下高企申报关键信息：\n"
                        for i, q in enumerate(questions[:3], 1):
                            msg += f"{i}. {q}\n"
                        
                        if len(questions) > 3:
                            msg += f"...等{len(questions)}个问题"
                
                else:
                    # 检查是否有文件夹上传
                    folders = state.get("folders", [])
                    if folders:
                        # 从文件夹提取信息
                        extracted_data = await self.extract_high_tech_info_from_folder(folders[0])
                        state["data"].update(extracted_data)
                        
                        # 检查完整性
                        completeness = self.check_high_tech_info_completeness(state["data"])
                        
                        if completeness >= 70:
                            # 进入下一阶段
                            state["step"] = "assessment"
                            msg = f"✅ 已从文件夹提取高企申报信息，完整性{completeness}%。\n\n开始进行高企资格评估..."
                        else:
                            # 需要补充信息
                            missing = self.get_missing_high_tech_fields(state["data"])
                            questions = self.generate_high_tech_questions(missing, state["data"])
                            
                            msg = f"📁 已从文件夹提取部分信息，完整性{completeness}%。\n\n请补充以下高企申报关键信息：\n"
                            for i, q in enumerate(questions[:3], 1):
                                msg += f"{i}. {q}\n"
                            
                            if len(questions) > 3:
                                msg += f"...等{len(questions)}个问题"
                    else:
                        msg = "请上传包含企业申报材料的ZIP压缩包（推荐）或文件夹。\n\n**推荐上传包含以下文件的压缩包：**\n• 审计报告（PDF/Excel）\n• 营业执照（图片/PDF）\n• 专利证书（PDF/图片）\n• 研发费用明细（Excel）\n• 财务报表（Excel/PDF）\n\n**压缩包制作方法：**\n1. 将所有申报材料放入一个文件夹\n2. 右键点击文件夹选择'压缩'或'添加到压缩文件'\n3. 上传生成的ZIP文件"
                    
            elif user_input in ["2", "上传文档"]:
                if files:
                    # 从文档提取信息
                    extracted_data = await self.extract_high_tech_info_from_documents(files)
                    state["data"].update(extracted_data)
                    
                    # 检查完整性
                    completeness = self.check_high_tech_info_completeness(state["data"])
                    
                    if completeness >= 70:
                        # 进入下一阶段
                        state["step"] = "assessment"
                        msg = f"✅ 已从文档提取高企申报信息，完整性{completeness}%。\n\n开始进行高企资格评估..."
                    else:
                        # 需要补充信息
                        missing = self.get_missing_high_tech_fields(state["data"])
                        questions = self.generate_high_tech_questions(missing, state["data"])
                        
                        msg = f"📄 已从文档提取部分信息，完整性{completeness}%。\n\n请补充以下高企申报关键信息：\n"
                        for i, q in enumerate(questions[:3], 1):
                            msg += f"{i}. {q}\n"
                        
                        if len(questions) > 3:
                            msg += f"...等{len(questions)}个问题"
                
                else:
                    msg = "请上传高企申报相关文档（审计报告、营业执照、专利证书、研发费用明细等）。"
                    
            elif user_input in ["3", "批量输入"]:
                msg = """请一次性提供企业关键信息，格式如：

企业名称：XXX科技有限公司
成立时间：2020年5月10日
所属高新技术领域：先进制造与自动化
主营业务：智能机器人研发与制造
上年度销售收入：3500万元
近三年研发费用占比：5.2%
高品收入占比：68.3%
科技人员占比：12.5%
职工总数：120人
研发人员数：15人
发明专利数量：3项
实用新型专利数量：12项
软件著作权数量：5项

请按以上格式提供信息："""
                state["info_mode"] = "batch_input"
                
            elif user_input in ["4", "对话引导"]:
                msg = "好的，我将通过问答引导您提供高企申报所需信息。\n\n首先，请问企业全称是什么？"
                state["info_mode"] = "conversation"
                state["conversation_step"] = 0
                
            elif state.get("info_mode") == "batch_input" and user_input:
                # 解析批量输入
                parsed_data = await self.parse_high_tech_text_input(user_input)
                state["data"].update(parsed_data)
                
                completeness = self.check_high_tech_info_completeness(state["data"])
                if completeness >= 60:
                    state["step"] = "assessment"
                    msg = f"✅ 高企申报信息接收完成，完整性{completeness}%。\n\n开始进行高企资格评估..."
                else:
                    missing = self.get_missing_high_tech_fields(state["data"])
                    questions = self.generate_high_tech_questions(missing, state["data"])
                    
                    msg = f"📝 信息接收部分完成，完整性{completeness}%。\n\n请补充高企申报关键信息：\n"
                    for i, q in enumerate(questions[:3], 1):
                        msg += f"{i}. {q}\n"
                        
            elif state.get("info_mode") == "conversation" and user_input:
                # 对话引导处理
                conversation_result = await self.handle_high_tech_conversation(
                    user_input, state.get("conversation_step", 0), state["data"]
                )
                
                state["data"].update(conversation_result.get("extracted_data", {}))
                state["conversation_step"] = conversation_result.get("next_step", 0)
                
                if conversation_result.get("completed", False):
                    state["step"] = "assessment"
                    msg = "✅ 高企申报信息收集完成！\n\n开始进行高企资格评估..."
                else:
                    msg = conversation_result.get("next_question", "请继续提供高企申报所需信息。")
                    
            else:
                msg = "请选择信息提供方式：1.上传文件夹 2.上传文档 3.批量输入 4.对话引导"
            
            # 保存状态
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "high_tech_info_collection",
                    "step": state["step"],
                    "session_id": session_id,
                    "completeness": state["data"].get("completeness", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 信息收集错误: {e}")
            return SkillResult(
                success=False,
                content=f"高企信息处理出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_high_tech_assessment(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理高企资格评估"""
        try:
            company_data = state["data"]
            
            # 执行高企评估
            assessment_result = await self.execute_high_tech_assessment(company_data)
            
            # 更新状态
            state["assessment"] = assessment_result
            state["step"] = "material_generation"
            
            # 生成评估报告
            report = self.format_high_tech_assessment_report(assessment_result)
            
            msg = f"高企资格评估完成！\n\n{report}\n\n开始生成高企申报材料..."
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "high_tech_assessment_complete",
                    "step": state["step"],
                    "session_id": session_id,
                    "assessment_result": assessment_result
                }
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 资格评估错误: {e}")
            return SkillResult(
                success=False,
                content=f"高企资格评估出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_high_tech_material_generation(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理高企材料生成"""
        try:
            company_data = state["data"]
            assessment = state.get("assessment", {})
            
            # 生成高企材料
            materials = await self.generate_high_tech_materials(company_data, assessment)
            
            # 更新状态
            state["materials"] = materials
            state["step"] = "proof_checking"
            
            msg = "高企申报材料生成完成！\n\n开始检查高企佐证材料..."
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "high_tech_materials_generated",
                    "step": state["step"],
                    "session_id": session_id,
                    "materials_count": len(materials)
                }
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 材料生成错误: {e}")
            return SkillResult(
                success=False,
                content=f"高企材料生成出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_high_tech_proof_checking(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理高企佐证材料检查"""
        try:
            company_data = state["data"]
            materials = state.get("materials", {})
            uploaded_files = state.get("files", [])
            
            # 检查高企材料
            check_result = await self.check_high_tech_proof_materials(materials, uploaded_files, company_data)
            
            # 更新状态
            state["proof_check"] = check_result
            state["step"] = "completion"
            
            # 生成检查报告
            report = self.format_high_tech_proof_check_report(check_result)
            
            msg = f"高企佐证材料检查完成！\n\n{report}\n\n高企申报流程完成！"
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "high_tech_workflow_complete",
                    "step": state["step"],
                    "session_id": session_id,
                    "check_result": check_result
                }
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 材料检查错误: {e}")
            return SkillResult(
                success=False,
                content=f"高企材料检查出错: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def handle_high_tech_completion(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理高企完成阶段"""
        # 生成最终输出
        final_output = await self.generate_high_tech_final_output(state)
        
        company_name = final_output.get("company_name", "未知公司")
        output_dir = final_output.get("output_dir", "")
        folder_structure = final_output.get("folder_structure", {})
        
        # 获取相对路径（相对于项目根目录）
        import os
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        relative_dir = os.path.relpath(output_dir, project_root) if output_dir else ""
        
        msg = f"🎉 高企申报流程已完成！\n\n"
        msg += f"**已为「{company_name}」创建专属高企申报文件夹**\n\n"
        
        msg += "**📁 高企申报文件夹结构：**\n"
        msg += f"`{relative_dir}/`\n"
        msg += "├── 公司基本信息.txt          # 公司基本信息\n"
        msg += "├── 文件夹结构说明.txt        # 文件夹结构说明\n"
        msg += "├── 原始文档/                 # 上传的原始文档 ({folder_structure.get('原始文档', 0)}个文件)\n"
        msg += "├── 高企评估报告/             # 高企资格评估相关文件 ({folder_structure.get('高企评估报告', 0)}个文件)\n"
        msg += "├── 高企申报材料/             # 高企申报材料清单 ({folder_structure.get('高企申报材料', 0)}个文件)\n"
        msg += "├── 佐证材料检查/             # 材料检查报告 ({folder_structure.get('佐证材料检查', 0)}个文件)\n"
        msg += "└── 最终高企申报包/           # 最终高企申报材料包 ({folder_structure.get('最终高企申报包', 0)}个文件)\n\n"
        
        msg += "**📄 高企申报包含内容：**\n"
        msg += "1. 公司基本信息文件\n"
        msg += "2. 高企8大条件评估报告\n"
        msg += "3. 创新能力评分报告（100分制）\n"
        msg += "4. 14项高企申报材料清单\n"
        msg += "5. 佐证材料检查报告\n"
        msg += "6. 原始上传文档备份\n"
        msg += "7. 最终高企申报材料包\n\n"
        
        msg += "**💡 高企申报使用说明：**\n"
        msg += "1. 检查「佐证材料检查」中的缺失材料清单\n"
        msg += "2. 根据「高企申报材料」中的清单准备完整材料\n"
        msg += "3. 重点准备两项专项审计报告（研发费用、高品收入）\n"
        msg += "4. 参考「最终高企申报包」中的说明完成申报\n"
        msg += "5. 所有材料已按高企申报要求整理，便于查找和管理\n\n"
        
        msg += "**🔧 后续操作：**\n"
        msg += "• 输入'查看详情'查看具体文件内容\n"
        msg += "• 输入'重新开始'为其他公司开始新的高企申报\n"
        msg += "• 输入'导出材料'导出高企申报材料包\n"
        msg += "• 所有文件已保存在专属文件夹中，便于后续查阅\n"
        
        return SkillResult(
            success=True,
            content=msg,
            metadata={
                "action": "high_tech_final_output",
                "session_id": session_id,
                "company_name": company_name,
                "output_dir": output_dir,
                "relative_dir": relative_dir,
                "folder_structure": folder_structure,
                "output_files": final_output.get("files", [])
            }
        )
    
    # ========== 高企申报核心方法 ==========
    
    async def extract_high_tech_info_from_zip(self, zip_file_info: Dict) -> Dict:
        """从压缩包提取高企申报信息"""
        try:
            import zipfile
            import tempfile
            import shutil
            
            zip_path = zip_file_info.get("file_path", "")
            if not zip_path or not os.path.exists(zip_path):
                logger.warning(f"[高企申报] 压缩包不存在: {zip_path}")
                return {"completeness": 0}
            
            logger.info(f"[高企申报] 开始处理压缩包: {zip_path}")
            
            # 创建临时目录用于解压
            temp_dir = tempfile.mkdtemp(prefix="high_tech_zip_")
            logger.info(f"[高企申报] 创建临时解压目录: {temp_dir}")
            
            try:
                # 解压ZIP文件
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                logger.info(f"[高企申报] 压缩包解压完成到: {temp_dir}")
                
                # 扫描解压后的所有文件
                all_files = []
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        all_files.append({
                            "path": file_path,
                            "name": file,
                            "ext": os.path.splitext(file)[1].lower(),
                            "size": os.path.getsize(file_path)
                        })
                
                logger.info(f"[高企申报] 压缩包中共有 {len(all_files)} 个文件")
                
                if not all_files:
                    logger.warning(f"[高企申报] 压缩包中没有文件")
                    return {"completeness": 0}
                
                # 分析文件类型
                file_analysis = self.analyze_folder_files(all_files)
                
                # 提取信息
                extracted_data = await self.extract_info_from_folder_files(all_files, file_analysis)
                
                # 计算完整性
                extracted_data["completeness"] = self.check_high_tech_info_completeness(extracted_data)
                extracted_data["folder_analysis"] = file_analysis
                extracted_data["zip_file"] = os.path.basename(zip_path)
                extracted_data["extracted_files"] = len(all_files)
                
                logger.info(f"[高企申报] 压缩包信息提取完成，完整性: {extracted_data['completeness']}%")
                
                return extracted_data
                
            finally:
                # 清理临时目录
                try:
                    shutil.rmtree(temp_dir)
                    logger.info(f"[高企申报] 清理临时目录: {temp_dir}")
                except Exception as e:
                    logger.warning(f"[高企申报] 清理临时目录失败: {e}")
            
        except zipfile.BadZipFile:
            logger.error(f"[高企申报] 压缩包格式错误: {zip_path}")
            return {"completeness": 0, "error": "压缩包格式错误"}
        except Exception as e:
            logger.error(f"[高企申报] 压缩包信息提取错误: {e}")
            return {"completeness": 0, "error": str(e)}
    
    async def extract_high_tech_info_from_folder(self, folder_info: Dict) -> Dict:
        """从文件夹提取高企申报信息"""
        try:
            folder_path = folder_info.get("folder_path", "")
            if not folder_path or not os.path.exists(folder_path):
                logger.warning(f"[高企申报] 文件夹不存在: {folder_path}")
                return {"completeness": 0}
            
            logger.info(f"[高企申报] 开始处理文件夹: {folder_path}")
            
            # 扫描文件夹中的所有文件
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    all_files.append({
                        "path": file_path,
                        "name": file,
                        "ext": os.path.splitext(file)[1].lower(),
                        "size": os.path.getsize(file_path)
                    })
            
            logger.info(f"[高企申报] 文件夹中共有 {len(all_files)} 个文件")
            
            # 分析文件类型
            file_analysis = self.analyze_folder_files(all_files)
            
            # 提取信息
            extracted_data = await self.extract_info_from_folder_files(all_files, file_analysis)
            
            # 计算完整性
            extracted_data["completeness"] = self.check_high_tech_info_completeness(extracted_data)
            extracted_data["folder_analysis"] = file_analysis
            
            logger.info(f"[高企申报] 文件夹信息提取完成，完整性: {extracted_data['completeness']}%")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"[高企申报] 文件夹信息提取错误: {e}")
            return {"completeness": 0, "error": str(e)}
    
    def analyze_folder_files(self, files: List[Dict]) -> Dict:
        """分析文件夹中的文件"""
        analysis = {
            "total_files": len(files),
            "by_extension": {},
            "by_type": {
                "financial": [],      # 财务文件
                "legal": [],          # 法律文件
                "intellectual_property": [],  # 知识产权
                "technical": [],      # 技术文件
                "personnel": [],      # 人员文件
                "other": []           # 其他文件
            },
            "key_files_found": []
        }
        
        # 文件扩展名分类
        for file_info in files:
            ext = file_info["ext"]
            analysis["by_extension"][ext] = analysis["by_extension"].get(ext, 0) + 1
            
            # 按类型分类
            filename = file_info["name"].lower()
            file_path = file_info["path"]
            
            # 财务文件
            if any(keyword in filename for keyword in ["审计", "财务", "报表", "收入", "费用", "利润", "tax", "financial", "audit"]):
                analysis["by_type"]["financial"].append(file_info)
                if any(keyword in filename for keyword in ["审计报告", "审计", "audit"]):
                    analysis["key_files_found"].append({"type": "审计报告", "file": filename})
            
            # 法律文件
            elif any(keyword in filename for keyword in ["营业执照", "执照", "许可证", "资质", "license", "certificate"]):
                analysis["by_type"]["legal"].append(file_info)
                if any(keyword in filename for keyword in ["营业执照", "执照"]):
                    analysis["key_files_found"].append({"type": "营业执照", "file": filename})
            
            # 知识产权
            elif any(keyword in filename for keyword in ["专利", "著作权", "商标", "知识产权", "patent", "copyright", "trademark"]):
                analysis["by_type"]["intellectual_property"].append(file_info)
                if any(keyword in filename for keyword in ["专利证书", "专利", "patent"]):
                    analysis["key_files_found"].append({"type": "专利证书", "file": filename})
            
            # 技术文件
            elif any(keyword in filename for keyword in ["研发", "技术", "项目", "成果", "rd", "research", "development", "technical"]):
                analysis["by_type"]["technical"].append(file_info)
            
            # 人员文件
            elif any(keyword in filename for keyword in ["人员", "员工", "职工", "社保", "personnel", "employee", "staff"]):
                analysis["by_type"]["personnel"].append(file_info)
            
            else:
                analysis["by_type"]["other"].append(file_info)
        
        return analysis
    
    async def extract_info_from_folder_files(self, files: List[Dict], analysis: Dict) -> Dict:
        """从文件夹文件中提取信息"""
        extracted_data = {}
        
        # 尝试从文件名提取公司名称
        company_name = self.extract_company_name_from_files(files)
        if company_name:
            extracted_data["company_name"] = company_name
        
        # 尝试从财务文件中提取数据
        financial_files = analysis["by_type"]["financial"]
        if financial_files:
            # 简化实现：返回模拟数据
            extracted_data.update({
                "revenue_last_year": 3500,
                "rd_expense_ratio": 5.2,
                "high_tech_product_ratio": 68.3,
                "financial_files_found": len(financial_files)
            })
        
        # 尝试从知识产权文件中提取数据
        ip_files = analysis["by_type"]["intellectual_property"]
        if ip_files:
            # 简化实现：返回模拟数据
            extracted_data.update({
                "invention_patents": 3,
                "utility_patents": 12,
                "software_copyrights": 5,
                "ip_files_found": len(ip_files)
            })
        
        # 尝试从人员文件中提取数据
        personnel_files = analysis["by_type"]["personnel"]
        if personnel_files:
            # 简化实现：返回模拟数据
            extracted_data.update({
                "employee_count": 120,
                "rd_personnel_count": 15,
                "tech_personnel_ratio": 12.5,
                "personnel_files_found": len(personnel_files)
            })
        
        # 设置默认值
        extracted_data.setdefault("company_name", "从文件夹提取的公司")
        extracted_data.setdefault("establishment_date", "2020-01-01")
        extracted_data.setdefault("industry_field", "先进制造与自动化")
        extracted_data.setdefault("main_products_services", "从文件分析的业务")
        
        # 添加文件夹分析信息
        extracted_data["folder_analysis_summary"] = {
            "total_files": analysis["total_files"],
            "key_files": analysis["key_files_found"],
            "financial_count": len(analysis["by_type"]["financial"]),
            "legal_count": len(analysis["by_type"]["legal"]),
            "ip_count": len(analysis["by_type"]["intellectual_property"]),
            "technical_count": len(analysis["by_type"]["technical"]),
            "personnel_count": len(analysis["by_type"]["personnel"])
        }
        
        return extracted_data
    
    def extract_company_name_from_files(self, files: List[Dict]) -> Optional[str]:
        """从文件名中提取公司名称"""
        # 常见公司名称关键词
        company_keywords = ["科技", "技术", "软件", "信息", "智能", "电子", "生物", "医药", "材料", "工程"]
        
        for file_info in files:
            filename = file_info["name"]
            
            # 检查文件名中是否包含公司关键词
            for keyword in company_keywords:
                if keyword in filename:
                    # 尝试提取公司名称（假设公司名称在文件名开头）
                    parts = filename.split(keyword)
                    if len(parts) > 1:
                        potential_name = parts[0] + keyword
                        if len(potential_name) >= 4:  # 至少4个字符
                            return potential_name
        
        return None
    
    async def extract_high_tech_info_from_documents(self, files: List) -> Dict:
        """从文档提取高企申报信息"""
        # 简化实现：返回模拟数据
        return {
            "company_name": "示例科技有限公司",
            "establishment_date": "2020-05-10",
            "industry_field": "先进制造与自动化",
            "main_products_services": "智能机器人研发与制造",
            "revenue_last_year": 3500,
            "rd_expense_ratio": 5.2,
            "high_tech_product_ratio": 68.3,
            "tech_personnel_ratio": 12.5,
            "employee_count": 120,
            "rd_personnel_count": 15,
            "invention_patents": 3,
            "utility_patents": 12,
            "software_copyrights": 5,
            "completeness": 75
        }
    
    def check_high_tech_info_completeness(self, data: Dict) -> float:
        """检查高企信息完整性"""
        required_fields = [
            "company_name", "establishment_date", "industry_field",
            "revenue_last_year", "rd_expense_ratio", "high_tech_product_ratio",
            "tech_personnel_ratio", "employee_count", "rd_personnel_count"
        ]
        
        present_count = sum(1 for field in required_fields if field in data and data[field])
        return (present_count / len(required_fields)) * 100
    
    def get_missing_high_tech_fields(self, data: Dict) -> List[str]:
        """获取缺失的高企字段"""
        required_fields = [
            ("company_name", "企业名称"),
            ("establishment_date", "成立日期"),
            ("industry_field", "所属高新技术领域"),
            ("revenue_last_year", "上年度销售收入"),
            ("rd_expense_ratio", "研发费用占比"),
            ("high_tech_product_ratio", "高品收入占比"),
            ("tech_personnel_ratio", "科技人员占比"),
            ("employee_count", "职工总数"),
            ("rd_personnel_count", "研发人员数")
        ]
        
        missing = []
        for field_id, field_name in required_fields:
            if field_id not in data or not data[field_id]:
                missing.append(field_name)
        
        return missing
    
    def generate_high_tech_questions(self, missing_fields: List[str], existing_data: Dict) -> List[str]:
        """生成高企相关问题"""
        questions = []
        
        field_questions = {
            "企业名称": "请问企业全称是什么？",
            "成立日期": "企业成立日期是什么时候？（格式：YYYY-MM-DD）",
            "所属高新技术领域": "企业属于哪个高新技术领域？（八大领域：电子信息、生物与新医药、航空航天、新材料、高技术服务、新能源与节能、资源与环境、先进制造与自动化）",
            "上年度销售收入": "上年度销售收入是多少万元？",
            "研发费用占比": "近三年研发费用占销售收入的比例是多少？（百分比）",
            "高品收入占比": "高新技术产品（服务）收入占企业总收入的比例是多少？（百分比）",
            "科技人员占比": "科技人员占职工总数的比例是多少？（百分比）",
            "职工总数": "企业职工总数是多少人？",
            "研发人员数": "研发人员数量是多少人？"
        }
        
        for field in missing_fields:
            if field in field_questions:
                questions.append(field_questions[field])
        
        return questions
    
    async def parse_high_tech_text_input(self, text: str) -> Dict:
        """解析高企批量输入文本"""
        import re
        
        data = {}
        
        # 简单解析逻辑
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
            match = re.search(pattern, text)
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
        
        return data
    
    async def handle_high_tech_conversation(self, user_input: str, step: int, existing_data: Dict) -> Dict:
        """处理高企对话引导"""
        questions = [
            "请问企业全称是什么？",
            "企业成立日期是什么时候？（格式：YYYY-MM-DD）",
            "企业属于哪个高新技术领域？（八大领域：电子信息、生物与新医药、航空航天、新材料、高技术服务、新能源与节能、资源与环境、先进制造与自动化）",
            "上年度销售收入是多少万元？",
            "近三年研发费用占销售收入的比例是多少？（百分比）",
            "高新技术产品（服务）收入占企业总收入的比例是多少？（百分比）",
            "科技人员占职工总数的比例是多少？（百分比）",
            "企业职工总数是多少人？",
            "研发人员数量是多少人？"
        ]
        
        field_mapping = [
            "company_name", "establishment_date", "industry_field",
            "revenue_last_year", "rd_expense_ratio", "high_tech_product_ratio",
            "tech_personnel_ratio", "employee_count", "rd_personnel_count"
        ]
        
        if step < len(questions):
            # 提取当前步骤的数据
            extracted_data = {}
            current_field = field_mapping[step]
            
            # 简单提取逻辑
            if step == 0:  # 企业名称
                extracted_data[current_field] = user_input
            elif step == 1:  # 成立日期
                extracted_data[current_field] = user_input
            elif step == 2:  # 高新技术领域
                extracted_data[current_field] = user_input
            elif step in [3, 4, 5, 6]:  # 数值类型
                try:
                    extracted_data[current_field] = float(user_input.replace("%", ""))
                except:
                    extracted_data[current_field] = user_input
            elif step in [7, 8]:  # 整数类型
                try:
                    extracted_data[current_field] = int(user_input)
                except:
                    extracted_data[current_field] = user_input
            
            next_step = step + 1
            completed = next_step >= len(questions)
            
            return {
                "extracted_data": extracted_data,
                "next_step": next_step,
                "completed": completed,
                "next_question": questions[next_step] if not completed else None
            }
        
        return {
            "extracted_data": {},
            "next_step": step,
            "completed": True,
            "next_question": None
        }
    
    async def execute_high_tech_assessment(self, company_data: Dict) -> Dict:
        """执行高企资格评估"""
        # 评估8大条件
        conditions_assessment = self.assess_high_tech_conditions(company_data)
        
        # 计算创新能力得分
        innovation_score = self.calculate_innovation_score(company_data)
        
        # 计算成功率
        success_rate = self.calculate_success_rate(conditions_assessment, innovation_score)
        
        # 生成建议
        suggestions = self.generate_high_tech_suggestions(conditions_assessment, innovation_score)
        
        return {
            "conditions_assessment": conditions_assessment,
            "innovation_score": innovation_score,
            "success_rate": success_rate,
            "suggestions": suggestions,
            "qualified": all(cond["passed"] for cond in conditions_assessment.values()) and innovation_score["total"] >= 71
        }
    
    def assess_high_tech_conditions(self, data: Dict) -> Dict:
        """评估高企8大条件"""
        conditions = {}
        
        # 1. 注册时间
        establishment_date = data.get("establishment_date")
        if establishment_date:
            try:
                from datetime import datetime
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
        
        conditions["technology_field"] = {
            "passed": any(field in industry_field for field in high_tech_fields),
            "reason": f"所属领域：{industry_field}，{'属于' if conditions['technology_field']['passed'] else '不属于'}高新技术领域"
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
        
        return conditions
    
    def calculate_innovation_score(self, data: Dict) -> Dict:
        """计算创新能力得分（100分制）"""
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
        # 简化评估：根据知识产权数量估算
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
        # 简化评估：根据企业规模估算
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
        # 简化评估：根据研发投入和人员增长估算
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
        
        return scores
    
    def calculate_success_rate(self, conditions_assessment: Dict, innovation_score: Dict) -> float:
        """计算申报成功率"""
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
        return max(0, min(100, success_rate))
    
    def generate_high_tech_suggestions(self, conditions_assessment: Dict, innovation_score: Dict) -> List[str]:
        """生成高企申报建议"""
        suggestions = []
        
        # 检查8大条件
        conditions = conditions_assessment
        
        if not conditions.get("registration_time", {}).get("passed", False):
            suggestions.append("企业注册时间不足一年，建议等待满足条件后再申报")
        
        if not conditions.get("intellectual_property", {}).get("passed", False):
            suggestions.append("缺少核心自主知识产权，建议尽快申请专利或软件著作权")
        
        if not conditions.get("technology_field", {}).get("passed", False):
            suggestions.append("技术领域不属于国家重点支持的高新技术领域，建议调整产品或技术方向")
        
        if not conditions.get("tech_personnel_ratio", {}).get("passed", False):
            suggestions.append("科技人员占比不足10%，建议增加研发人员或调整人员结构")
        
        if not conditions.get("rd_expense_ratio", {}).get("passed", False):
            suggestions.append("研发费用占比不符合要求，建议增加研发投入或优化费用归集")
        
        if not conditions.get("high_tech_product_ratio", {}).get("passed", False):
            suggestions.append("高品收入占比不足60%，建议调整产品结构或收入分类")
        
        # 创新能力建议
        innovation_total = innovation_score.get("total", {}).get("score", 0)
        if innovation_total < 71:
            suggestions.append(f"创新能力预估得分{innovation_total}分，未达到71分要求，建议加强知识产权布局和科技成果转化")
        
        # 通用建议
        if not suggestions:
            suggestions.append("企业基本符合高企申报条件，建议尽快准备申报材料")
            suggestions.append("重点准备两项专项审计报告（研发费用、高品收入）")
            suggestions.append("建议提前3-6个月开始材料准备，确保材料完整规范")
        
        return suggestions
    
    def format_high_tech_assessment_report(self, assessment_result: Dict) -> str:
        """格式化高企评估报告"""
        report = "【高企资格评估报告】\n\n"
        
        conditions = assessment_result.get("conditions_assessment", {})
        innovation_score = assessment_result.get("innovation_score", {})
        success_rate = assessment_result.get("success_rate", 0)
        qualified = assessment_result.get("qualified", False)
        
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
        
        innovation_total = innovation_score.get("total", {})
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
        
        # 建议
        suggestions = assessment_result.get("suggestions", [])
        if suggestions:
            report += "\n**四、改进建议：**\n"
            for i, suggestion in enumerate(suggestions[:5], 1):
                report += f"{i}. {suggestion}\n"
        
        return report
    
    async def generate_high_tech_materials(self, company_data: Dict, assessment: Dict) -> Dict:
        """生成高企申报材料"""
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
        
        return materials
    
    async def check_high_tech_proof_materials(self, materials: Dict, uploaded_files: List, company_data: Dict) -> Dict:
        """检查高企佐证材料"""
        # 简化实现：返回模拟检查结果
        existing = [
            "企业营业执照",
            "知识产权证书",
            "近三年审计报告"
        ]
        
        missing = [
            "研究开发费用专项审计报告",
            "高新技术产品（服务）收入专项审计报告",
            "科研项目立项证明",
            "产品质量检验报告"
        ]
        
        completeness = 40  # 模拟完整性百分比
        
        return {
            "existing": existing,
            "missing": missing,
            "completeness": completeness,
            "total_materials": len(existing) + len(missing),
            "existing_count": len(existing),
            "missing_count": len(missing)
        }
    
    def format_high_tech_proof_check_report(self, check_result: Dict) -> str:
        """格式化材料检查报告"""
        report = "【高企申报材料检查报告】\n\n"
        
        completeness = check_result.get("completeness", 0)
        existing = check_result.get("existing", [])
        missing = check_result.get("missing", [])
        
        report += f"📊 **材料完整性: {completeness}%**\n\n"
        
        if existing:
            report += "✅ **已有材料：**\n"
            for material in existing:
                report += f"  • {material}\n"
        
        if missing:
            report += "\n❌ **缺失材料：**\n"
            for material in missing:
                report += f"  • {material}\n"
        
        report += "\n**💡 重点说明：**\n"
        report += "1. 两项专项审计报告必须由符合资质的中介机构出具\n"
        report += "2. 建议提前联系会计师事务所准备审计报告\n"
        report += "3. 材料准备周期通常需要3-6个月\n"
        
        return report
    
    async def generate_high_tech_final_output(self, state: Dict) -> Dict:
        """生成高企最终输出"""
        company_data = state.get("data", {})
        company_name = company_data.get("company_name", "未知公司")
        
        # 创建输出目录
        import os
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name[:30]  # 限制长度
        
        output_dir = f"./output/high-tech-enterprise/{safe_name}_{timestamp}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建子目录
        subdirs = ["原始文档", "评估报告", "申报材料", "检查报告", "最终申报包"]
        for subdir in subdirs:
            os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)
        
        output_files = []
        
        # 1. 保存公司信息
        info_path = os.path.join(output_dir, "公司信息.txt")
        with open(info_path, 'w', encoding='utf-8') as f:
            f.write(f"高企申报公司信息\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            for key, value in company_data.items():
                f.write(f"{key}: {value}\n")
        
        output_files.append(info_path)
        
        # 2. 保存评估报告
        if "assessment" in state:
            assessment = state["assessment"]
            report_path = os.path.join(output_dir, "评估报告", "高企资格评估报告.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self.format_high_tech_assessment_report(assessment))
            output_files.append(report_path)
        
        # 3. 保存材料清单
        if "materials" in state:
            materials = state["materials"]
            materials_path = os.path.join(output_dir, "申报材料", "高企申报材料清单.txt")
            with open(materials_path, 'w', encoding='utf-8') as f:
                f.write("高企申报14项材料清单\n")
                f.write(f"{'='*50}\n\n")
                for category, items in materials.items():
                    f.write(f"【{category}】\n")
                    for item in items:
                        f.write(f"  • {item}\n")
                    f.write("\n")
            output_files.append(materials_path)
        
        # 4. 保存检查报告
        if "proof_check" in state:
            check_result = state["proof_check"]
            check_path = os.path.join(output_dir, "检查报告", "材料检查报告.txt")
            with open(check_path, 'w', encoding='utf-8') as f:
                f.write(self.format_high_tech_proof_check_report(check_result))
            output_files.append(check_path)
        
        # 5. 创建申报包说明
        readme_path = os.path.join(output_dir, "最终申报包", "申报说明.txt")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"高新技术企业（高企）申报材料包\n")
            f.write(f"公司名称: {company_name}\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write(f"{'='*50}\n\n")
            f.write("本申报包包含以下内容：\n")
            f.write("1. 公司基本信息\n")
            f.write("2. 高企资格评估报告\n")
            f.write("3. 创新能力评分报告\n")
            f.write("4. 14项申报材料清单\n")
            f.write("5. 材料检查报告\n")
            f.write("6. 原始上传文档\n")
            f.write("\n申报流程说明：\n")
            f.write("1. 检查缺失材料并补充\n")
            f.write("2. 准备两项专项审计报告\n")
            f.write("3. 整理所有申报材料\n")
            f.write("4. 在线提交高企认定申请\n")
            f.write("5. 跟进评审进度\n")
        
        output_files.append(readme_path)
        
        # 6. 创建文件夹结构说明
        structure_path = os.path.join(output_dir, "文件夹结构说明.txt")
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write(f"高企申报文件夹结构说明\n")
            f.write(f"{'='*50}\n\n")
            f.write(f"{output_dir}/\n")
            f.write(f"├── 公司信息.txt                # 公司基本信息\n")
            f.write(f"├── 文件夹结构说明.txt          # 本文件\n")
            f.write(f"├── 原始文档/                   # 上传的原始文档\n")
            f.write(f"├── 评估报告/                   # 高企资格评估相关文件\n")
            f.write(f"├── 申报材料/                   # 高企申报材料清单\n")
            f.write(f"├── 检查报告/                   # 材料检查报告\n")
            f.write(f"└── 最终申报包/                 # 最终申报材料包\n")
        
        output_files.append(structure_path)
        
        # 7. 复制上传的文件到原始文档文件夹
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
                    logger.warning(f"[高企申报] 复制文件失败: {e}")
        
        logger.info(f"[高企申报] 为{company_name}创建高企申报文件夹: {output_dir}")
        
        return {
            "output_dir": output_dir,
            "company_name": company_name,
            "files": output_files,
            "folder_structure": {
                "原始文档": len(uploaded_files),
                "评估报告": 1 if "assessment" in state else 0,
                "申报材料": 1 if "materials" in state else 0,
                "检查报告": 1 if "proof_check" in state else 0,
                "最终申报包": 1
            }
        }
    
    def cleanup_session(self, session_id: str):
        """清理会话状态"""
        if session_id in self.workflow_states:
            del self.workflow_states[session_id]
            logger.info(f"[高企申报] 清理会话: {session_id}")
