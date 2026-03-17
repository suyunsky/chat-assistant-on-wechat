"""
OCR图片文字识别工具 - 支持百度OCR API和PaddleOCR
"""

import os
import json
import time
import tempfile
import base64
import hashlib
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

from agent.tools.base_tool import BaseTool, ToolResult
from common.log import logger


class OCRTool(BaseTool):
    """OCR图片文字识别工具"""
    
    # 类属性
    name = "ocr_image"
    description = "识别图片中的文字内容，支持中文、英文等多种语言，可用于发票、文档、名片等图片的文字提取"
    params = {
        "type": "object",
        "properties": {
            "image_path": {
                "type": "string",
                "description": "图片文件路径（支持本地路径）"
            },
            "language": {
                "type": "string",
                "description": "识别语言",
                "enum": ["auto", "ch", "en", "ch_en", "japan", "korean", "french", "german", "spanish"],
                "default": "ch"
            },
            "recognize_type": {
                "type": "string",
                "description": "识别类型，针对不同类型优化识别",
                "enum": ["general", "receipt", "business_card", "document", "table", "handwriting", "formula"],
                "default": "general"
            },
            "preprocess": {
                "type": "boolean",
                "description": "是否进行图片预处理（增强对比度、去噪等）",
                "default": True
            },
            "extract_fields": {
                "type": "array",
                "description": "需要提取的特定字段（如发票号码、金额、日期、姓名、电话等）",
                "items": {"type": "string"},
                "default": []
            },
            "return_format": {
                "type": "string",
                "description": "返回格式",
                "enum": ["text", "structured", "both"],
                "default": "both"
            }
        },
        "required": ["image_path"]
    }
    
    def __init__(self):
        super().__init__()
        
        # PaddleOCR实例（延迟初始化）
        self._paddle_ocr = None
        self._ocr_initialized = False
        
        # 百度OCR配置
        self._baidu_ocr_config = self._load_baidu_ocr_config()
        
    def _load_baidu_ocr_config(self) -> Dict:
        """加载百度OCR配置"""
        try:
            # 从配置文件读取
            import json
            
            # 尝试多个可能的配置文件路径
            possible_paths = [
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config.json'),
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'config.json'),
                os.path.join(os.getcwd(), 'config.json'),
                '/Users/maowenhui/Downloads/chat-assistant-on-wechat/chat-assistant-on-wechat/config.json'
            ]
            
            config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
            
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                baidu_config = {
                    'api_key': config.get('baidu_ocr_api_key', ''),
                    'secret_key': config.get('baidu_ocr_secret_key', ''),
                    'enabled': bool(config.get('baidu_ocr_api_key') and config.get('baidu_ocr_secret_key'))
                }
                
                if baidu_config['enabled']:
                    logger.info(f"[OCR] 百度OCR配置加载成功，API Key: {baidu_config['api_key'][:10]}...")
                else:
                    logger.info("[OCR] 百度OCR未配置，将使用PaddleOCR")
                    
                return baidu_config
            else:
                logger.warning(f"[OCR] 配置文件不存在，尝试的路径: {possible_paths}")
                return {'api_key': '', 'secret_key': '', 'enabled': False}
                
        except Exception as e:
            logger.error(f"[OCR] 加载百度OCR配置失败: {e}")
            return {'api_key': '', 'secret_key': '', 'enabled': False}
    
    def _get_baidu_access_token(self) -> str:
        """获取百度OCR访问令牌"""
        try:
            import requests
            
            api_key = self._baidu_ocr_config['api_key']
            secret_key = self._baidu_ocr_config['secret_key']
            
            if not api_key or not secret_key:
                return ""
            
            # 百度OCR获取access_token的URL
            auth_url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": secret_key
            }
            
            response = requests.get(auth_url, params=params)
            result = response.json()
            
            if 'access_token' in result:
                logger.debug("[OCR] 百度OCR访问令牌获取成功")
                return result['access_token']
            else:
                logger.error(f"[OCR] 获取百度OCR访问令牌失败: {result}")
                return ""
                
        except Exception as e:
            logger.error(f"[OCR] 获取百度OCR访问令牌异常: {e}")
            return ""
    
    def _recognize_with_baidu_ocr(self, image_path: str, language: str, recognize_type: str) -> Dict:
        """使用百度OCR识别文字"""
        try:
            # 检查百度OCR是否启用
            if not self._baidu_ocr_config['enabled']:
                return {
                    "success": False,
                    "error": "百度OCR未配置",
                    "engine": "baidu_ocr"
                }
            
            start_time = time.time()
            
            # 获取访问令牌
            access_token = self._get_baidu_access_token()
            if not access_token:
                return {
                    "success": False,
                    "error": "获取百度OCR访问令牌失败",
                    "engine": "baidu_ocr"
                }
            
            # 读取图片并转换为base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # 构建请求参数
            url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general"
            
            # 根据识别类型选择不同的参数
            params = {
                "access_token": access_token,
                "image": image_base64,
                "language_type": "CHN_ENG",  # 中英文混合
                "detect_direction": "true",  # 检测图像朝向
                "paragraph": "true",  # 输出段落信息
                "probability": "true"  # 返回置信度
            }
            
            # 根据识别类型调整参数
            if recognize_type == "receipt":
                params["recognize_granularity"] = "big"  # 大粒度识别
            elif recognize_type == "business_card":
                params["recognize_granularity"] = "small"  # 小粒度识别
            elif recognize_type == "document":
                params["paragraph"] = "true"
            elif recognize_type == "table":
                params["table"] = "true"  # 表格识别
            
            # 发送请求
            import requests
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(url, data=params, headers=headers)
            result = response.json()
            
            execution_time = time.time() - start_time
            
            # 检查响应
            if 'error_code' in result:
                error_msg = result.get('error_msg', '未知错误')
                logger.error(f"[OCR] 百度OCR识别失败: {error_msg}")
                return {
                    "success": False,
                    "error": f"百度OCR识别失败: {error_msg}",
                    "engine": "baidu_ocr"
                }
            
            # 解析结果
            text_lines = []
            confidences = []
            positions = []
            
            if 'words_result' in result:
                for item in result['words_result']:
                    if 'words' in item:
                        text_lines.append(item['words'])
                    
                    # 获取置信度
                    if 'probability' in item and 'average' in item['probability']:
                        confidences.append(float(item['probability']['average']))
                    else:
                        confidences.append(0.8)  # 默认置信度
                    
                    # 获取位置信息
                    if 'location' in item:
                        location = item['location']
                        positions.append([
                            [location['left'], location['top']],
                            [location['left'] + location['width'], location['top']],
                            [location['left'] + location['width'], location['top'] + location['height']],
                            [location['left'], location['top'] + location['height']]
                        ])
                    else:
                        positions.append([])
            
            # 合并文本
            text = "\n".join(text_lines)
            
            # 计算平均置信度
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # 识别语言检测
            detected_lang = self._detect_language(text)
            
            logger.info(f"[OCR] 百度OCR识别完成: {len(text_lines)}行文字, 置信度: {avg_confidence:.2f}, 耗时: {execution_time:.2f}s")
            
            return {
                "success": True,
                "text": text,
                "lines": text_lines,
                "confidences": confidences,
                "positions": positions,
                "avg_confidence": avg_confidence,
                "detected_language": detected_lang,
                "execution_time": execution_time,
                "line_count": len(text_lines),
                "char_count": len(text),
                "engine": "baidu_ocr"
            }
            
        except Exception as e:
            logger.error(f"[OCR] 百度OCR识别异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "baidu_ocr"
            }
        
    def _init_paddle_ocr(self, language: str = "ch") -> bool:
        """初始化PaddleOCR"""
        try:
            # 尝试导入PaddleOCR
            from paddleocr import PaddleOCR
            
            # 语言映射
            lang_map = {
                "ch": "ch",
                "en": "en",
                "ch_en": "ch",
                "japan": "japan",
                "korean": "korean",
                "french": "french",
                "german": "german",
                "spanish": "spanish",
                "auto": "ch"
            }
            
            ocr_lang = lang_map.get(language, "ch")
            
            # 初始化PaddleOCR - 使用最简化的参数避免段错误
            # 添加环境变量避免模型源检查
            import os
            os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
            
            # 使用最简单的配置（只提供语言参数）
            self._paddle_ocr = PaddleOCR(
                lang=ocr_lang  # 只提供语言参数
            )
            
            self._ocr_initialized = True
            logger.info(f"[OCR] PaddleOCR初始化成功，语言: {ocr_lang}")
            return True
            
        except ImportError as e:
            logger.error(f"[OCR] PaddleOCR未安装: {e}")
            logger.info("[OCR] 请安装PaddleOCR: pip install paddlepaddle paddleocr")
            return False
        except Exception as e:
            logger.error(f"[OCR] PaddleOCR初始化失败: {e}")
            return False
    
    def _preprocess_image(self, image_path: str) -> str:
        """图片预处理"""
        try:
            # 打开图片
            img = Image.open(image_path)
            
            # 记录原始信息
            original_mode = img.mode
            original_size = img.size
            
            # 转换模式为RGB（PaddleOCR需要RGB格式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logger.debug(f"[OCR] 图片模式转换: {original_mode} -> RGB")
            
            # 调整尺寸（限制最大尺寸，提高识别速度）
            max_size = 1600
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.debug(f"[OCR] 图片尺寸调整: {original_size} -> {new_size}")
            
            # 增强对比度（提高文字清晰度）
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.3)
            
            # 增强锐度
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.2)
            
            # 轻度高斯模糊去噪
            img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # 再次增强对比度
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.1)
            
            # 保存预处理后的图片到临时文件
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                img.save(tmp.name, 'JPEG', quality=90)
                processed_path = tmp.name
            
            logger.debug(f"[OCR] 图片预处理完成: {image_path} -> {processed_path}")
            return processed_path
            
        except Exception as e:
            logger.warning(f"[OCR] 图片预处理失败，使用原图: {e}")
            return image_path
    
    def _recognize_with_paddleocr(self, image_path: str, language: str) -> Dict:
        """使用PaddleOCR识别文字"""
        try:
            # 确保PaddleOCR已初始化
            if not self._ocr_initialized:
                if not self._init_paddle_ocr(language):
                    return {
                        "success": False,
                        "error": "PaddleOCR初始化失败"
                    }
            
            start_time = time.time()
            
            # 检查图片大小，避免内存问题
            try:
                import os
                from PIL import Image
                
                # 检查文件大小
                file_size = os.path.getsize(image_path)
                if file_size > 5 * 1024 * 1024:  # 5MB
                    logger.warning(f"[OCR] 图片文件过大: {file_size/1024/1024:.1f}MB，强制缩小")
                    
                    # 强制缩小图片
                    img = Image.open(image_path)
                    max_size = 1200  # 更小的最大尺寸
                    if max(img.size) > max_size:
                        ratio = max_size / max(img.size)
                        new_size = tuple(int(dim * ratio) for dim in img.size)
                        img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        # 保存缩小后的图片
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                            img.save(tmp.name, 'JPEG', quality=80, optimize=True)
                            image_path = tmp.name
                            logger.info(f"[OCR] 图片已缩小: {img.size} -> {new_size}")
                
                # 检查图片尺寸
                img = Image.open(image_path)
                if img.size[0] * img.size[1] > 2000 * 2000:  # 400万像素
                    logger.warning(f"[OCR] 图片尺寸过大: {img.size[0]}x{img.size[1]}，强制缩小")
                    max_pixels = 2000 * 2000
                    ratio = (max_pixels / (img.size[0] * img.size[1])) ** 0.5
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                        img.save(tmp.name, 'JPEG', quality=80, optimize=True)
                        image_path = tmp.name
                        logger.info(f"[OCR] 图片像素过多，已缩小: {new_size}")
                        
            except Exception as e:
                logger.warning(f"[OCR] 图片大小检查失败: {e}")
            
            try:
                # 执行OCR识别（新版本PaddleOCR推荐使用predict方法）
                # 添加超时保护
                import signal
                
                class TimeoutException(Exception):
                    pass
                
                def timeout_handler(signum, frame):
                    raise TimeoutException("OCR识别超时")
                
                # 设置超时（30秒）
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(30)
                
                try:
                    result = self._paddle_ocr.predict(image_path)
                    signal.alarm(0)  # 取消超时
                    
                except TimeoutException:
                    logger.error("[OCR] OCR识别超时")
                    return {
                        "success": False,
                        "error": "OCR识别超时，请尝试使用较小的图片",
                        "engine": "paddleocr"
                    }
                except Exception as e:
                    signal.alarm(0)  # 取消超时
                    raise e
                
                execution_time = time.time() - start_time
                
                # 解析结果
                text_lines = []
                confidences = []
                positions = []
                
                try:
                    # 新版本PaddleOCR返回OCRResult对象，它是一个字典
                    ocr_result = result[0]
                    
                    # 检查是否有rec_texts和rec_scores字段
                    if hasattr(ocr_result, 'get'):
                        # 如果是字典或类似字典的对象
                        rec_texts = ocr_result.get('rec_texts', [])
                        rec_scores = ocr_result.get('rec_scores', [])
                        
                        if rec_texts and rec_scores and len(rec_texts) == len(rec_scores):
                            for i, (text, score) in enumerate(zip(rec_texts, rec_scores)):
                                text_lines.append(str(text))
                                confidences.append(float(score))
                                # 尝试获取位置信息
                                if 'rec_polys' in ocr_result and i < len(ocr_result['rec_polys']):
                                    positions.append(ocr_result['rec_polys'][i])
                                else:
                                    positions.append([])
                        else:
                            logger.warning(f"[OCR] 无效的识别结果: rec_texts={rec_texts}, rec_scores={rec_scores}")
                    else:
                        logger.warning(f"[OCR] 未知的结果格式: {type(ocr_result)}")
                except Exception as e:
                    logger.error(f"[OCR] 解析OCR结果时出错: {e}")
                    return {
                        "success": False,
                        "error": f"解析OCR结果失败: {str(e)}",
                        "engine": "paddleocr"
                    }
                
                # 合并文本
                text = "\n".join(text_lines)
                
                # 计算平均置信度
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # 识别语言检测（简单基于字符判断）
                detected_lang = self._detect_language(text)
                
                logger.info(f"[OCR] 识别完成: {len(text_lines)}行文字, 置信度: {avg_confidence:.2f}, 耗时: {execution_time:.2f}s")
                
                return {
                    "success": True,
                    "text": text,
                    "lines": text_lines,
                    "confidences": confidences,
                    "positions": positions,
                    "avg_confidence": avg_confidence,
                    "detected_language": detected_lang,
                    "execution_time": execution_time,
                    "line_count": len(text_lines),
                    "char_count": len(text),
                    "engine": "paddleocr"
                }
                
            except MemoryError as e:
                logger.error(f"[OCR] 内存不足: {e}")
                return {
                    "success": False,
                    "error": "内存不足，请尝试使用较小的图片",
                    "engine": "paddleocr"
                }
            except Exception as e:
                logger.error(f"[OCR] PaddleOCR识别失败: {e}")
                return {
                    "success": False,
                    "error": f"识别失败: {str(e)}",
                    "engine": "paddleocr"
                }
            
        except Exception as e:
            logger.error(f"[OCR] PaddleOCR识别失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "engine": "paddleocr"
            }
    
    def _detect_language(self, text: str) -> str:
        """简单语言检测"""
        if not text:
            return "unknown"
        
        # 统计中文字符
        chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
        total_chars = len(text)
        
        if total_chars == 0:
            return "unknown"
        
        chinese_ratio = chinese_chars / total_chars
        
        if chinese_ratio > 0.3:
            return "chinese"
        elif any(char.isalpha() for char in text):
            # 简单英文检测
            return "english"
        else:
            return "mixed"
    
    def _postprocess_text(self, ocr_result: Dict, recognize_type: str, extract_fields: List[str]) -> Dict:
        """文字后处理"""
        if not ocr_result.get("success"):
            return ocr_result
        
        text = ocr_result.get("text", "")
        lines = ocr_result.get("lines", [])
        
        # 基础清理
        cleaned_text = self._clean_text(text)
        cleaned_lines = [self._clean_text(line) for line in lines]
        
        # 根据识别类型进行特殊处理
        structured_data = {}
        extracted_fields_result = {}
        
        if recognize_type == "receipt":
            structured_data = self._parse_receipt(cleaned_text, cleaned_lines)
        elif recognize_type == "business_card":
            structured_data = self._parse_business_card(cleaned_text, cleaned_lines)
        elif recognize_type == "document":
            structured_data = self._parse_document(cleaned_text, cleaned_lines)
        elif recognize_type == "table":
            structured_data = self._parse_table(cleaned_text, cleaned_lines)
        
        # 提取特定字段
        if extract_fields:
            extracted_fields_result = self._extract_specific_fields(cleaned_text, extract_fields)
        
        return {
            "success": True,
            "original_text": text,
            "cleaned_text": cleaned_text,
            "cleaned_lines": cleaned_lines,
            "structured_data": structured_data,
            "extracted_fields": extracted_fields_result,
            "recognize_type": recognize_type,
            "language": ocr_result.get("detected_language", "unknown")
        }
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        import re
        
        if not text:
            return ""
        
        # 移除多余的空格和换行
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 纠正常见OCR错误
        corrections = {
            'O': '0',  # 字母O误识别为数字0
            'o': '0',  # 小写o误识别为数字0
            'l': '1',  # 字母l误识别为数字1
            'I': '1',  # 大写I误识别为数字1
            'i': '1',  # 小写i误识别为数字1
            'Z': '2',  # 字母Z误识别为数字2
            'z': '2',  # 小写z误识别为数字2
            'S': '5',  # 字母S误识别为数字5
            's': '5',  # 小写s误识别为数字5
            'B': '8',  # 字母B误识别为数字8
            'b': '6',  # 小写b误识别为数字6
            'g': '9',  # 小写g误识别为数字9
        }
        
        # 只替换单独出现的字符（避免影响正常单词）
        for wrong, correct in corrections.items():
            # 使用正则表达式匹配单独出现的字符
            text = re.sub(rf'\b{wrong}\b', correct, text)
        
        # 移除特殊字符但保留中文、英文、数字和常用标点
        text = re.sub(r'[^\w\u4e00-\u9fff\s.,，。!?！？:：;；"\'()（）\[\]【】《》<>{}]', '', text)
        
        return text.strip()
    
    def _parse_receipt(self, text: str, lines: List[str]) -> Dict:
        """解析发票/收据"""
        import re
        
        result = {
            "invoice_number": "",
            "date": "",
            "amount": "",
            "total_amount": "",
            "tax_amount": "",
            "seller": "",
            "seller_tax_id": "",
            "buyer": "",
            "buyer_tax_id": "",
            "items": [],
            "payment_method": ""
        }
        
        # 提取发票号码
        invoice_patterns = [
            r'发票号码[:：]?\s*([A-Z0-9]{8,20})',
            r'号码[:：]?\s*([A-Z0-9]{8,20})',
            r'No\.?\s*([A-Z0-9]{8,20})',
            r'发票代码[:：]?\s*([A-Z0-9]{10,20})'
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result["invoice_number"] = match.group(1)
                break
        
        # 提取日期
        date_patterns = [
            r'日期[:：]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
            r'开票日期[:：]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
            r'时间[:：]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
            r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                result["date"] = match.group(1)
                break
        
        # 提取金额
        amount_patterns = [
            r'金额[:：]?\s*[¥￥\$]?\s*([0-9,]+\.?[0-9]*)',
            r'合计[:：]?\s*[¥￥\$]?\s*([0-9,]+\.?[0-9]*)',
            r'总计[:：]?\s*[¥￥\$]?\s*([0-9,]+\.?[0-9]*)',
            r'[¥￥\$]\s*([0-9,]+\.?[0-9]*)',
            r'小计[:：]?\s*[¥￥\$]?\s*([0-9,]+\.?[0-9]*)'
        ]
        
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # 取最后一个匹配（通常是总计）
                result["total_amount"] = matches[-1]
                if len(matches) > 1:
                    result["amount"] = matches[0]
                break
        
        # 提取销售方
        seller_patterns = [
            r'销售方[:：]?\s*(.+)',
            r'卖方[:：]?\s*(.+)',
            r'开票方[:：]?\s*(.+)'
        ]
        
        for pattern in seller_patterns:
            match = re.search(pattern, text)
            if match:
                result["seller"] = match.group(1).strip()
                break
        
        # 提取购买方
        buyer_patterns = [
            r'购买方[:：]?\s*(.+)',
            r'买方[:：]?\s*(.+)',
            r'受票方[:：]?\s*(.+)'
        ]
        
        for pattern in buyer_patterns:
            match = re.search(pattern, text)
            if match:
                result["buyer"] = match.group(1).strip()
                break
        
        return result
    
    def _parse_business_card(self, text: str, lines: List[str]) -> Dict:
        """解析名片"""
        import re
        
        result = {
            "name": "",
            "title": "",
            "company": "",
            "department": "",
            "phone": [],
            "email": [],
            "address": "",
            "website": "",
            "wechat": "",
            "qq": ""
        }
        
        # 提取姓名（通常在第一行）
        if lines:
            # 第一行可能是姓名
            first_line = lines[0].strip()
            if len(first_line) <= 4 and not any(char.isdigit() for char in first_line):
                result["name"] = first_line
        
        # 提取电话
        phone_patterns = [
            r'(\d{3,4}[-—]\d{7,8})',  # 座机
            r'(\d{11})',  # 手机
            r'(1[3-9]\d{9})',  # 手机号
            r'电话[:：]?\s*([\d\-]+)',
            r'TEL[:：]?\s*([\d\-]+)',
            r'Phone[:：]?\s*([\d\-]+)'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match not in result["phone"]:
                    result["phone"].append(match)
        
        # 提取邮箱
        email_patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'邮箱[:：]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'Email[:：]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'E-mail[:：]?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        ]
        
        for pattern in email_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                if match not in result["email"]:
                    result["email"].append(match)
        
        # 提取公司名称
        company_keywords = ['公司', '有限公司', '集团', '科技', '技术', '股份', '企业']
        for line in lines:
            for keyword in company_keywords:
                if keyword in line and len(line) > 2:
                    result["company"] = line.strip()
                    break
            if result["company"]:
                break
        
        # 提取职位
        title_keywords = ['经理', '总监', '主管', '工程师', '顾问', '代表', '助理', '主任']
        for line in lines:
            for keyword in title_keywords:
                if keyword in line:
                    result["title"] = line.strip()
                    break
            if result["title"]:
                break
        
        return result
    
    def _parse_document(self, text: str, lines: List[str]) -> Dict:
        """解析文档"""
        result = {
            "title": "",
            "author": "",
            "date": "",
            "sections": [],
            "paragraphs": len(lines),
            "word_count": len(text.split())
        }
        
        # 第一行可能是标题
        if lines:
            first_line = lines[0].strip()
            if len(first_line) > 3 and len(first_line) < 50:
                result["title"] = first_line
        
        return result
    
    def _parse_table(self, text: str, lines: List[str]) -> Dict:
        """解析表格"""
        result = {
            "rows": len(lines),
            "columns": 0,
            "data": lines,
            "has_header": False
        }
        
        # 简单判断是否有表头（第一行包含冒号、冒号等）
        if lines:
            first_line = lines[0]
            if any(sep in first_line for sep in [':', '：', '|', '\t']):
                result["has_header"] = True
        
        return result
    
    def _extract_specific_fields(self, text: str, fields: List[str]) -> Dict:
        """提取特定字段"""
        import re
        
        result = {}
        
        field_patterns = {
            "invoice_number": r'发票号码[:：]?\s*([A-Z0-9]{8,20})',
            "amount": r'金额[:：]?\s*[¥￥\$]?\s*([0-9,]+\.?[0-9]*)',
            "date": r'日期[:：]?\s*(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)',
            "phone": r'(1[3-9]\d{9})',
            "email": r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            "name": r'姓名[:：]?\s*(.{2,4})',
            "company": r'公司[:：]?\s*(.+)',
            "address": r'地址[:：]?\s*(.+)'
        }
        
        for field in fields:
            if field in field_patterns:
                pattern = field_patterns[field]
                match = re.search(pattern, text)
                if match:
                    result[field] = match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return result
    
    def execute(self, arguments: Dict) -> ToolResult:
        """执行OCR识别（同步版本）"""
        import asyncio
        
        # 使用asyncio运行异步版本
        try:
            return asyncio.run(self._execute_async(arguments))
        except Exception as e:
            logger.error(f"[OCR] 同步执行异常: {e}", exc_info=True)
            return ToolResult.fail(f"OCR工具执行异常: {str(e)}")
    
    async def _execute_async(self, arguments: Dict) -> ToolResult:
        """异步执行OCR识别"""
        try:
            # 获取参数
            image_path = arguments.get("image_path")
            language = arguments.get("language", "ch")
            recognize_type = arguments.get("recognize_type", "general")
            preprocess = arguments.get("preprocess", True)
            extract_fields = arguments.get("extract_fields", [])
            return_format = arguments.get("return_format", "both")
            
            # 验证参数
            if not image_path:
                return ToolResult.fail("请提供图片路径参数: image_path")
            
            if not os.path.exists(image_path):
                return ToolResult.fail(f"图片文件不存在: {image_path}")
            
            # 验证图片格式
            allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
            file_ext = os.path.splitext(image_path.lower())[1]
            if file_ext not in allowed_extensions:
                return ToolResult.fail(f"不支持的图片格式: {file_ext}。支持格式: {', '.join(allowed_extensions)}")
            
            logger.info(f"[OCR] 开始识别图片: {image_path}, 语言: {language}, 类型: {recognize_type}")
            
            # 图片预处理
            processed_path = image_path
            if preprocess:
                processed_path = self._preprocess_image(image_path)
                logger.debug(f"[OCR] 图片预处理完成: {processed_path}")
            
            # OCR识别 - 优先使用百度OCR，失败时使用PaddleOCR
            ocr_result = None
            engine_used = "unknown"
            
            # 首先尝试百度OCR
            if self._baidu_ocr_config['enabled']:
                logger.info("[OCR] 尝试使用百度OCR识别...")
                ocr_result = self._recognize_with_baidu_ocr(processed_path, language, recognize_type)
                engine_used = "baidu_ocr"
            
            # 如果百度OCR失败或未启用，尝试PaddleOCR
            if not ocr_result or not ocr_result.get("success"):
                if engine_used == "baidu_ocr":
                    logger.warning(f"[OCR] 百度OCR识别失败，尝试使用PaddleOCR: {ocr_result.get('error', '未知错误') if ocr_result else '无结果'}")
                
                logger.info("[OCR] 尝试使用PaddleOCR识别...")
                ocr_result = self._recognize_with_paddleocr(processed_path, language)
                engine_used = "paddleocr"
            
            if not ocr_result.get("success"):
                error_msg = ocr_result.get("error", "OCR识别失败")
                return ToolResult.fail(f"OCR识别失败: {error_msg}")
            
            # 文字后处理
            processed_result = self._postprocess_text(ocr_result, recognize_type, extract_fields)
            
            # 清理临时文件
            if preprocess and processed_path != image_path and os.path.exists(processed_path):
                try:
                    os.unlink(processed_path)
                    logger.debug(f"[OCR] 清理临时文件: {processed_path}")
                except:
                    pass
            
            # 构建返回结果
            result_data = {
                "success": True,
                "image_info": {
                    "path": image_path,
                    "size": os.path.getsize(image_path),
                    "format": file_ext
                },
                "ocr_info": {
                    "engine": engine_used,
                    "language": language,
                    "recognize_type": recognize_type,
                    "confidence": ocr_result.get("avg_confidence", 0),
                    "execution_time": ocr_result.get("execution_time", 0),
                    "line_count": ocr_result.get("line_count", 0),
                    "char_count": ocr_result.get("char_count", 0),
                    "detected_language": ocr_result.get("detected_language", "unknown")
                }
            }
            
            # 根据返回格式添加内容
            if return_format in ["text", "both"]:
                result_data["text"] = processed_result.get("cleaned_text", "")
                result_data["lines"] = processed_result.get("cleaned_lines", [])
            
            if return_format in ["structured", "both"]:
                result_data["structured_data"] = processed_result.get("structured_data", {})
                result_data["extracted_fields"] = processed_result.get("extracted_fields", {})
            
            logger.info(f"[OCR] 识别成功: 引擎={engine_used}, {result_data['ocr_info']['line_count']}行, {result_data['ocr_info']['char_count']}字符, 置信度: {result_data['ocr_info']['confidence']:.2f}")
            
            return ToolResult.success(result_data)
            
        except Exception as e:
            logger.error(f"[OCR] 工具执行异常: {e}", exc_info=True)
            return ToolResult.fail(f"OCR工具执行异常: {str(e)}")
    
    def cleanup(self):
        """清理资源"""
        if self._paddle_ocr:
            try:
                # PaddleOCR没有显式的清理方法
                self._paddle_ocr = None
                self._ocr_initialized = False
                logger.info("[OCR] 资源已清理")
            except:
                pass
