from crewai.tools import BaseTool
from typing import Type, Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re
import json
from lxml import etree
from bs4 import BeautifulSoup
import colorsys


class GradientSpecification(BaseModel):
    """Structured output for gradient specifications"""
    gradient_type: str = Field(description="Type of gradient: 'linear' or 'radial'")
    direction: str = Field(description="Direction or angle of gradient")
    colors: List[Dict[str, Any]] = Field(description="List of color stops with positions")
    additional_properties: Dict[str, Any] = Field(default_factory=dict, description="Special styling requirements")
    target_elements: List[str] = Field(description="SVG elements to apply gradient to")


class ValidationReport(BaseModel):
    """Structured output for SVG validation"""
    syntax_valid: bool = Field(description="Whether SVG syntax is valid")
    accessibility_score: int = Field(description="Accessibility rating 1-10")
    visual_quality_assessment: str = Field(description="Detailed visual quality analysis")
    recommendations: List[str] = Field(description="List of improvement recommendations")
    final_approval: bool = Field(description="Whether output meets standards")


class GradientAnalysisToolInput(BaseModel):
    instruction: str = Field(description="Natural language instruction describing the gradient")

class GradientAnalysisTool(BaseTool):
    name: str = "gradient_analysis_tool"
    description: str = "Analyzes natural language descriptions to extract gradient specifications"
    args_schema: Type[BaseModel] = GradientAnalysisToolInput
    
    def _run(self, instruction: str) -> str:
        """Parse natural language gradient instructions"""
        
        
        spec = {
            "gradient_type": "linear",
            "direction": "to right",
            "colors": [],
            "additional_properties": {},
            "target_elements": ["rect", "circle", "path"]
        }
        
        instruction_lower = instruction.lower()
        
       
        if any(word in instruction_lower for word in ["radial", "circular", "center", "radius"]):
            spec["gradient_type"] = "radial"
        
        
        direction_patterns = {
            r"to\s+(right|left|top|bottom)": r"\1",
            r"(\d+)\s*deg": r"\1deg",
            r"(horizontal|vertical)": lambda m: "to right" if m.group(1) == "horizontal" else "to bottom",
            r"diagonal": "45deg"
        }
        
        for pattern, replacement in direction_patterns.items():
            match = re.search(pattern, instruction_lower)
            if match:
                if callable(replacement):
                    spec["direction"] = replacement(match)
                else:
                    spec["direction"] = replacement
                break
        
        
        color_patterns = [
            r"#[0-9a-fA-F]{6}",  
            r"rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)",  
            r"\b(red|blue|green|yellow|purple|orange|pink|black|white|gray|grey)\b" 
        ]
        
        colors_found = []
        for pattern in color_patterns:
            matches = re.findall(pattern, instruction, re.IGNORECASE)
            colors_found.extend(matches)
        

        if colors_found:
            for i, color in enumerate(colors_found[:5]): 
                position = (i / max(1, len(colors_found) - 1)) * 100 if len(colors_found) > 1 else 0
                spec["colors"].append({
                    "color": color.lower(),
                    "position": f"{position}%"
                })
        else:
            spec["colors"] = [
                {"color": "#ff0000", "position": "0%"},
                {"color": "#0000ff", "position": "100%"}
            ]
        
 
        element_patterns = [
            r"\b(rect|rectangle|square)\b",
            r"\b(circle|oval|ellipse)\b",
            r"\b(path|shape)\b",
            r"\b(text|label)\b"
        ]
        
        elements_found = []
        for pattern in element_patterns:
            if re.search(pattern, instruction_lower):
                if "rect" in pattern:
                    elements_found.append("rect")
                elif "circle" in pattern:
                    elements_found.append("circle")
                elif "path" in pattern:
                    elements_found.append("path")
                elif "text" in pattern:
                    elements_found.append("text")
        
        if elements_found:
            spec["target_elements"] = list(set(elements_found))
        
        return json.dumps(spec, indent=2)


class SVGManipulationToolInput(BaseModel):
    svg_content: str = Field(description="SVG content to modify")
    gradient_spec: str = Field(description="JSON gradient specification")

