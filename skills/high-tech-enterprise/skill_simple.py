"""
高新技术企业（高企）申报技能 - 简化版本
专注于高企申报核心功能
"""

import os
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from common.log import logger
from agent.skills.types import Skill, SkillContext, SkillResult


class HighTechEnterpriseSkillSimple(Skill):
    """高新技术企业（高企）申报技能 - 简化版本"""
    
    def __init__(self):
        super().__init__()
        self.name = "高企申报助手"
        self.description = "专注于高新技术企业申报的智能助手，基于国家高企认定管理办法"
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
            trigger_keywords = ["高企", "高新技术企业", "高企申报", "高企认定"]
            if any(keyword in user_input for keyword in trigger_keywords):
                return await self.start_high_tech_flow(context, session_id)
            
            # 检查是否在工作流中
            if session_id in self.workflow_states:
                return await self.continue_workflow(context, session_id)
            
            # 默认回复
            return SkillResult(
                success=True,
                content="我是高企申报助手。请输入'高企申报'开始申报流程。",
                metadata={"action": "greeting"}
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 技能执行错误: {e}")
            return SkillResult(
                success=False,
                content=f"抱歉，处理过程中出现错误: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def start_high_tech_flow(self, context: SkillContext, session_id: str) -> SkillResult:
        """开始高企申报流程"""
        # 初始化工作流状态
        self.workflow_states[session_id] = {
            "step": "welcome",
            "data": {},
            "start_time": datetime.now().isoformat(),
            "files": context.get("files", [])
        }
        
        welcome_msg = """🏭 **高新技术企业（高企）申报助手**

我将帮助您完成高企申报全流程。根据国家《高新技术企业认定管理办法》，申报需要同时满足8大条件：

**高企申报8大条件：**
1. ✅ 企业注册成立一年（365天）以上
2. ✅ 拥有核心自主知识产权
3. ✅ 技术属于国家重点支持的高新技术领域
4. ✅ 科技人员占比不低于10%
5. ✅ 研发费用占比符合要求（根据收入不同为3-5%）
6. ✅ 高品收入占比不低于60%
7. ✅ 创新能力评价71分以上（满分100分）
8. ✅ 申请前一年内未发生重大安全、质量事故

**请提供企业基本信息，我将为您评估是否符合高企申报条件：**

请按以下格式提供信息（可复制修改）：
```
企业名称：XXX科技有限公司
成立时间：2020年5月10日
所属领域：先进制造与自动化
上年度收入：3500万元
研发费用占比：5.2%
高品收入占比：68.3%
科技人员占比：12.5%
职工总数：120人
研发人员数：15人
发明专利：3项
实用新型专利：12项
```

**请提供以上信息开始评估：**"""
        
        return SkillResult(
            success=True,
            content=welcome_msg,
            metadata={
                "action": "start_high_tech",
                "session_id": session_id,
                "step": "welcome"
            }
        )
    
    async def continue_workflow(self, context: SkillContext, session_id: str) -> SkillResult:
        """继续工作流"""
        state = self.workflow_states[session_id]
        current_step = state["step"]
        user_input = context.get("query", "").strip()
        
        if current_step == "welcome":
            return await self.process_company_info(state, user_input, session_id)
        elif current_step == "assessment":
            return await self.provide_assessment_result(state, user_input, session_id)
        elif current_step == "materials":
            return await self.provide_materials_list(state, user_input, session_id)
        else:
            return SkillResult(
                success=False,
                content="工作流状态异常，请重新开始。",
                metadata={"error": "invalid_step"}
            )
    
    async def process_company_info(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """处理企业信息"""
        try:
            # 解析用户输入
            company_data = self.parse_company_info(user_input)
            state["data"] = company_data
            state["step"] = "assessment"
            
            # 执行评估
            assessment = self.assess_high_tech_conditions(company_data)
            state["assessment"] = assessment
            
            # 生成评估报告
            report = self.generate_assessment_report(assessment, company_data)
            
            msg = f"**高企资格评估完成！**\n\n{report}\n\n"
            msg += "**下一步：**\n"
            msg += "回复'材料清单'查看高企申报14项材料清单\n"
            msg += "回复'重新评估'修改企业信息\n"
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={
                    "action": "assessment_complete",
                    "session_id": session_id,
                    "qualified": assessment["qualified"]
                }
            )
            
        except Exception as e:
            logger.error(f"[高企申报] 信息处理错误: {e}")
            return SkillResult(
                success=False,
                content=f"信息处理出错，请按格式提供信息。错误: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def provide_assessment_result(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """提供评估结果"""
        if "材料清单" in user_input or "材料" in user_input:
            state["step"] = "materials"
            materials_list = self.generate_materials_list()
            
            msg = "**高企申报14项材料清单：**\n\n"
            msg += materials_list
            msg += "\n**说明：**\n"
            msg += "1. 带✅的为必需材料\n"
            msg += "2. 两项专项审计报告必须由符合资质的中介机构出具\n"
            msg += "3. 建议提前3-6个月开始准备材料\n"
            
            self.workflow_states[session_id] = state
            
            return SkillResult(
                success=True,
                content=msg,
                metadata={"action": "materials_list", "session_id": session_id}
            )
        elif "重新评估" in user_input or "修改" in user_input:
            state["step"] = "welcome"
            self.workflow_states[session_id] = state
            
            return await self.start_high_tech_flow({"session_id": session_id}, session_id)
        else:
            return SkillResult(
                success=True,
                content="请回复'材料清单'查看申报材料，或'重新评估'修改信息。",
                metadata={"action": "prompt_next", "session_id": session_id}
            )
    
    async def provide_materials_list(self, state: Dict, user_input: str, session_id: str) -> SkillResult:
        """提供材料清单"""
        if "重新评估" in user_input or "修改" in user_input:
            state["step"] = "welcome"
            self.workflow_states[session_id] = state
            
            return await self.start_high_tech_flow({"session_id": session_id}, session_id)
        else:
            return SkillResult(
                success=True,
                content="高企申报流程完成！如需重新评估请回复'重新评估'。",
                metadata={"action": "complete", "session_id": session_id}
            )
    
    def parse_company_info(self, text: str) -> Dict:
        """解析企业信息"""
        import re
        
        data = {}
        
        patterns = {
            "company_name": r"企业名称[:：]\s*(.+)",
            "establishment_date": r"成立时间[:：]\s*(.+)",
            "industry_field": r"所属领域[:：]\s*(.+)",
            "revenue_last_year": r"上年度收入[:：]\s*([\d.]+)",
            "rd_expense_ratio": r"研发费用占比[:：]\s*([\d.]+)",
            "high_tech_product_ratio": r"高品收入占比[:：]\s*([\d.]+)",
            "tech_personnel_ratio": r"科技人员占比[:：]\s*([\d.]+)",
            "employee_count": r"职工总数[:：]\s*(\d+)",
            "rd_personnel_count": r"研发人员数[:：]\s*(\d+)",
            "invention_patents": r"发明专利[:：]\s*(\d+)",
            "utility_patents": r"实用新型专利[:：]\s*(\d+)"
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
                        data[field] = 0
                elif field in ["employee_count", "rd_personnel_count", "invention_patents", "utility_patents"]:
                    try:
                        data[field] = int(value)
                    except:
                        data[field] = 0
                else:
                    data[field] = value
        
        # 设置默认值
        data.setdefault("company_name", "未知企业")
        data.setdefault("establishment_date", "2020-01-01")
        data.setdefault("industry_field", "未知领域")
        data.setdefault("revenue_last_year", 0)
        data.setdefault("rd_expense_ratio", 0)
        data.setdefault("high_tech_product_ratio", 0)
        data.setdefault("tech_personnel_ratio", 0)
        data.setdefault("employee_count", 0)
        data.setdefault("rd_personnel_count", 0)
        data.setdefault("invention_patents", 0)
        data.setdefault("utility_patents", 0)
        
        return data
    
    def assess_high_tech_conditions(self, data: Dict) -> Dict:
        """评估高企8大条件"""
        conditions = {}
        
        # 1. 注册时间
        try:
            from datetime import datetime
            establish_date = datetime.strptime(data["establishment_date"], "%Y年%m月%d日")
            days_since = (datetime.now() - establish_date).days
            conditions["registration"] = {
                "passed": days_since >= 365,
                "score": 100 if days_since >= 365 else 0,
                "reason": f"成立{days_since}天，{'符合' if days_since >= 365 else '不符合'}一年以上要求"
            }
        except:
            conditions["registration"] = {
                "passed": False,
                "score": 0,
                "reason": "成立日期格式错误，请使用'YYYY年MM月DD日'格式"
            }
        
        # 2. 知识产权
        total_ip = data["invention_patents"] + data["utility_patents"]
        conditions["ip"] = {
            "passed": total_ip > 0,
            "score": min(100, total_ip * 20),  # 每项知识产权20分，最高100分
            "reason": f"拥有{total_ip}项知识产权（发明专利{data['invention_patents']}项，实用新型{data['utility_patents']}项）"
        }
        
        # 3. 技术领域
        high_tech_fields = ["电子信息", "生物与新医药", "航空航天", "新材料", "高技术服务", "新能源与节能", "资源与环境", "先进制造与自动化"]
        field_match = any(field in data["industry_field"] for field in high_tech_fields)
        conditions["field"] = {
            "passed": field_match,
            "score": 100 if field_match else 0,
            "reason": f"所属领域：{data['industry_field']}，{'属于' if field_match else '不属于'}高新技术领域"
        }
        
        # 4. 科技人员占比
        tech_ratio = data["tech_personnel_ratio"]
        conditions["tech_ratio"] = {
            "passed": tech_ratio >= 10,
            "score": min(100, tech_ratio * 10),  # 每1%得10分，最高100分
            "reason": f"科技人员占比{tech_ratio}%，{'符合' if tech_ratio >= 10 else '不符合'}≥10%要求"
        }
        
        # 5. 研发费用占比
        rd_ratio = data["rd_expense_ratio"]
        revenue = data["revenue_last_year"]
        
        # 根据收入确定要求
        if revenue < 5000:
            required_ratio = 5
        elif revenue < 20000:
            required_ratio = 4
        else:
            required_ratio = 3
        
        conditions["rd_ratio"] = {
            "passed": rd_ratio >= required_ratio,
            "score": min(100, (rd_ratio / required_ratio) * 100),
            "reason": f"研发费用占比{rd_ratio}%，收入{revenue}万元要求{required_ratio}%，{'符合' if rd_ratio >= required_ratio else '不符合'}"
        }
        
        # 6. 高品收入占比
        high_tech_ratio = data["high_tech_product_ratio"]
        conditions["high_tech_ratio"] = {
            "passed": high_tech_ratio >= 60,
            "score": min(100, high_tech_ratio * 1.67),  # 60%得100分
            "reason": f"高品收入占比{high_tech_ratio}%，{'符合' if high_tech_ratio >= 60 else '不符合'}≥60%要求"
        }
        
        # 7. 创新能力（简化评估）
        innovation_score = self.calculate_innovation_score(data)
        conditions["innovation"] = {
            "passed": innovation_score >= 71,
            "score": innovation_score,
            "reason": f"创新能力预估得分{innovation_score}分，{'符合' if innovation_score >= 71 else '不符合'}≥71分要求"
        }
        
        # 8. 安全环保（默认通过）
        conditions["safety"] = {
            "passed": True,
            "score": 100,
            "reason": "需企业确认申请前一年内未发生重大安全、质量事故"
        }
        
        # 总体评估
        passed_count = sum(1 for cond in conditions.values() if cond["passed"])
        total_score = sum(cond["score"] for cond in conditions.values()) / len(conditions)
        
        conditions["overall"] = {
            "passed": passed_count >= 7 and conditions["innovation"]["passed"],  # 至少7项通过且创新能力通过
            "score": total_score,
            "reason": f"{passed_count}/8项条件通过，综合得分{total_score:.1f}分"
        }
        
        return {
            "conditions": conditions,
            "qualified": conditions["overall"]["passed"],
            "passed_count": passed_count,
            "total_score": total_score
        }
    
    def calculate_innovation_score(self, data: Dict) -> float:
        """计算创新能力得分（简化版）"""
        score = 0
        
        # 1. 知识产权得分（30分）
        invention_score = min(15, data["invention_patents"] * 5)  # 每项发明专利5分，最高15分
        utility_score = min(15, data["utility_patents"] * 1.5)   # 每项实用新型1.5分，最高15分
        score += invention_score + utility_score
        
        # 2. 研发投入得分（20分）
        rd_ratio = data["rd_expense_ratio"]
        if rd_ratio >= 8:
            score += 20
        elif rd_ratio >= 6:
            score += 15
        elif rd_ratio >= 4:
            score += 10
        elif rd_ratio >= 3:
            score += 5
        
        # 3. 科技人员得分（20分）
        tech_ratio = data["tech_personnel_ratio"]
        if tech_ratio >= 20:
            score += 20
        elif tech_ratio >= 15:
            score += 15
        elif tech_ratio >= 10:
            score += 10
        elif tech_ratio >= 5:
            score += 5
        
        # 4. 成长性得分（30分）- 简化评估
        score += 20