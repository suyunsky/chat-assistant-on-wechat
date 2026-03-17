"""
Write tool - Write file content
Creates or overwrites files, automatically creates parent directories
"""

import os
from typing import Dict, Any
from pathlib import Path

from agent.tools.base_tool import BaseTool, ToolResult
from common.utils import expand_path


class Write(BaseTool):
    """Tool for writing file content"""
    
    name: str = "write"
    description: str = "Write content to a file. Creates the file if it doesn't exist, overwrites if it does. Automatically creates parent directories. IMPORTANT: Single write should not exceed 10KB. For large files, create a skeleton first, then use edit to add content in chunks."
    
    params: dict = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to the file to write (relative or absolute)"
            },
            "content": {
                "type": "string",
                "description": "Content to write to the file"
            }
        },
        "required": ["path", "content"]
    }
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.cwd = self.config.get("cwd", os.getcwd())
        self.memory_manager = self.config.get("memory_manager", None)
    
    def execute(self, args: Dict[str, Any]) -> ToolResult:
        """
        Execute file write operation
        
        :param args: Contains file path and content
        :return: Operation result
        """
        path = args.get("path", "").strip()
        content = args.get("content", "")
        
        if not path:
            return ToolResult.fail("Error: path parameter is required")
        
        # 检查是否是"企业申报"相关的文件
        # 通过上下文判断当前是否在企业申报任务中
        is_enterprise_declaration = False
        company_name = None
        
        # 从上下文获取信息
        if hasattr(self, 'context') and self.context:
            # 检查对话历史中是否包含"企业申报"关键词
            import re
            conversation_text = str(self.context).lower()
            if any(keyword in conversation_text for keyword in [
                '企业申报', 'enterprise declaration', 'business declaration',
                '营业执照', '税务登记', '组织机构代码', '开户许可证',
                '申报材料', '申报文件', '申报资料'
            ]):
                is_enterprise_declaration = True
                
                # 尝试从对话中提取企业名称
                company_patterns = [
                    r'([\u4e00-\u9fa5a-zA-Z0-9]+公司)',
                    r'([\u4e00-\u9fa5a-zA-Z0-9]+企业)',
                    r'([\u4e00-\u9fa5a-zA-Z0-9]+集团)',
                    r'([\u4e00-\u9fa5a-zA-Z0-9]+有限公司)',
                    r'([\u4e00-\u9fa5a-zA-Z0-9]+有限责任公司)',
                    r'company[:\s]+([\u4e00-\u9fa5a-zA-Z0-9]+)',
                    r'enterprise[:\s]+([\u4e00-\u9fa5a-zA-Z0-9]+)',
                    r'企业名称[：:\s]+([\u4e00-\u9fa5a-zA-Z0-9]+)',
                    r'公司名称[：:\s]+([\u4e00-\u9fa5a-zA-Z0-9]+)'
                ]
                
                for pattern in company_patterns:
                    match = re.search(pattern, conversation_text, re.IGNORECASE)
                    if match:
                        company_name = match.group(1)
                        break
                
                if not company_name:
                    company_name = "未命名企业"
        
        # 如果是企业申报文件，重新组织路径
        if is_enterprise_declaration:
            # 创建企业申报根目录
            enterprise_root_dir = os.path.join(os.getcwd(), "企业申报")
            if not os.path.exists(enterprise_root_dir):
                os.makedirs(enterprise_root_dir, exist_ok=True)
                print(f"[Write Tool] 创建企业申报根目录: {enterprise_root_dir}")
            
            # 创建企业专属文件夹
            company_dir = os.path.join(enterprise_root_dir, company_name)
            if not os.path.exists(company_dir):
                os.makedirs(company_dir, exist_ok=True)
                print(f"[Write Tool] 创建企业专属文件夹: {company_dir}")
            
            # 获取原始文件名
            original_filename = os.path.basename(path)
            
            # 如果路径已经是绝对路径，只取文件名
            if os.path.isabs(path):
                original_filename = os.path.basename(path)
            
            # 构建新的文件路径（直接放在企业专属文件夹中，不按日期分）
            new_path = os.path.join(company_dir, original_filename)
            
            # 记录重定向信息
            print(f"[Write Tool] 企业申报文件重定向: {path} -> {new_path}")
            print(f"[Write Tool] 企业名称: {company_name}")
            
            # 使用新的路径
            path = new_path
        
        # Resolve path
        absolute_path = self._resolve_path(path)
        
        try:
            # Create parent directory (if needed)
            parent_dir = os.path.dirname(absolute_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write file
            with open(absolute_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Get bytes written
            bytes_written = len(content.encode('utf-8'))
            
            # Auto-sync to memory database if this is a memory file
            if self.memory_manager and 'memory/' in path:
                self.memory_manager.mark_dirty()
            
            result = {
                "message": f"Successfully wrote {bytes_written} bytes to {path}",
                "path": path,
                "bytes_written": bytes_written
            }
            
            # 如果是企业申报文件，添加额外信息
            if is_enterprise_declaration:
                result["enterprise_declaration"] = True
                result["company_name"] = company_name
                result["original_path"] = args.get("path", "")
                result["message"] = f"企业申报文件已保存到企业专属目录: {company_name}/{original_filename}"
                result["company_directory"] = company_dir
            
            return ToolResult.success(result)
            
        except PermissionError:
            return ToolResult.fail(f"Error: Permission denied writing to {path}")
        except Exception as e:
            return ToolResult.fail(f"Error writing file: {str(e)}")
    
    def _resolve_path(self, path: str) -> str:
        """
        Resolve path to absolute path
        
        :param path: Relative or absolute path
        :return: Absolute path
        """
        # Expand ~ to user home directory
        path = expand_path(path)
        if os.path.isabs(path):
            return path
        return os.path.abspath(os.path.join(self.cwd, path))