class SVGManipulationTool(BaseTool):
    name: str = "svg_manipulation_tool"
    description: str = "Manipulates SVG files to add or modify gradient definitions"
    args_schema: Type[BaseModel] = SVGManipulationToolInput
    
    def _run(self, svg_content: str, gradient_spec: str) -> str:
        """Apply gradient specifications to SVG content"""
        
        try:
            spec = json.loads(gradient_spec) if isinstance(gradient_spec, str) else gradient_spec
        except:
            return "Error: Invalid gradient specification format"
        
    
        if not svg_content.strip():
            svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
    <defs></defs>
    <rect width="300" height="200" x="50" y="50" fill="url(#gradient1)"/>
</svg>'''
        
        try:
            soup = BeautifulSoup(svg_content, 'xml')
            svg = soup.find('svg')
            
            if not svg:
                return "Error: Invalid SVG content"
            
        
            defs = svg.find('defs')
            if not defs:
                defs = soup.new_tag('defs')
                svg.insert(0, defs)
            
         
            gradient_id = "gradient1"
            
            
            if spec["gradient_type"] == "radial":
                gradient = soup.new_tag('radialGradient', id=gradient_id)
                gradient['cx'] = "50%"
                gradient['cy'] = "50%"
                gradient['r'] = "50%"
            else:
                gradient = soup.new_tag('linearGradient', id=gradient_id)
                
                
                direction = spec.get("direction", "to right")
                if "deg" in direction:
                    angle = int(re.search(r'(\d+)', direction).group(1))
                    gradient['gradientTransform'] = f"rotate({angle} 0.5 0.5)"
                elif direction == "to right":
                    gradient['x1'] = "0%"
                    gradient['y1'] = "0%"
                    gradient['x2'] = "100%"
                    gradient['y2'] = "0%"
                elif direction == "to left":
                    gradient['x1'] = "100%"
                    gradient['y1'] = "0%"
                    gradient['x2'] = "0%"
                    gradient['y2'] = "0%"
                elif direction == "to bottom":
                    gradient['x1'] = "0%"
                    gradient['y1'] = "0%"
                    gradient['x2'] = "0%"
                    gradient['y2'] = "100%"
                elif direction == "to top":
                    gradient['x1'] = "0%"
                    gradient['y1'] = "100%"
                    gradient['x2'] = "0%"
                    gradient['y2'] = "0%"
            
           
            for color_stop in spec.get("colors", []):
                stop = soup.new_tag('stop')
                stop['offset'] = color_stop.get("position", "0%")
                stop['stop-color'] = color_stop.get("color", "#000000")
                gradient.append(stop)
            
            
            existing = defs.find(attrs={'id': gradient_id})
            if existing:
                existing.decompose()
            
           
            defs.append(gradient)
            
        
            target_elements = spec.get("target_elements", ["rect"])
            for element_type in target_elements:
                elements = svg.find_all(element_type)
                for element in elements:
                    element['fill'] = f"url(#{gradient_id})"
            
            return str(soup)
            
        except Exception as e:
            return f"Error processing SVG: {str(e)}"


class GradientGeneratorToolInput(BaseModel):
    gradient_spec: str = Field(description="JSON gradient specification")

class GradientGeneratorTool(BaseTool):
    name: str = "gradient_generator_tool"
    description: str = "Generates optimized gradient definitions for SVG"
    args_schema: Type[BaseModel] = GradientGeneratorToolInput
    
    def _run(self, gradient_spec: str) -> str:
        """Generate optimized gradient SVG markup"""
        
        try:
            spec = json.loads(gradient_spec) if isinstance(gradient_spec, str) else gradient_spec
        except:
            return "Error: Invalid gradient specification"
        
        gradient_type = spec.get("gradient_type", "linear")
        colors = spec.get("colors", [])
        direction = spec.get("direction", "to right")
        
        if gradient_type == "radial":
            gradient_def = f'''<radialGradient id="gradient1" cx="50%" cy="50%" r="50%">'''
        else:
            if "deg" in direction:
                angle = re.search(r'(\d+)', direction).group(1)
                gradient_def = f'''<linearGradient id="gradient1" gradientTransform="rotate({angle} 0.5 0.5)">'''
            else:
                coords = {
                    "to right": 'x1="0%" y1="0%" x2="100%" y2="0%"',
                    "to left": 'x1="100%" y1="0%" x2="0%" y2="0%"',
                    "to bottom": 'x1="0%" y1="0%" x2="0%" y2="100%"',
                    "to top": 'x1="0%" y1="100%" x2="0%" y2="0%"'
                }
                coord_attr = coords.get(direction, coords["to right"])
                gradient_def = f'''<linearGradient id="gradient1" {coord_attr}>'''
        
       
        for color_stop in colors:
            color = color_stop.get("color", "#000000")
            position = color_stop.get("position", "0%")
            gradient_def += f'\n    <stop offset="{position}" stop-color="{color}"/>'
        
        gradient_def += f'\n</{gradient_type}Gradient>'
        
        return gradient_def


class SVGValidatorToolInput(BaseModel):
    svg_content: str = Field(description="SVG content to validate")

class SVGValidatorTool(BaseTool):
    name: str = "svg_validator_tool"
    description: str = "Validates SVG syntax and structure"
    args_schema: Type[BaseModel] = SVGValidatorToolInput
    
    def _run(self, svg_content: str) -> str:
        """Validate SVG content for correctness"""
        
        validation_result = {
            "syntax_valid": False,
            "errors": [],
            "warnings": [],
            "recommendations": []
        }
        
        try:
            parser = etree.XMLParser(ns_clean=True, recover=False)
            etree.fromstring(svg_content.encode('utf-8'), parser)
            validation_result["syntax_valid"] = True
            
        except etree.XMLSyntaxError as e:
            validation_result["errors"].append(f"XML Syntax Error: {str(e)}")
        except Exception as e:
            validation_result["errors"].append(f"Parsing Error: {str(e)}")
        
       
        try:
            soup = BeautifulSoup(svg_content, 'xml')
            svg = soup.find('svg')
            
            if not svg:
                validation_result["errors"].append("No SVG root element found")
            else:
                if not svg.get('width') and not svg.get('viewBox'):
                    validation_result["warnings"].append("SVG should have width or viewBox attribute")
                
                
                defs = svg.find('defs')
                if defs:
                    gradients = defs.find_all(['linearGradient', 'radialGradient'])
                    for gradient in gradients:
                        if not gradient.get('id'):
                            validation_result["errors"].append("Gradient missing required 'id' attribute")
                        
                        stops = gradient.find_all('stop')
                        if len(stops) < 2:
                            validation_result["warnings"].append("Gradient should have at least 2 color stops")
              
                elements_with_fill = svg.find_all(attrs={'fill': re.compile(r'url\(#.*\)')})
                if not elements_with_fill and defs and defs.find_all(['linearGradient', 'radialGradient']):
                    validation_result["warnings"].append("Gradients defined but not used")
        
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {str(e)}")
        
        return json.dumps(validation_result, indent=2)


class AccessibilityCheckerTool(BaseTool):
    name: str = "accessibility_checker_tool"
    description: str = "Checks SVG accessibility and color contrast"
    
    def _run(self, svg_content: str) -> str:
        """Check SVG for accessibility compliance"""
        
        accessibility_report = {
            "accessibility_score": 5,
            "issues": [],
            "recommendations": [],
            "color_contrast_issues": []
        }
        
        try:
            soup = BeautifulSoup(svg_content, 'xml')
            svg = soup.find('svg')
            
            if not svg:
                accessibility_report["issues"].append("No SVG element found")
                accessibility_report["accessibility_score"] = 1
                return json.dumps(accessibility_report, indent=2)
            
      
            title = svg.find('title')
            desc = svg.find('desc')
            
            if not title:
                accessibility_report["issues"].append("Missing <title> element for screen readers")
                accessibility_report["accessibility_score"] -= 2
                accessibility_report["recommendations"].append("Add <title> element describing the SVG content")
            
            if not desc:
                accessibility_report["recommendations"].append("Consider adding <desc> element for detailed description")
            
        
            if not svg.get('role'):
                accessibility_report["recommendations"].append("Consider adding role='img' attribute")
            
            
            gradients = soup.find_all(['linearGradient', 'radialGradient'])
            for gradient in gradients:
                stops = gradient.find_all('stop')
                colors = [stop.get('stop-color', '#000000') for stop in stops]
                

                if len(set(colors)) < 2:
                    accessibility_report["color_contrast_issues"].append(
                        f"Gradient {gradient.get('id', 'unnamed')} may have insufficient color variation"
                    )
            
          
            if len(accessibility_report["issues"]) == 0:
                accessibility_report["accessibility_score"] = min(10, accessibility_report["accessibility_score"] + 3)
            
        except Exception as e:
            accessibility_report["issues"].append(f"Error during accessibility check: {str(e)}")
            accessibility_report["accessibility_score"] = 1
        
        return json.dumps(accessibility_report, indent=2)