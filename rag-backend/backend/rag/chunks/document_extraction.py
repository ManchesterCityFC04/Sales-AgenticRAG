import requests
import os
import time
import json
from docx import Document
import PyPDF2
from typing import Optional
from dotenv import load_dotenv
import zipfile
import uuid
from urllib.parse import urlparse
from .models import DocumentContent

class DocumentExtractor:
    def __init__(self):
        """初始化文档提取器，从环境变量获取API配置"""
        load_dotenv()
    
    def _extract_document_name(self, file_path: str) -> str:
        """从文件路径提取文档名称"""
        return os.path.basename(file_path)
    
    def read_document(self, file_path: str, pdf_extract_method: str = "pypdf2") -> DocumentContent:
        """读取不同格式的文档内容
        
        Args:
            file_path: 文件路径
            pdf_extract_method: PDF提取方式，可选"pypdf2"或"mineru"
        """
        file_extension = file_path.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            if pdf_extract_method == "pypdf2":
                # 使用PyPDF2读取PDF
                try:
                    with open(file_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        text = ""
                        for page_num in range(len(reader.pages)):
                            text += reader.pages[page_num].extract_text()
                        return DocumentContent(
                            content=text,
                            document_name=self._extract_document_name(file_path)
                        )
                except Exception as e:
                    raise Exception(f"PDF处理错误(PyPDF2): {str(e)}")
            elif pdf_extract_method == "mineru":
                # 使用mineru API读取PDF
                try:
                    # 注意：MinerU官方API需要PDF文件的URL，不支持直接文件上传
                    # 如果file_path是URL，直接使用；否则需要先上传文件获取URL
                    if file_path.startswith(('http://', 'https://')):
                        pdf_url=file_path
                        text = self._extract_pdf_with_mineru(pdf_url)
                        return DocumentContent(
                            content=text,
                            document_name=self._extract_document_name(file_path)
                        )
                    else:
                        raise ValueError("MinerU API需要PDF文件的URL地址，请提供有效的HTTP/HTTPS URL")
                except Exception as e:
                    raise Exception(f"PDF处理错误(mineru): {str(e)}")
            else:
                raise ValueError(f"不支持的PDF提取方式: {pdf_extract_method}")
                
        elif file_extension == 'doc' or file_extension == 'docx':
            # 读取Word文档
            try:
                doc = Document(file_path)
                text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                return DocumentContent(
                    content=text,
                    document_name=self._extract_document_name(file_path)
                )
            except Exception as e:
                raise Exception(f"Word文档处理错误: {str(e)}")
                
        elif file_extension == 'md':
            # 读取Markdown文件
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    return DocumentContent(
                        content=text,
                        document_name=self._extract_document_name(file_path)
                    )
            except Exception as e:
                raise Exception(f"Markdown文件处理错误: {str(e)}")
                
        else:
            raise ValueError(f"不支持的文件格式: {file_extension}")
    
    def _extract_pdf_with_mineru(self, pdf_url: Optional[str] = None) -> str:
        """使用mineru API提取PDF文本
        
        Args:
            pdf_url: PDF文件的URL地址（如果提供，将优先使用URL而不是本地文件）
            
        Returns:
            提取的文本内容
        """
        # 从环境变量或实例变量获取API配置
        api_url =os.getenv('MINERU_API_URL')
        api_key =os.getenv('MINERU_API_KEY')
        
        if not api_key:
            raise ValueError("请设置环境变量 MINERU_API_KEY 或在初始化时提供API密钥")
        
        # 使用官方API端点
        task_url = f"{api_url.rstrip('/')}/extract/task"
        
        # 准备请求头
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        try:
            # 如果没有提供URL，需要先上传文件获取URL（这里简化处理，实际可能需要额外的文件上传服务）
            # 他这个接口就只能提供URL，不能直接上传文件，大概是不会有这个问题
            if not pdf_url:
                raise ValueError("MinerU官方API需要PDF文件的URL地址，不支持直接文件上传。请先将文件上传到可访问的URL")
            
            # 准备请求数据
            data = {
                'url': pdf_url,
                'is_ocr': True,  # 启用OCR识别
                'enable_formula': True  # 是否启用公式识别
            }
            
            # 创建解析任务
            response = requests.post(
                task_url,
                headers=headers,
                json=data
            )
            
            response.raise_for_status()
            
            # 解析响应
            result = response.json()
            
            if result.get('code') != 0:
                error_msg = result.get('msg', '创建任务失败')
                raise Exception(f"MinerU任务创建失败: {error_msg}")
            
            # 获取任务ID
            task_data = result.get('data', {})
            task_id = task_data.get('task_id')
            
            if not task_id:
                raise Exception("未获得有效的任务ID")
            
            # 轮询获取处理结果
            return self._poll_mineru_task_result(task_id)
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"MinerU API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"MinerU API返回的不是有效的JSON格式: {str(e)}")
        except Exception as e:
            raise Exception(f"MinerU处理过程中发生错误: {str(e)}")
    
    def _poll_mineru_task_result(self, task_id: str, max_wait_time: int = 300) -> str:
        """轮询MinerU任务处理结果
        
        Args:
            task_id: 任务ID
            max_wait_time: 最大等待时间（秒）
            
        Returns:
            提取的文本内容
        """
        
        # 从环境变量或实例变量获取API配置
        api_url =os.getenv('MINERU_API_URL')
        api_key =os.getenv('MINERU_API_KEY')
        
        result_url = f"{api_url.rstrip('/')}/extract/task/{task_id}"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(result_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get('code') != 0:
                    error_msg = result.get('msg', '查询结果失败')
                    raise Exception(f"查询任务结果失败: {error_msg}")
                
                task_data = result.get('data', {})
                state = task_data.get('state')
                
                if state == 'done':
                    # 任务完成，获取结果压缩包URL
                    full_zip_url = task_data.get('full_zip_url', '')
                    if full_zip_url:
                        # 检测返回的是否为zip文件URL
                        if full_zip_url.lower().endswith('.zip'):
                            return self._download_and_extract_mineru_result(full_zip_url)
                        else:
                            return f"解析完成，结果文件: {full_zip_url}"
                    else:
                        return "解析完成，但未获取到结果文件URL"
                elif state == 'failed':
                    error_msg = task_data.get('err_msg', '解析失败')
                    raise Exception(f"MinerU解析失败: {error_msg}")
                elif state in ['pending', 'running', 'converting']:
                    # 任务还在处理中，等待后重试
                    if state == 'running':
                        # 显示进度信息
                        progress = task_data.get('extract_progress', {})
                        extracted_pages = progress.get('extracted_pages', 0)
                        total_pages = progress.get('total_pages', 0)
                        print(f"解析进度: {extracted_pages}/{total_pages} 页")
                    time.sleep(5)  # 等待5秒后重试
                    continue
                else:
                    raise Exception(f"未知的任务状态: {state}")
                    
            except requests.exceptions.RequestException as e:
                raise Exception(f"查询处理结果失败: {str(e)}")
        
        raise Exception(f"处理超时，超过{max_wait_time}秒未完成")
    
    def _download_and_extract_mineru_result(self, zip_url: str) -> str:
        """下载并解压MinerU结果文件，读取full.md内容
        
        Args:
            zip_url: zip文件的URL地址
            
        Returns:
            full.md文件的内容
        """
        try:
            # 创建输出目录
            zip_output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'mineru_zip')
            extract_output_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', 'mineru')
            
            os.makedirs(zip_output_dir, exist_ok=True)
            os.makedirs(extract_output_dir, exist_ok=True)
            
            # 从URL中提取文件名
            parsed_url = urlparse(zip_url)
            zip_filename = os.path.basename(parsed_url.path)
            if not zip_filename.endswith('.zip'):
                 # 如果URL中没有文件名，生成一个唯一的文件名
                 zip_filename = f"mineru_result_{uuid.uuid4().hex[:8]}.zip"
             
            zip_file_path = os.path.join(zip_output_dir, zip_filename)
             
            # 下载zip文件
            print(f"正在下载MinerU结果文件: {zip_url}")
            response = requests.get(zip_url, stream=True, timeout=60)
            response.raise_for_status()
             
            with open(zip_file_path, 'wb') as f:
                 for chunk in response.iter_content(chunk_size=8192):
                     if chunk:
                         f.write(chunk)
             
            print(f"下载完成: {zip_file_path}")
             
             # 解压zip文件，保留zip文件名作为文件夹名
            zip_name_without_ext = os.path.splitext(zip_filename)[0]
            extract_target_dir = os.path.join(extract_output_dir, zip_name_without_ext)
             
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                 zip_ref.extractall(extract_target_dir)
             
            print(f"解压完成到: {extract_target_dir}")
             
             # 更新解压目录为新的目标目录
            extract_output_dir = extract_target_dir
            
            # 查找并读取full.md文件
            # 首先尝试在解压目录中查找full.md文件
            full_md_path = None
            
            # 遍历解压目录查找full.md文件
            for root, dirs, files in os.walk(extract_output_dir):
                for file in files:
                    if file == 'full.md':
                        full_md_path = os.path.join(root, file)
                        break
                if full_md_path:
                    break
            
            if not full_md_path:
                # 如果没找到full.md，列出所有文件供调试
                all_files = []
                for root, dirs, files in os.walk(extract_output_dir):
                    for file in files:
                        all_files.append(os.path.join(root, file))
                raise Exception(f"未找到full.md文件。解压后的文件列表: {all_files}")
            
            # 读取full.md文件内容
            with open(full_md_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"成功读取full.md文件: {full_md_path}")
            return content
        except requests.exceptions.RequestException as e:
            raise Exception(f"下载zip文件失败: {str(e)}")
        except zipfile.BadZipFile as e:
            raise Exception(f"zip文件损坏或格式错误: {str(e)}")
        except FileNotFoundError as e:
            raise Exception(f"文件未找到: {str(e)}")
        except Exception as e:
            raise Exception(f"处理MinerU结果文件时发生错误: {str(e)}")
    
# 使用示例
if __name__ == "__main__":
    # 创建文档提取器实例
    extractor = DocumentExtractor()
    
    # 示例：提取PDF文档内容
    try:
        #  # 使用PyPDF2提取本地文件
        #  text_pypdf2 = extractor.read_document(r"D:\代码\python\rag\project\backend\rag\chunks\example.pdf", pdf_extract_method="pypdf2")
        #  print("PyPDF2提取结果:", text_pypdf2[:200] + "...")
         
         # 使用MinerU API提取（需要PDF文件的URL地址）
         pdf_url = "https://cdn-mineru.openxlab.org.cn/demo/example.pdf"
         text_mineru = extractor.read_document(pdf_url, pdf_extract_method="mineru")
         #print("MinerU提取结果:", text_mineru)
         
    except Exception as e:
         print(f"文档提取失败: {e}")
    
    # # 示例：提取Word文档内容
    # try:
    #     text_word = extractor.read_document(r"D:\代码\python\rag\project\backend\rag\chunks\test_word.docx")
    #     print("Word文档提取结果:", text_word[:200] + "...")
    # except Exception as e:
    #     print(f"Word文档提取失败: {e}")
    
    # # 示例：提取Markdown文档内容
    # try:
    #     text_md = extractor.read_document(r"D:\代码\python\rag\project\backend\rag\chunks\example.md")
    #     print("Markdown文档提取结果:", text_md[:200] + "...")
    # except Exception as e:
    #     print(f"Markdown文档提取失败: {e}")
