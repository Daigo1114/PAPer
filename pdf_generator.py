import os
import time
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.colors import black, darkblue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import markdown
from bs4 import BeautifulSoup
import re

class PDFGenerator:
    """
    PDF文档生成器
    将工作流输出的内容转换为格式化的PDF文档
    """
    
    def __init__(self):
        self.setup_fonts()
        
    def setup_fonts(self):
        """
        设置中文字体（如果可用）
        """
        try:
            # 尝试注册常见的中文字体
            font_paths = [
                '/System/Library/Fonts/PingFang.ttc',  # macOS
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
                'C:/Windows/Fonts/simsun.ttc',  # Windows
                'C:/Windows/Fonts/simhei.ttf',  # Windows
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                        self.has_chinese_font = True
                        break
                    except:
                        continue
            else:
                self.has_chinese_font = False
                
        except Exception as e:
            print(f"字体设置失败: {e}")
            self.has_chinese_font = False
    
    def create_styles(self):
        """
        创建PDF样式
        """
        styles = getSampleStyleSheet()
        
        # 标题样式
        if self.has_chinese_font:
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontName='ChineseFont',
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
                textColor=darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontName='ChineseFont',
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12,
                textColor=black
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName='ChineseFont',
                fontSize=12,
                spaceAfter=6,
                leading=18
            )
        else:
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Title'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,
                textColor=darkblue
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading1'],
                fontSize=14,
                spaceAfter=12,
                spaceBefore=12,
                textColor=black
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=12,
                spaceAfter=6,
                leading=18
            )
        
        return {
            'title': title_style,
            'heading': heading_style,
            'normal': normal_style
        }
    
    def parse_content(self, content: str):
        """
        解析内容，支持markdown格式
        """
        # 如果内容包含markdown标记，转换为HTML
        if '#' in content or '*' in content or '-' in content:
            html_content = markdown.markdown(content)
            soup = BeautifulSoup(html_content, 'html.parser')
            return self.parse_html_elements(soup)
        else:
            # 纯文本内容，按段落分割
            paragraphs = content.split('\n\n')
            return [{'type': 'paragraph', 'content': p.strip()} for p in paragraphs if p.strip()]
    
    def parse_html_elements(self, soup):
        """
        解析HTML元素
        """
        elements = []
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'p', 'div']):
            if element.name in ['h1', 'h2', 'h3']:
                elements.append({
                    'type': 'heading',
                    'level': int(element.name[1]),
                    'content': element.get_text().strip()
                })
            elif element.name in ['p', 'div']:
                text = element.get_text().strip()
                if text:
                    elements.append({
                        'type': 'paragraph',
                        'content': text
                    })
        
        return elements
    
    def generate_pdf(self, content: str, subject: str, question_types: list, 
                    filename: Optional[str] = None) -> str:
        """
        生成PDF文档
        
        Args:
            content: 要转换的内容
            subject: 学科科目
            question_types: 题型列表
            filename: 输出文件名（可选）
            
        Returns:
            生成的PDF文件路径
        """
        if not filename:
            timestamp = int(time.time())
            filename = f"exam_questions_{timestamp}.pdf"
        
        # 确保文件名以.pdf结尾
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        # 创建PDF文档
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # 创建样式
        styles = self.create_styles()
        
        # 构建文档内容
        story = []
        
        # 添加标题
        title_text = f"{subject} - 试题生成"
        story.append(Paragraph(title_text, styles['title']))
        story.append(Spacer(1, 20))
        
        # 添加基本信息
        info_text = f"题型：{', '.join(question_types)}"
        story.append(Paragraph(info_text, styles['normal']))
        
        generation_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        time_text = f"生成时间：{generation_time}"
        story.append(Paragraph(time_text, styles['normal']))
        story.append(Spacer(1, 30))
        
        # 解析并添加主要内容
        elements = self.parse_content(content)
        
        question_number = 1
        
        for element in elements:
            if element['type'] == 'heading':
                story.append(Paragraph(element['content'], styles['heading']))
                story.append(Spacer(1, 12))
            elif element['type'] == 'paragraph':
                # 检查是否是题目（简单的启发式判断）
                content_text = element['content']
                
                # 如果段落看起来像是一个问题，添加题号
                if (content_text.endswith('？') or content_text.endswith('?') or 
                    '选择' in content_text or '填空' in content_text or 
                    '简答' in content_text or '编程' in content_text):
                    formatted_text = f"{question_number}. {content_text}"
                    question_number += 1
                else:
                    formatted_text = content_text
                
                story.append(Paragraph(formatted_text, styles['normal']))
                story.append(Spacer(1, 8))
        
        # 如果内容为空，添加默认内容
        if not elements:
            story.append(Paragraph("暂无生成内容", styles['normal']))
        
        # 生成PDF
        try:
            doc.build(story)
            print(f"PDF文档已生成: {filename}")
            return filename
        except Exception as e:
            print(f"PDF生成失败: {e}")
            raise e
    
    def clean_old_files(self, max_age_hours: int = 24):
        """
        清理旧的PDF文件
        
        Args:
            max_age_hours: 文件最大保留时间（小时）
        """
        current_time = time.time()
        
        for filename in os.listdir('.'):
            if filename.startswith('exam_questions_') and filename.endswith('.pdf'):
                file_path = os.path.join('.', filename)
                try:
                    file_age = current_time - os.path.getctime(file_path)
                    if file_age > max_age_hours * 3600:  # 转换为秒
                        os.remove(file_path)
                        print(f"已删除旧文件: {filename}")
                except Exception as e:
                    print(f"删除文件失败 {filename}: {e}")


def create_sample_pdf():
    """
    创建示例PDF文档
    """
    generator = PDFGenerator()
    
    sample_content = """
    # 数据库原理试题

    ## 选择题

    1. 关系数据库中，用来表示实体之间联系的是？
    A. 属性  B. 关系  C. 元组  D. 域

    2. SQL语言中，用于查询数据的语句是？
    A. INSERT  B. UPDATE  C. SELECT  D. DELETE

    ## 简答题

    1. 请简述数据库事务的ACID特性。

    2. 解释什么是数据库的三级模式结构？

    ## 综合题

    1. 给定关系模式R(A,B,C,D)，函数依赖集F={A→B, B→C, C→D}，请分析该关系模式的范式等级。
    """
    
    filename = generator.generate_pdf(
        content=sample_content,
        subject="数据库原理",
        question_types=["选择题", "简答题", "综合题"]
    )
    
    return filename

if __name__ == "__main__":
    # 测试PDF生成
    create_sample_pdf()