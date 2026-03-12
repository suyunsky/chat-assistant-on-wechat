"""
佐证材料检查模块
检查材料完整性，生成缺失清单
"""

import os
import re
from typing import Dict, Any, List, Tuple
from datetime import datetime

from common.log import logger


class ProofChecker:
    """佐证材料检查器"""
    
    def __init__(self):
        # 必需材料清单
        self.required_materials = [
            {
                "name": "企业营业执照",
                "description": "营业执照复印件加盖公章",
                "keywords": ["营业执照", "business license", "工商执照"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "2021-2023年年度审计报告",
                "description": "已赋码电子原件",
                "keywords": ["审计报告", "audit report", "财务审计", "年度审计"],
                "file_extensions": [".pdf"]
            },
            {
                "name": "2021-2023年12月底缴纳社保人数证明",
                "description": "社保部门出具",
                "keywords": ["社保", "social security", "社会保险", "缴纳证明"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "I类知识产权清单",
                "description": "包括授权号、名称等",
                "keywords": ["专利", "patent", "知识产权", "发明专利", "实用新型"],
                "file_extensions": [".pdf", ".doc", ".docx", ".xlsx"]
            },
            {
                "name": "研发机构证明",
                "description": "认定文件或证书",
                "keywords": ["研发机构", "技术中心", "工程中心", "实验室", "研发中心"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "管理体系认证证书",
                "description": "ISO9001等",
                "keywords": ["ISO9001", "质量管理体系", "管理体系", "认证证书"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "信息化系统证明",
                "description": "系统截图或协议",
                "keywords": ["ERP", "CRM", "OA", "信息化", "系统", "软件"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png", ".doc", ".docx"]
            },
            {
                "name": "自主品牌证明材料",
                "description": "商标注册证",
                "keywords": ["商标", "trademark", "品牌", "注册证"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "国家企业信用信息公示系统截图",
                "description": "网站截图",
                "keywords": ["信用信息", "公示系统", "企业信用"],
                "file_extensions": [".jpg", ".jpeg", ".png", ".pdf"]
            },
            {
                "name": "信用中国查询截图",
                "description": "网站截图",
                "keywords": ["信用中国", "信用查询"],
                "file_extensions": [".jpg", ".jpeg", ".png", ".pdf"]
            },
            {
                "name": "真实性申明",
                "description": "加盖公章",
                "keywords": ["真实性", "申明", "声明", "承诺书"],
                "file_extensions": [".pdf", ".doc", ".docx"]
            }
        ]
        
        # 建议材料清单
        self.suggested_materials = [
            {
                "name": "产品认证证书",
                "description": "UL、CE等",
                "keywords": ["UL", "CE", "产品认证", "认证证书"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "国家级科技奖励证书",
                "description": "如有则提供",
                "keywords": ["科技奖励", "科技进步奖", "创新奖", "奖励证书"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            },
            {
                "name": "创客中国大赛获奖证明",
                "description": "如有则提供",
                "keywords": ["创客中国", "大赛", "获奖", "证明"],
                "file_extensions": [".pdf", ".jpg", ".jpeg", ".png"]
            }
        ]
        
        logger.info("[专精特新] 材料检查器初始化完成")
    
    async def execute(self, materials: Dict[str, Any], uploaded_files: List, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行材料检查"""
        try:
            logger.info("[专精特新] 开始检查佐证材料")
            
            # 分析已上传文件
            file_analysis = self._analyze_uploaded_files(uploaded_files)
            
            # 检查材料完整性
            completeness_result = self._check_completeness(file_analysis)
            
            # 生成缺失清单
            missing_list = self._generate_missing_list(completeness_result)
            
            # 生成检查报告
            check_report = self._generate_check_report(completeness_result, missing_list, company_data)
            
            result = {
                "completeness": completeness_result["completeness_percentage"],
                "existing": completeness_result["existing_materials"],
                "missing": missing_list,
                "file_analysis": file_analysis,
                "report": check_report,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"[专精特新] 材料检查完成，完整性: {result['completeness']}%")
            return result
            
        except Exception as e:
            logger.error(f"[专精特新] 材料检查错误: {e}")
            return {
                "completeness": 0,
                "existing": [],
                "missing": self.required_materials,
                "error": str(e),
                "report": f"材料检查过程中出现错误: {str(e)}"
            }
    
    def _analyze_uploaded_files(self, uploaded_files: List) -> Dict[str, Any]:
        """分析已上传文件"""
        analysis = {
            "total_files": len(uploaded_files),
            "matched_materials": [],
            "unmatched_files": [],
            "file_details": []
        }
        
        for file_info in uploaded_files:
            try:
                file_path = file_info.get("path", "")
                file_name = file_info.get("filename", "")
                file_size = file_info.get("size", 0)
                
                if not os.path.exists(file_path):
                    logger.warning(f"[专精特新] 文件不存在: {file_path}")
                    continue
                
                # 获取文件扩展名
                file_ext = os.path.splitext(file_name)[1].lower()
                
                # 分析文件内容（简化版本：只分析文件名）
                matched_materials = self._match_file_to_materials(file_name, file_ext)
                
                file_detail = {
                    "filename": file_name,
                    "path": file_path,
                    "size": file_size,
                    "extension": file_ext,
                    "matched_materials": matched_materials
                }
                
                analysis["file_details"].append(file_detail)
                
                if matched_materials:
                    analysis["matched_materials"].extend(matched_materials)
                else:
                    analysis["unmatched_files"].append(file_name)
                    
            except Exception as e:
                logger.error(f"[专精特新] 分析文件 {file_info.get('filename')} 时出错: {e}")
        
        # 去重
        analysis["matched_materials"] = list(set(analysis["matched_materials"]))
        
        return analysis
    
    def _match_file_to_materials(self, file_name: str, file_ext: str) -> List[str]:
        """将文件匹配到材料类型"""
        matched = []
        
        # 检查所有必需材料
        for material in self.required_materials:
            # 检查文件扩展名
            if file_ext not in material["file_extensions"]:
                continue
            
            # 检查关键词
            for keyword in material["keywords"]:
                if keyword.lower() in file_name.lower():
                    matched.append(material["name"])
                    break
        
        # 检查建议材料
        for material in self.suggested_materials:
            if file_ext not in material["file_extensions"]:
                continue
            
            for keyword in material["keywords"]:
                if keyword.lower() in file_name.lower():
                    matched.append(material["name"])
                    break
        
        return matched
    
    def _check_completeness(self, file_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """检查材料完整性"""
        matched_materials = file_analysis.get("matched_materials", [])
        
        # 统计必需材料
        required_material_names = [m["name"] for m in self.required_materials]
        existing_required = []
        missing_required = []
        
        for material_name in required_material_names:
            if material_name in matched_materials:
                existing_required.append(material_name)
            else:
                missing_required.append(material_name)
        
        # 统计建议材料
        suggested_material_names = [m["name"] for m in self.suggested_materials]
        existing_suggested = []
        missing_suggested = []
        
        for material_name in suggested_material_names:
            if material_name in matched_materials:
                existing_suggested.append(material_name)
            else:
                missing_suggested.append(material_name)
        
        # 计算完整性百分比
        total_required = len(required_material_names)
        existing_count = len(existing_required)
        
        if total_required > 0:
            completeness_percentage = (existing_count / total_required) * 100
        else:
            completeness_percentage = 0
        
        return {
            "completeness_percentage": round(completeness_percentage, 1),
            "existing_materials": existing_required + existing_suggested,
            "missing_required": missing_required,
            "missing_suggested": missing_suggested,
            "total_required": total_required,
            "existing_required_count": existing_count
        }
    
    def _generate_missing_list(self, completeness_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成缺失材料清单"""
        missing_list = []
        
        # 必需材料
        for material_name in completeness_result.get("missing_required", []):
            # 查找材料详情
            material_detail = None
            for material in self.required_materials:
                if material["name"] == material_name:
                    material_detail = material
                    break
            
            if material_detail:
                missing_list.append({
                    "category": "必需",
                    "name": material_detail["name"],
                    "description": material_detail["description"],
                    "priority": "高"
                })
        
        # 建议材料
        for material_name in completeness_result.get("missing_suggested", []):
            # 查找材料详情
            material_detail = None
            for material in self.suggested_materials:
                if material["name"] == material_name:
                    material_detail = material
                    break
            
            if material_detail:
                missing_list.append({
                    "category": "建议",
                    "name": material_detail["name"],
                    "description": material_detail["description"],
                    "priority": "中"
                })
        
        return missing_list
    
    def _generate_check_report(self, completeness_result: Dict[str, Any], 
                              missing_list: List[Dict[str, str]], 
                              company_data: Dict[str, Any]) -> str:
        """生成检查报告"""
        report = "【佐证材料完整性检查报告】\n\n"
        
        company_name = company_data.get("company_name", "该企业")
        completeness = completeness_result.get("completeness_percentage", 0)
        
        report += f"企业名称：{company_name}\n"
        report += f"检查时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n"
        report += f"材料完整性：{completeness}%\n\n"
        
        # 总体评价
        if completeness >= 90:
            report += "✅ 总体评价：材料基本齐全，符合申报要求\n\n"
        elif completeness >= 70:
            report += "⚠️ 总体评价：材料基本满足要求，建议补充部分材料\n\n"
        elif completeness >= 50:
            report += "⚠️ 总体评价：材料存在较多缺失，需要补充\n\n"
        else:
            report += "❌ 总体评价：材料严重不足，需要大量补充\n\n"
        
        # 已有材料
        existing_materials = completeness_result.get("existing_materials", [])
        if existing_materials:
            report += "【已有材料】\n"
            for i, material in enumerate(existing_materials, 1):
                report += f"{i}. {material}\n"
            report += "\n"
        
        # 缺失材料
        if missing_list:
            report += "【缺失材料】\n"
            
            # 按优先级分组
            high_priority = [m for m in missing_list if m["priority"] == "高"]
            medium_priority = [m for m in missing_list if m["priority"] == "中"]
            
            if high_priority:
                report += "必需材料（高优先级）：\n"
                for i, material in enumerate(high_priority, 1):
                    report += f"{i}. {material['name']} - {material['description']}\n"
                report += "\n"
            
            if medium_priority:
                report += "建议材料（中优先级）：\n"
                for i, material in enumerate(medium_priority, 1):
                    report += f"{i}. {material['name']} - {material['description']}\n"
                report += "\n"
        
        # 文件分析摘要
        total_required = completeness_result.get("total_required", 0)
        existing_count = completeness_result.get("existing_required_count", 0)
        
        report += "【统计摘要】\n"
        report += f"必需材料总数：{total_required}项\n"
        report += f"已提供材料：{existing_count}项\n"
        report += f"缺失材料：{total_required - existing_count}项\n"
        report += f"材料完整性：{completeness}%\n\n"
        
        # 建议
        report += "【建议与说明】\n"
        
        if completeness >= 90:
            report += "1. 材料基本齐全，可以开始准备申报\n"
            report += "2. 建议补充建议材料以增加申报成功率\n"
            report += "3. 确保所有材料清晰、完整、有效\n"
        elif completeness >= 70:
            report += "1. 需要补充必需材料中的缺失项\n"
            report += "2. 建议在申报前完成所有必需材料的准备\n"
            report += "3. 可以同时准备建议材料\n"
        elif completeness >= 50:
            report += "1. 材料缺失较多，需要重点补充\n"
            report += "2. 建议制定材料补充计划\n"
            report += "3. 可以分阶段准备，先完成必需材料\n"
        else:
            report += "1. 材料严重不足，需要系统性地准备\n"
            report += "2. 建议制定详细的材料准备计划\n"
            report += "3. 可以寻求专业机构的帮助\n"
        
        # 材料准备说明
        report += "\n【材料准备说明】\n"
        report += "1. 所有材料需提供清晰扫描件或照片\n"
        report += "2. 文件命名建议：材料类型_企业简称_日期\n"
        report += "3. 文件格式：PDF、JPG、PNG等常用格式\n"
        report += "4. 文件大小：单个文件不超过10MB\n"
        report += "5. 所有复印件需加盖企业公章\n"
        
        return report
    
    def get_material_preparation_guide(self, material_name: str) -> Dict[str, Any]:
        """获取材料准备指南"""
        # 查找材料详情
        material_detail = None
        for material in self.required_materials + self.suggested_materials:
            if material["name"] == material_name:
                material_detail = material
                break
        
        if not material_detail:
            return {"error": f"未找到材料 '{material_name}' 的详细信息"}
        
        # 根据材料类型提供具体指南
        guides = {
            "企业营业执照": {
                "准备要求": "1. 提供最新版营业执照复印件\n2. 复印件需加盖企业公章\n3. 确保信息清晰可辨\n4. 扫描分辨率不低于300dpi",
                "获取方式": "企业注册地市场监督管理局",
                "注意事项": "确保营业执照在有效期内，经营范围包含申报业务",
                "模板": "无固定模板，使用标准营业执照"
            },
            "2021-2023年年度审计报告": {
                "准备要求": "1. 提供经会计师事务所审计的年度报告\n2. 报告需包含资产负债表、利润表、现金流量表\n3. 报告需有注册会计师签字和事务所盖章\n4. 提供已赋码电子原件",
                "获取方式": "委托会计师事务所进行年度审计",
                "注意事项": "确保审计报告连续三年，数据真实准确",
                "模板": "遵循《中国注册会计师审计准则》"
            },
            "2021-2023年12月底缴纳社保人数证明": {
                "准备要求": "1. 社保部门出具的官方证明\n2. 证明需包含每年12月底的参保人数\n3. 证明需加盖社保部门公章\n4. 提供清晰扫描件",
                "获取方式": "当地社会保险经办机构",
                "注意事项": "确保人数与实际情况一致，时间节点准确",
                "模板": "社保部门标准格式"
            },
            "I类知识产权清单": {
                "准备要求": "1. 列出所有I类知识产权（发明专利、集成电路布图设计等）\n2. 包括授权号、名称、授权日期、权利人\n3. 提供专利证书扫描件\n4. 清单需加盖企业公章",
                "获取方式": "国家知识产权局或相关授权机构",
                "注意事项": "确保知识产权在有效期内，权利人为申报企业",
                "模板": "可自行设计表格，包含必要信息"
            },
            "研发机构证明": {
                "准备要求": "1. 提供研发机构认定文件或证书\n2. 文件需有认定机构盖章\n3. 证明研发机构的级别和认定时间\n4. 提供清晰扫描件",
                "获取方式": "科技部门、经信部门等认定机构",
                "注意事项": "确保证明文件在有效期内",
                "模板": "认定机构标准格式"
            },
            "管理体系认证证书": {
                "准备要求": "1. 提供ISO9001等管理体系认证证书\n2. 证书需在有效期内\n3. 提供证书扫描件\n4. 证书需清晰可辨",
                "获取方式": "认证机构",
                "注意事项": "确保认证范围包含申报业务",
                "模板": "认证机构标准证书"
            },
            "信息化系统证明": {
                "准备要求": "1. 提供信息化系统截图或使用协议\n2. 截图需显示系统名称和主要功能\n3. 协议需有双方盖章\n4. 证明系统在正常使用中",
                "获取方式": "系统供应商或自行截图",
                "注意事项": "确保系统与主营业务相关",
                "模板": "无固定模板，能证明系统存在即可"
            },
            "自主品牌证明材料": {
                "准备要求": "1. 提供商标注册证\n2. 注册证需在有效期内\n3. 提供清晰扫描件\n4. 商标需与申报产品相关",
                "获取方式": "国家知识产权局商标局",
                "注意事项": "确保商标权利人为申报企业",
                "模板": "商标注册证标准格式"
            },
            "国家企业信用信息公示系统截图": {
                "准备要求": "1. 登录国家企业信用信息公示系统\n2. 搜索企业名称并截图\n3. 截图需显示企业基本信息\n4. 截图需清晰完整",
                "获取方式": "国家企业信用信息公示系统网站",
                "注意事项": "确保截图时间在近期",
                "模板": "网站截图，包含企业信用信息"
            },
            "信用中国查询截图": {
                "准备要求": "1. 登录信用中国网站\n2. 搜索企业名称并截图\n3. 截图需显示信用信息\n4. 截图需清晰完整",
                "获取方式": "信用中国网站",
                "注意事项": "确保截图时间在近期",
                "模板": "网站截图，包含信用信息"
            },
            "真实性申明": {
                "准备要求": "1. 按照模板填写真实性申明\n2. 申明需有法定代表人签字\n3. 申明需加盖企业公章\n4. 提供扫描件",
                "获取方式": "自行准备",
                "注意事项": "确保信息真实准确",
                "模板": "申报系统提供的标准模板"
            }
        }
        
        # 返回对应材料的指南
        if material_name in guides:
            guide = guides[material_name]
            return {
                "material_name": material_name,
                "description": material_detail["description"],
                "guide": guide
            }
        else:
            return {
                "material_name": material_name,
                "description": material_detail["description"],
                "guide": {
                    "准备要求": "请按照材料描述要求准备",
                    "获取方式": "请联系相关部门获取",
                    "注意事项": "确保材料真实有效",
                    "模板": "无固定模板"
                }
            }
    
    def generate_material_preparation_plan(self, missing_list: List[Dict[str, str]]) -> Dict[str, Any]:
        """生成材料准备计划"""
        plan = {
            "total_missing": len(missing_list),
            "high_priority_count": len([m for m in missing_list if m["priority"] == "高"]),
            "medium_priority_count": len([m for m in missing_list if m["priority"] == "中"]),
            "phases": [],
            "timeline": {},
            "suggestions": []
        }
        
        # 第一阶段：高优先级材料（1-2周）
        high_priority = [m for m in missing_list if m["priority"] == "高"]
        if high_priority:
            phase1 = {
                "phase": "第一阶段",
                "timeframe": "1-2周",
                "target": "完成所有必需材料",
                "materials": high_priority,
                "actions": [
                    "联系相关部门获取材料",
                    "准备盖章文件",
                    "扫描整理材料"
                ]
            }
            plan["phases"].append(phase1)
        
        # 第二阶段：中优先级材料（2-3周）
        medium_priority = [m for m in missing_list if m["priority"] == "中"]
        if medium_priority:
            phase2 = {
                "phase": "第二阶段",
                "timeframe": "2-3周",
                "target": "完成建议材料",
                "materials": medium_priority,
                "actions": [
                    "准备认证材料",
                    "收集奖励证书",
                    "整理补充材料"
                ]
            }
            plan["phases"].append(phase2)
        
        # 时间线
        plan["timeline"] = {
            "第一周": "准备营业执照、审计报告等基础材料",
            "第二周": "准备知识产权、研发机构等核心材料",
            "第三周": "准备认证证书、系统证明等辅助材料",
            "第四周": "整理所有材料，查漏补缺"
        }
        
        # 建议
        if high_priority:
            plan["suggestions"].append("优先准备必需材料，确保申报基本条件")
        
        if medium_priority:
            plan["suggestions"].append("建议材料可提升申报成功率，尽量准备")
        
        plan["suggestions"].append("所有材料需提前准备，避免临时赶工")
        plan["suggestions"].append("建议指定专人负责材料准备和整理")
        plan["suggestions"].append("定期检查材料准备进度，及时调整计划")
        
        return plan
