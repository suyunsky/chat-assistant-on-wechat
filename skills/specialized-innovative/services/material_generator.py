"""
申报材料生成模块
生成申请书、市场占有率说明、企业介绍等材料
"""

import json
import os
from typing import Dict, Any, List
from datetime import datetime

from common.log import logger


class MaterialGenerator:
    """申报材料生成器"""
    
    def __init__(self):
        logger.info("[专精特新] 材料生成器初始化完成")
    
    async def execute(self, company_data: Dict[str, Any], assessment: Dict[str, Any]) -> Dict[str, Any]:
        """生成申报材料"""
        try:
            logger.info("[专精特新] 开始生成申报材料")
            
            materials = {}
            
            # 1. 生成市场占有率说明（1000字）
            market_share_statement = await self.generate_market_share_statement(company_data, assessment)
            materials["market_share_statement"] = market_share_statement
            
            # 2. 生成企业2000字介绍
            company_introduction = await self.generate_company_introduction(company_data, assessment)
            materials["company_introduction"] = company_introduction
            
            # 3. 生成补短板说明（300字）
            supplement_shortage_statement = await self.generate_supplement_shortage_statement(company_data, assessment)
            materials["supplement_shortage_statement"] = supplement_shortage_statement
            
            # 4. 生成申请书框架
            application_framework = self.generate_application_framework(company_data, assessment)
            materials["application_framework"] = application_framework
            
            # 5. 生成佐证材料清单
            proof_materials_list = self.generate_proof_materials_list(company_data, assessment)
            materials["proof_materials_list"] = proof_materials_list
            
            logger.info(f"[专精特新] 材料生成完成，共生成{len(materials)}类材料")
            return materials
            
        except Exception as e:
            logger.error(f"[专精特新] 材料生成错误: {e}")
            return {
                "error": str(e),
                "market_share_statement": f"材料生成出错: {str(e)}",
                "company_introduction": f"材料生成出错: {str(e)}",
                "supplement_shortage_statement": f"材料生成出错: {str(e)}"
            }
    
    async def generate_market_share_statement(self, company_data: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """生成市场占有率说明（1000字）"""
        try:
            # 获取关键数据
            company_name = company_data.get("company_name", "该公司")
            industry = company_data.get("industry", "相关行业")
            main_products = company_data.get("main_products", "主要产品")
            market_share = company_data.get("market_share", 0)
            
            # 这里可以调用大模型生成更专业的内容
            # 简化版本：使用模板
            
            statement = f"""一、市场定义与范围

{company_name}所处的细分市场为{industry}领域中的{main_products}市场。该市场主要面向[描述目标客户群体]，市场规模近年来保持稳定增长态势。

根据行业研究报告显示，{industry}领域的{main_products}市场在2023年总体规模约为[具体数字]亿元，预计未来三年复合增长率将达到[具体百分比]%。

二、市场规模与竞争格局

当前{main_products}市场的主要参与者包括：
1. [主要竞争对手1]，市场占有率约[百分比]%
2. [主要竞争对手2]，市场占有率约[百分比]%
3. {company_name}，市场占有率约{market_share}%
4. [其他竞争对手]，合计市场占有率约[百分比]%

市场竞争呈现[描述竞争特点，如：集中度较高、差异化竞争等]的特点。

三、企业市场地位分析

{company_name}在{main_products}细分市场中处于[描述地位，如：领先地位、重要参与者等]。公司通过以下方面建立了市场竞争优势：

1. 技术优势：[描述技术特点]
2. 产品优势：[描述产品特点]
3. 客户优势：[描述客户基础]
4. 品牌优势：[描述品牌影响力]

四、市场占有率数据来源与计算方法

本报告中市场占有率数据基于以下来源和方法计算：
1. 行业权威机构发布的年度报告
2. 公司内部销售数据统计
3. 第三方市场调研数据
4. 计算公式：公司产品销售额 / 细分市场总销售额 × 100%

经综合测算，{company_name}在{industry}领域的{main_products}细分市场中，2023年市场占有率约为{market_share}%，位居行业[排名位置]。

五、未来市场展望

随着[描述行业发展趋势]，预计{main_products}市场将呈现[描述未来趋势]。{company_name}将通过[描述发展策略]，进一步提升市场占有率，目标在未来三年内达到[目标百分比]%的市场份额。"""
            
            return statement
            
        except Exception as e:
            logger.error(f"[专精特新] 生成市场占有率说明错误: {e}")
            return f"生成市场占有率说明时出错: {str(e)}"
    
    async def generate_company_introduction(self, company_data: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """生成企业2000字介绍"""
        try:
            # 获取关键数据
            company_name = company_data.get("company_name", "该企业")
            establishment_year = company_data.get("establishment_year", 0)
            industry = company_data.get("industry", "相关行业")
            main_business = company_data.get("main_business", "主营业务")
            main_products = company_data.get("main_products", "主要产品")
            revenue_2023 = company_data.get("revenue_2023", 0)
            rd_expense_ratio = company_data.get("rd_expense_ratio", 0)
            patent_count = company_data.get("patent_count", 0)
            employee_count = company_data.get("employee_count", 0)
            
            # 计算企业年龄
            current_year = datetime.now().year
            company_age = current_year - establishment_year if establishment_year else 0
            
            introduction = f"""一、企业经营概况

{company_name}成立于{establishment_year}年，是一家专注于{industry}领域的高新技术企业。公司深耕{main_business}，经过{company_age}年的发展，已成长为行业内具有重要影响力的企业。

公司注册资本[具体数字]万元，总部位于[具体地点]，在[其他地点]设有分支机构。现有员工{employee_count}人，其中研发人员占比[具体百分比]%，本科以上学历员工占比[具体百分比]%。

二、主营业务与技术优势

公司主营业务为{main_business}，核心产品包括{main_products}。在技术研发方面，公司具有以下优势：

1. 研发投入持续增长：近年来研发费用占营业收入比重保持在{rd_expense_ratio:.1f}%以上，高于行业平均水平。
2. 知识产权积累丰富：累计获得专利{patent_count}项，其中发明专利[具体数字]项，软件著作权[具体数字]项。
3. 技术团队实力雄厚：拥有[具体数字]名高级工程师、[具体数字]名博士组成的研发团队。
4. 研发平台建设完善：建立了[具体研发平台名称]，与[高校/科研机构名称]建立了产学研合作关系。

三、市场地位与经营业绩

公司在{industry}领域具有显著的市场地位：
1. 市场占有率：在{main_products}细分市场中占有率约[具体百分比]%，位居行业前列。
2. 客户基础：产品已广泛应用于[描述应用领域]，服务客户包括[描述重要客户]。
3. 经营业绩：2023年实现营业收入{revenue_2023}万元，近三年营业收入复合增长率[具体百分比]%。
4. 盈利能力：毛利率[具体百分比]%，净利率[具体百分比]%，盈利能力持续提升。

四、产业链地位与协同效应

公司在产业链中处于[描述产业链位置]，具有以下特点：
1. 上游协同：与[上游供应商名称]建立了稳定的供应链合作关系。
2. 下游应用：产品广泛应用于[下游应用领域]，为[下游客户名称]提供关键配套。
3. 横向合作：与[同行企业名称]在[具体领域]开展技术合作。
4. 生态建设：积极参与[行业生态建设]，推动产业链协同发展。

五、质量管理与体系建设

公司高度重视质量管理和体系建设：
1. 质量管理：通过了ISO9001质量管理体系认证，建立了完善的质量控制体系。
2. 环境管理：通过了ISO14001环境管理体系认证，践行绿色发展理念。
3. 信息安全：建立了完善的信息安全管理体系，保障客户数据安全。
4. 标准化建设：参与了[具体标准]的制定工作，推动行业标准化发展。

六、社会责任与可持续发展

公司积极履行社会责任：
1. 就业贡献：为当地提供{employee_count}个就业岗位，其中[具体数字]%为本地员工。
2. 税收贡献：近三年累计纳税[具体数字]万元，为地方经济发展做出贡献。
3. 环保投入：每年投入[具体数字]万元用于环保设施建设和改造。
4. 公益事业：积极参与[具体公益项目]，回馈社会。

七、未来发展规划

面向未来，公司将围绕以下重点方向加快发展：
1. 技术创新：加大研发投入，在[具体技术领域]实现突破。
2. 市场拓展：深化国内市场，拓展国际市场，目标三年内国际市场收入占比达到[具体百分比]%。
3. 产业升级：推动智能制造升级，建设数字化工厂。
4. 人才培养：实施"人才强企"战略，培养一批行业领军人才。

{company_name}将始终坚持创新驱动、质量为本的发展理念，致力于成为{industry}领域的领军企业，为行业发展和技术进步做出更大贡献。"""
            
            return introduction
            
        except Exception as e:
            logger.error(f"[专精特新] 生成企业介绍错误: {e}")
            return f"生成企业介绍时出错: {str(e)}"
    
    async def generate_supplement_shortage_statement(self, company_data: Dict[str, Any], assessment: Dict[str, Any]) -> str:
        """生成补短板说明（300字）"""
        try:
            industry = company_data.get("industry", "相关行业")
            main_products = company_data.get("main_products", "主要产品")
            
            statement = f"""在{industry}领域，{main_products}长期依赖进口，存在明显的"卡脖子"问题。通过自主研发和技术攻关，成功实现了该产品的国产化替代，填补了国内空白。

具体表现在以下几个方面：
1. 技术突破：攻克了[具体技术难题]，打破了国外技术垄断。
2. 性能提升：产品性能达到国际先进水平，部分指标优于进口产品。
3. 成本优势：生产成本较进口产品降低[具体百分比]%，具有显著的价格优势。
4. 供应链安全：建立了自主可控的供应链体系，保障了产业链安全。

该成果的应用推广，有效缓解了{industry}领域对进口产品的依赖，提升了我国在该领域的自主可控能力，具有重要的战略意义和经济价值。"""
            
            return statement
            
        except Exception as e:
            logger.error(f"[专精特新] 生成补短板说明错误: {e}")
            return f"生成补短板说明时出错: {str(e)}"
    
    def generate_application_framework(self, company_data: Dict[str, Any], assessment: Dict[str, Any]) -> Dict[str, Any]:
        """生成申请书框架"""
        framework = {
            "一、企业基本情况": {
                "企业名称": company_data.get("company_name", ""),
                "注册时间": company_data.get("establishment_year", ""),
                "所属行业": company_data.get("industry", ""),
                "企业规模": self._determine_company_size(company_data),
                "统一社会信用代码": "[待填写]",
                "通讯地址": "[待填写]",
                "法定代表人": "[待填写]",
                "联系人": "[待填写]"
            },
            "二、经济效益和经营情况": {
                "2021-2023年主要财务指标": self._generate_financial_table(company_data),
                "员工情况": {
                    "全职员工数量": company_data.get("employee_count", 0),
                    "研发人员数量": company_data.get("rd_employee_count", 0)
                },
                "融资情况": {
                    "股权融资总额": "[待填写]",
                    "银行贷款": "[待填写]"
                }
            },
            "三、专业化": {
                "企业从事特定细分市场时间": f"{company_data.get('company_age', 0)}年",
                "主营业务收入占营业收入比重": f"{company_data.get('main_revenue_ratio', 0):.1f}%",
                "近2年主营业务收入平均增长率": f"{company_data.get('revenue_growth_2y_avg', 0):.1f}%",
                "排名前三的主要产品": self._format_main_products(company_data.get("main_products", ""))
            },
            "四、精细化": {
                "管理体系认证情况": "[待填写]",
                "核心业务信息系统支撑情况": "[待填写]",
                "产品认证情况": "[待填写]",
                "资产负债率": f"{company_data.get('asset_liability_ratio', 0):.1f}%"
            },
            "五、特色化": {
                "主导产品全国细分市场占有率": f"{company_data.get('market_share', 0):.1f}%",
                "市场占有率说明": "详见附件：市场占有率说明",
                "企业自有品牌个数": "[待填写]",
                "自有品牌销售收入": "[待填写]"
            },
            "六、创新能力": {
                "研发机构建设情况": "[待填写]",
                "研发费用情况": {
                    "2021年": f"{company_data.get('rd_expense_2021', 0)}万元",
                    "2022年": f"{company_data.get('rd_expense_2022', 0)}万元",
                    "2023年": f"{company_data.get('rd_expense_2023', 0)}万元",
                    "研发费用占比": f"{company_data.get('rd_expense_ratio', 0):.1f}%"
                },
                "知识产权情况": {
                    "I类知识产权总数": company_data.get("patent_count", 0),
                    "其中发明专利": "[待填写]"
                }
            },
            "七、产业链配套": {
                "所属产业链": "[待填写]",
                "补短板填空白情况": "详见附件：补短板说明",
                "为知名大企业配套情况": "[待填写]"
            },
            "八、主导产品所属领域": {
                "主导产品名称": company_data.get("main_products", ""),
                "是否属于工业'六基'领域": "[待填写]",
                "主导产品类别": "[待填写]"
            },
            "九、其他": {
                "企业总体情况简要介绍": "详见附件：企业介绍",
                "标准制定情况": "[待填写]",
                "获得称号情况": "[待填写]"
            }
        }
        
        return framework
    
    def generate_proof_materials_list(self, company_data: Dict[str, Any], assessment: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成佐证材料清单"""
        materials_list = [
            {"序号": "1", "材料名称": "企业营业执照", "要求": "复印件加盖公章", "备注": "必需"},
            {"序号": "2", "材料名称": "2021-2023年年度审计报告", "要求": "已赋码电子原件", "备注": "必需"},
            {"序号": "3", "材料名称": "2021-2023年12月底缴纳社保人数证明", "要求": "社保部门出具", "备注": "必需"},
            {"序号": "4", "材料名称": "I类知识产权清单", "要求": "包括授权号、名称等", "备注": "必需"},
            {"序号": "5", "材料名称": "研发机构证明", "要求": "认定文件或证书", "备注": "必需"},
            {"序号": "6", "材料名称": "管理体系认证证书", "要求": "ISO9001等", "备注": "必需"},
            {"序号": "7", "材料名称": "产品认证证书", "要求": "UL、CE等", "备注": "建议"},
            {"序号": "8", "材料名称": "信息化系统证明", "要求": "系统截图或协议", "备注": "必需"},
            {"序号": "9", "材料名称": "自主品牌证明材料", "要求": "商标注册证", "备注": "必需"},
            {"序号": "10", "材料名称": "国家级科技奖励证书", "要求": "如有则提供", "备注": "可选"},
            {"序号": "11", "材料名称": "创客中国大赛获奖证明", "要求": "如有则提供", "备注": "可选"},
            {"序号": "12", "材料名称": "国家企业信用信息公示系统截图", "要求": "网站截图", "备注": "必需"},
            {"序号": "13", "材料名称": "信用中国查询截图", "要求": "网站截图", "备注": "必需"},
            {"序号": "14", "材料名称": "真实性申明", "要求": "加盖公章", "备注": "必需"}
        ]
        
        return materials_list
    
    def _determine_company_size(self, data: Dict[str, Any]) -> str:
        """确定企业规模"""
        revenue = data.get("revenue_2023", 0)
        employee_count = data.get("employee_count", 0)
        
        if revenue >= 40000 or employee_count >= 1000:
            return "大型"
        elif revenue >= 2000 or employee_count >= 300:
            return "中型"
        elif revenue >= 300 or employee_count >= 20:
            return "小型"
        else:
            return "微型"
    
    def _generate_financial_table(self, data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """生成财务数据表"""
        financial_data = {}
        
        years = [2021, 2022, 2023]
        for year in years:
            year_data = {
                "营业收入": data.get(f"revenue_{year}", 0),
                "主营业务收入": data.get(f"main_revenue_{year}", 0),
                "净利润": data.get(f"net_profit_{year}", 0),
                "研发费用": data.get(f"rd_expense_{year}", 0),
                "资产总额": data.get(f"asset_total_{year}", 0),
                "负债总额": data.get(f"liability_total_{year}", 0)
            }
            financial_data[str(year)] = year_data
        
        return financial_data
    
    def _format_main_products(self, main_products: str) -> str:
        """格式化主要产品"""
        if not main_products:
            return "待填写"
        
        # 简单处理：如果包含逗号或分号，按原样返回
        if "," in main_products or "，" in main_products or ";" in main_products:
            return main_products
        
        # 否则按长度分割
        if len(main_products) > 30:
            return main_products[:30] + "..."
        
        return main_products
