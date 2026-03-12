# 专精特新小巨人申报技能文件上传解决方案

## 问题分析
当前Web通道不支持文件上传，但专精特新申报需要处理多种企业文档：
- PDF文件（审计报告、营业执照等）
- Excel文件（财务数据、专利清单等）
- Word文件（企业介绍、证明材料等）

## 解决方案设计

### 方案一：扩展Web通道支持文件上传（推荐）
在现有Web通道基础上添加文件上传功能。

#### 实现步骤：
1. **前端修改**：
   - 在chat.html中添加文件上传组件
   - 支持多文件选择和拖拽上传
   - 显示上传进度和文件列表

2. **后端修改**：
   - 在web_channel.py中添加文件上传API端点
   - 实现文件接收和临时存储
   - 支持文件类型验证和大小限制

3. **消息处理**：
   - 扩展WebMessage类支持文件类型
   - 将文件路径或内容传递给技能处理

#### 技术实现：

**前端代码示例**：
```html
<div class="file-upload-area">
  <input type="file" id="fileInput" multiple accept=".pdf,.xlsx,.xls,.docx,.doc,.txt">
  <div class="drop-zone" id="dropZone">
    <p>拖拽文件到此处或点击选择</p>
    <p class="file-types">支持PDF、Excel、Word文档</p>
  </div>
  <div id="fileList"></div>
</div>
```

**后端API端点**：
```python
class FileUploadHandler:
    def POST(self):
        web.header('Content-Type', 'application/json; charset=utf-8')
        try:
            data = web.input(file={})
            file_data = data.file
            
            # 保存文件到临时目录
            import tempfile
            import os
            from common.tmp_dir import TmpDir
            
            tmp_dir = TmpDir().path()
            file_path = os.path.join(tmp_dir, file_data.filename)
            
            with open(file_path, 'wb') as f:
                f.write(file_data.file.read())
            
            return json.dumps({
                "status": "success",
                "file_path": file_path,
                "filename": file_data.filename,
                "size": os.path.getsize(file_path)
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})
```

### 方案二：使用URL引用文件
用户提供文件URL，系统下载处理。

#### 实现步骤：
1. **前端界面**：
   - 添加URL输入框
   - 支持多个URL输入
   - 显示下载状态

2. **后端处理**：
   - 验证URL有效性
   - 下载文件到临时目录
   - 传递给技能处理

#### 技术实现：
```python
class FileURLHandler:
    def POST(self):
        data = json.loads(web.data())
        urls = data.get('urls', [])
        
        downloaded_files = []
        for url in urls:
            try:
                # 下载文件
                response = requests.get(url, timeout=30)
                filename = os.path.basename(url)
                file_path = os.path.join(tmp_dir, filename)
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_files.append({
                    "path": file_path,
                    "filename": filename,
                    "size": len(response.content)
                })
            except Exception as e:
                logger.error(f"Failed to download {url}: {e}")
        
        return json.dumps({
            "status": "success",
            "files": downloaded_files
        })
```

### 方案三：本地路径引用（开发/测试用）
用户提供本地文件路径，系统直接读取。

#### 实现步骤：
1. **前端界面**：
   - 添加路径输入框
   - 支持多个路径输入
   - 显示文件验证状态

2. **后端处理**：
   - 验证路径存在性和可读性
   - 复制文件到工作目录
   - 传递给技能处理

### 方案四：混合方案（推荐）
结合多种方式，提供灵活的文件输入：

1. **直接上传**：通过Web界面上传文件
2. **URL引用**：提供文件下载链接
3. **路径引用**：开发环境使用本地路径
4. **云存储**：集成云存储服务（如阿里云OSS、腾讯云COS）

## 专精特新技能文件处理需求

### 支持的文件类型：
1. **PDF文件**：
   - 企业营业执照
   - 年度审计报告
   - 专利证书
   - 认证证书

