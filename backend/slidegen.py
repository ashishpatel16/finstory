"""
PowerPoint Presentation Generator
Creates beautiful PPTX presentations from JSON input
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from typing import List, Dict, Any, Optional
import json


class SlideGenerator:
    """Generates PowerPoint presentations from JSON data"""
    
    # Beautiful color scheme
    COLORS = {
        'primary': RGBColor(41, 128, 185),      # Blue
        'secondary': RGBColor(52, 73, 94),       # Dark gray
        'accent': RGBColor(46, 204, 113),        # Green
        'text': RGBColor(44, 62, 80),            # Dark text
        'light_bg': RGBColor(236, 240, 241),    # Light gray background
        'white': RGBColor(255, 255, 255),
        'orange': RGBColor(230, 126, 34),       # Orange
        'red': RGBColor(231, 76, 60),            # Red
    }
    
    def __init__(self, width: float = 10.0, height: float = 7.5):
        """
        Initialize the presentation generator
        
        Args:
            width: Slide width in inches (default: 10.0 for widescreen)
            height: Slide height in inches (default: 7.5 for widescreen)
        """
        self.prs = Presentation()
        self.prs.slide_width = Inches(width)
        self.prs.slide_height = Inches(height)
    
    def _add_title_slide(self, title: str, subtitle: Optional[str] = None):
        """Create a title slide with beautiful styling"""
        slide_layout = self.prs.slide_layouts[6]  # Blank layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Add background shape
        left = top = Inches(0)
        width = self.prs.slide_width
        height = self.prs.slide_height
        background = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, left, top, width, height
        )
        background.fill.solid()
        background.fill.fore_color.rgb = self.COLORS['primary']
        background.line.fill.background()
        
        # Add title
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(2.5), Inches(9), Inches(1.5)
        )
        title_frame = title_box.text_frame
        title_frame.text = title
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(54)
        title_para.font.bold = True
        title_para.font.color.rgb = self.COLORS['white']
        title_para.alignment = PP_ALIGN.CENTER
        
        # Add subtitle if provided
        if subtitle:
            subtitle_box = slide.shapes.add_textbox(
                Inches(0.5), Inches(4.5), Inches(9), Inches(1)
            )
            subtitle_frame = subtitle_box.text_frame
            subtitle_frame.text = subtitle
            subtitle_para = subtitle_frame.paragraphs[0]
            subtitle_para.font.size = Pt(28)
            subtitle_para.font.color.rgb = self.COLORS['light_bg']
            subtitle_para.alignment = PP_ALIGN.CENTER
        
        return slide
    
    def _add_content_slide(self, title: str, content: Any):
        """Create a content slide with various content types"""
        slide_layout = self.prs.slide_layouts[6]  # Blank layout
        slide = self.prs.slides.add_slide(slide_layout)
        
        # Add title bar
        title_bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), 
            self.prs.slide_width, Inches(1.2)
        )
        title_bar.fill.solid()
        title_bar.fill.fore_color.rgb = self.COLORS['primary']
        title_bar.line.fill.background()
        
        # Add title text
        title_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(0.2), Inches(9), Inches(0.8)
        )
        title_frame = title_box.text_frame
        title_frame.text = title
        title_para = title_frame.paragraphs[0]
        title_para.font.size = Pt(36)
        title_para.font.bold = True
        title_para.font.color.rgb = self.COLORS['white']
        title_para.alignment = PP_ALIGN.LEFT
        
        # Add content based on type
        content_top = Inches(1.8)
        
        if isinstance(content, list):
            # Bullet points
            self._add_bullet_points(slide, content, content_top)
        elif isinstance(content, dict):
            # Structured content
            if 'type' in content:
                if content['type'] == 'text':
                    self._add_text_content(slide, content.get('text', ''), content_top)
                elif content['type'] == 'bullets':
                    self._add_bullet_points(slide, content.get('items', []), content_top)
                elif content['type'] == 'two_column':
                    self._add_two_column(slide, content.get('left', []), 
                                       content.get('right', []), content_top)
            else:
                # Key-value pairs
                self._add_key_value_pairs(slide, content, content_top)
        else:
            # Plain text
            self._add_text_content(slide, str(content), content_top)
        
        return slide
    
    def _add_bullet_points(self, slide, items: List[str], top: float):
        """Add bullet points to slide"""
        text_box = slide.shapes.add_textbox(
            Inches(0.8), top, Inches(8.4), Inches(5)
        )
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        for i, item in enumerate(items):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            
            p.text = item
            p.level = 0
            p.font.size = Pt(20)
            p.font.color.rgb = self.COLORS['text']
            p.space_after = Pt(12)
    
    def _add_text_content(self, slide, text: str, top: float):
        """Add plain text content to slide"""
        text_box = slide.shapes.add_textbox(
            Inches(0.8), top, Inches(8.4), Inches(5)
        )
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        text_frame.text = text
        
        para = text_frame.paragraphs[0]
        para.font.size = Pt(20)
        para.font.color.rgb = self.COLORS['text']
        para.alignment = PP_ALIGN.LEFT
    
    def _add_two_column(self, slide, left_items: List[str], right_items: List[str], top: float):
        """Add two-column layout"""
        # Left column
        left_box = slide.shapes.add_textbox(
            Inches(0.8), top, Inches(4), Inches(5)
        )
        left_frame = left_box.text_frame
        left_frame.word_wrap = True
        
        for i, item in enumerate(left_items):
            if i == 0:
                p = left_frame.paragraphs[0]
            else:
                p = left_frame.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(18)
            p.font.color.rgb = self.COLORS['text']
            p.space_after = Pt(10)
        
        # Right column
        right_box = slide.shapes.add_textbox(
            Inches(5.2), top, Inches(4), Inches(5)
        )
        right_frame = right_box.text_frame
        right_frame.word_wrap = True
        
        for i, item in enumerate(right_items):
            if i == 0:
                p = right_frame.paragraphs[0]
            else:
                p = right_frame.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(18)
            p.font.color.rgb = self.COLORS['text']
            p.space_after = Pt(10)
    
    def _add_key_value_pairs(self, slide, data: Dict[str, Any], top: float):
        """Add key-value pairs in a structured format"""
        text_box = slide.shapes.add_textbox(
            Inches(0.8), top, Inches(8.4), Inches(5)
        )
        text_frame = text_box.text_frame
        text_frame.word_wrap = True
        
        for i, (key, value) in enumerate(data.items()):
            if i == 0:
                p = text_frame.paragraphs[0]
            else:
                p = text_frame.add_paragraph()
            
            p.text = f"{key}: {value}"
            p.font.size = Pt(20)
            p.font.color.rgb = self.COLORS['text']
            p.space_after = Pt(14)
            p.space_before = Pt(8)
    
    def generate_from_json(self, slides_data: List[Dict[str, Any]]) -> Presentation:
        """
        Generate presentation from JSON data
        
        Args:
            slides_data: List of slide dictionaries, each containing:
                - type: 'title' or 'content'
                - title: Slide title (required)
                - subtitle: Subtitle (for title slides)
                - content: Content (for content slides) - can be:
                    - String
                    - List of strings (bullet points)
                    - Dict with 'type' key ('text', 'bullets', 'two_column')
                    - Dict of key-value pairs
        
        Returns:
            Presentation object
        """
        for slide_data in slides_data:
            slide_type = slide_data.get('type', 'content')
            title = slide_data.get('title', 'Untitled')
            
            if slide_type == 'title':
                subtitle = slide_data.get('subtitle')
                self._add_title_slide(title, subtitle)
            else:
                content = slide_data.get('content', '')
                self._add_content_slide(title, content)
        
        return self.prs
    
    def save(self, filename: str):
        """Save the presentation to a file"""
        self.prs.save(filename)


def generate_pptx_from_json(json_data: str, output_path: str) -> str:
    """
    Convenience function to generate PPTX from JSON string
    
    Args:
        json_data: JSON string containing slides data
        output_path: Path where the PPTX file should be saved
    
    Returns:
        Path to the saved file
    """
    slides_data = json.loads(json_data)
    generator = SlideGenerator()
    generator.generate_from_json(slides_data)
    generator.save(output_path)
    return output_path


def generate_pptx_from_dict(slides_data: List[Dict[str, Any]], output_path: str) -> str:
    """
    Convenience function to generate PPTX from Python dictionary
    
    Args:
        slides_data: List of dictionaries containing slide data
        output_path: Path where the PPTX file should be saved
    
    Returns:
        Path to the saved file
    """
    generator = SlideGenerator()
    generator.generate_from_json(slides_data)
    generator.save(output_path)
    return output_path


# Example usage
if __name__ == "__main__":
    # Example JSON structure
    example_slides = [
        {
            "type": "title",
            "title": "Welcome to Finstory",
            "subtitle": "Financial Storytelling Made Easy"
        },
        {
            "type": "content",
            "title": "Overview",
            "content": [
                "Financial data analysis and visualization",
                "Automated report generation",
                "Beautiful presentation creation",
                "Data-driven insights"
            ]
        },
        {
            "type": "content",
            "title": "Key Features",
            "content": {
                "type": "two_column",
                "left": [
                    "Real-time data processing",
                    "Advanced analytics",
                    "Custom templates"
                ],
                "right": [
                    "Export to multiple formats",
                    "Collaborative editing",
                    "Secure data handling"
                ]
            }
        },
        {
            "type": "content",
            "title": "Statistics",
            "content": {
                "Total Users": "10,000+",
                "Data Points": "1M+",
                "Reports Generated": "50K+",
                "Accuracy": "99.9%"
            }
        }
    ]
    
    # Generate presentation
    generator = SlideGenerator()
    generator.generate_from_json(example_slides)
    generator.save("example_presentation.pptx")
    print("Presentation generated: example_presentation.pptx")

slides = [{"type": "title", "title": "Hello", "subtitle": "World"}]
generate_pptx_from_dict(slides, "output.pptx")