2. **Excel文件**：
   - 财务数据表
   - 专利清单
   - 员工社保数据
   - 研发费用明细

3. **Word文件**：
   - 企业介绍
   - 市场占有率说明
   - 证明材料说明
   - 申请书草稿

### 文件处理流程：
```
用户上传文件 → 文件验证 → 临时存储 → 技能处理 → 结果返回 → 清理临时文件
```

### 技能端文件处理接口：
```python
class SpecializedInnovativeSkill:
    async def process_files(self, files: List[Dict], company_data: Dict) -> Dict:
        """
        处理上传的企业文件
        
        Args:
            files: 文件列表，每个文件包含path、filename、type等信息
            company_data: 企业基本信息
            
        Returns:
            处理结果，包含提取的数据和验证信息
        """
        results = {
            "extracted_data": {},
            "file_analysis": [],
            "validation_results": []
        }
        
        for file_info in files:
            file_path = file_info["path"]
            file_type = file_info.get("type", self._detect_file_type(file_path))
            
            if file_type == "pdf":
                data = await self._process_pdf(file_path)
            elif file_type == "excel":
                data = await self._process_excel(file_path)
            elif file_type == "word":
                data = await self._process_word(file_path)
            else:
                data = {"error": f"Unsupported file type: {file_type}"}
            
            results["file_analysis"].append({
                "filename": file_info["filename"],
                "type": file_type,
                "data": data,
                "status": "success" if "error" not in data else "error"
            })
        
        return results
```

## 实施计划

### 第一阶段：基础文件上传（1-2天）
1. 扩展Web通道支持文件上传
2. 实现前端文件上传组件
3. 添加文件类型验证
4. 实现临时文件管理

### 第二阶段：文件处理集成（1-2天）
1. 集成PDF处理库（pdfplumber）
2. 集成Excel处理库（openpyxl）
3. 集成Word处理库（python-docx）
4. 实现文件内容提取

### 第三阶段：技能集成（1天）
1. 修改技能接口支持文件处理
2. 实现文件数据与企业信息合并
3. 优化用户体验

### 第四阶段：高级功能（可选）
1. 支持云存储集成
2. 添加文件预览功能
3. 实现批量处理
4. 添加文件模板下载

## 技术依赖

### Python库：
```bash
pip install pdfplumber openpyxl python-docx Pillow
```

### 前端库：
```html
<!-- 文件上传组件 -->
<script src="https://unpkg.com/dropzone@5/dist/min/dropzone.min.js"></script>
<link rel="stylesheet" href="https://unpkg.com/dropzone@5/dist/min/dropzone.min.css">
```

## 安全考虑

1. **文件类型验证**：只允许特定类型的文件上传
2. **文件大小限制**：限制单个文件和总大小
3. **病毒扫描**：集成病毒扫描（可选）
4. **临时文件清理**：定期清理过期文件
5. **访问控制**：验证用户权限

## 性能优化

1. **异步处理**：大文件异步处理，避免阻塞
2. **分片上传**：支持大文件分片上传
3. **进度显示**：实时显示上传和处理进度
4. **缓存机制**：缓存处理结果，避免重复处理

## 测试计划

1. **单元测试**：测试文件上传和处理逻辑
2. **集成测试**：测试完整流程
3. **性能测试**：测试大文件处理性能
4. **安全测试**：测试文件上传安全性

## 部署建议

1. **开发环境**：使用方案三（本地路径）快速测试
2. **测试环境**：使用方案一（文件上传）完整测试
3. **生产环境**：使用方案四（混合方案）提供最佳体验

## 总结

推荐采用**方案一（扩展Web通道）**作为主要实现，同时保留**方案二（URL引用）**作为备选。这样既能提供良好的用户体验，又能保证系统的灵活性和可扩展性。

文件上传功能对于专精特新申报技能至关重要，能够显著提升用户体验和申报效率。建议优先实施第一阶段和第二阶段，快速上线核心功能。