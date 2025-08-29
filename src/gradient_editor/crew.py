from crewai import Agent, Crew, Process, Task
from .tools.gradient_tools import (
    GradientAnalysisTool, 
    SVGManipulationTool, 
    GradientGeneratorTool,
    SVGValidatorTool,
    AccessibilityCheckerTool,
    GradientSpecification,
    ValidationReport
)
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GradientEditorCrew:
    """Gradient Editor CrewAI crew"""
    
    def __init__(self) -> None:
        # Initialize tools
        self.gradient_analysis_tool = GradientAnalysisTool()
        self.svg_manipulation_tool = SVGManipulationTool()
        self.gradient_generator_tool = GradientGeneratorTool()
        self.svg_validator_tool = SVGValidatorTool()
        self.accessibility_checker_tool = AccessibilityCheckerTool()
        
        # Create agents
        self.gradient_parser_agent = Agent(
            role="Natural Language Understanding Specialist for Gradient Instructions",
            goal="Extract precise gradient specifications from natural language descriptions, including gradient type, direction, colors, and positioning details",
            backstory="You are an expert in interpreting human language about visual design elements. You specialize in understanding how people describe gradients, colors, and visual effects, translating their intent into structured technical specifications.",
            tools=[self.gradient_analysis_tool],
            verbose=True,
            allow_delegation=False
        )
        
        self.svg_manipulator_agent = Agent(
            role="SVG Gradient Implementation Expert",
            goal="Generate and apply gradient definitions to SVG elements based on parsed specifications, ensuring proper syntax and visual accuracy",
            backstory="You are a master of SVG markup and CSS gradients. You understand the intricacies of SVG gradient definitions, coordinate systems, and how to apply gradients to various SVG elements while maintaining clean, valid code.",
            tools=[self.svg_manipulation_tool, self.gradient_generator_tool],
            verbose=True,
            allow_delegation=False
        )
        
        self.validation_agent = Agent(
            role="SVG Quality Assurance Specialist",
            goal="Validate SVG output for correctness, accessibility, and visual quality, ensuring the generated gradients meet design standards",
            backstory="You are a meticulous quality assurance expert with deep knowledge of SVG standards, accessibility guidelines, and visual design principles. You ensure that all generated SVG content is valid, performant, and visually appealing.",
            tools=[self.svg_validator_tool, self.accessibility_checker_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def generate_gradient(self, instruction: str, svg_content: str = "") -> dict:
        """Main method to generate gradients from natural language instructions"""
        
        print(f"\n🎨 Starting gradient generation workflow...")
        print(f"📝 User instruction: '{instruction}'")
        print(f"📄 Input SVG content: {'Provided' if svg_content.strip() else 'Will create new SVG'}")
        
        try:
            # Task 1: Parse gradient instruction
            print(f"\n🤖 Agent 1: Gradient Parser - Analyzing natural language...")
            parse_task = Task(
                description=f"""
                ROLE: You are a Natural Language Understanding Specialist for Gradient Instructions.
                
                TASK: Analyze this user instruction and extract gradient specifications.
                
                USER INSTRUCTION: {instruction}
                
                IMPORTANT: When using the gradient_analysis_tool, pass the instruction parameter correctly:
                - Use: {{"instruction": "the user instruction text"}}
                - NOT: {{"description": "..."}}
                
                Extract and return a JSON specification containing:
                - gradient_type: "linear" or "radial"
                - direction: angle in degrees or keywords like "to right", "to bottom"
                - colors: array of color objects with hex/rgb values and positions
                - additional_properties: any special styling requirements
                - target_elements: which SVG elements should receive the gradient
                
                Call gradient_analysis_tool with instruction="{instruction}" to get the parsed specification.
                """,
                expected_output="JSON gradient specification with all required fields",
                agent=self.gradient_parser_agent
            )
            
            # Task 2: Generate SVG gradient
            print(f"🤖 Agent 2: SVG Manipulator - Creating SVG with gradients...")
            generate_task = Task(
                description=f"""
                ROLE: You are an SVG Gradient Implementation Expert.
                
                TASK: Create a complete SVG file with gradient definitions based on the parsed specification from the previous task.
                
                INPUT SVG: {svg_content if svg_content.strip() else 'Create new SVG with basic shapes'}
                
                IMPORTANT: When using svg_manipulation_tool, pass parameters correctly:
                - svg_content: the SVG content to modify (or empty string for new SVG)
                - gradient_spec: the JSON specification from the previous task
                
                REQUIREMENTS:
                1. Use svg_manipulation_tool with the gradient specification from previous task
                2. Ensure proper <defs> section with gradient definitions
                3. Apply gradients to target elements using fill="url(#gradientId)"
                4. Return ONLY the complete SVG markup, nothing else
                5. SVG must be valid and renderable
                
                OUTPUT: Complete SVG markup ready for file output
                """,
                expected_output="Complete valid SVG markup with gradient definitions and applied fills",
                agent=self.svg_manipulator_agent
            )
            
            # Task 3: Validate and finalize SVG
            print(f"🤖 Agent 3: Validator - Checking SVG quality...")
            validate_task = Task(
                description=f"""
                ROLE: You are an SVG Quality Assurance Specialist.
                
                TASK: Validate the generated SVG from the previous task and return the final SVG.
                
                IMPORTANT: When using validation tools, pass the svg_content parameter correctly:
                - svg_validator_tool expects: {{"svg_content": "the SVG markup to validate"}}
                - accessibility_checker_tool expects: {{"svg_content": "the SVG markup to check"}}
                
                PROCESS:
                1. Use svg_validator_tool with the SVG from previous task
                2. Use accessibility_checker_tool for compliance checking
                3. If critical issues found, provide corrected SVG
                4. Return the final, validated SVG markup (not JSON reports)
                
                OUTPUT: Final validated SVG markup ready for output
                """,
                expected_output="Final validated SVG markup ready for output",
                agent=self.validation_agent
            )
            
            # Create crew
            crew = Crew(
                agents=[self.gradient_parser_agent, self.svg_manipulator_agent, self.validation_agent],
                tasks=[parse_task, generate_task, validate_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute the crew
            print(f"\n🚀 Executing CrewAI workflow...")
            result = crew.kickoff()
            
            # Extract the final SVG from the result
            final_svg = str(result)
            
            # Save SVG to outputs folder
            import os
            from datetime import datetime
            
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            svg_filename = f"gradient_{timestamp}.svg"
            svg_filepath = os.path.join(output_dir, svg_filename)
            
            with open(svg_filepath, 'w', encoding='utf-8') as f:
                f.write(final_svg)
            
            print(f"\n✅ Workflow completed successfully!")
            print(f"📁 SVG saved to: {svg_filepath}")
            print(f"🎯 Final output: Valid SVG with applied gradients")
            
            return {
                'success': True,
                'svg_output': final_svg,
                'svg_file': svg_filepath,
                'workflow_log': {
                    'instruction': instruction,
                    'input_svg_provided': bool(svg_content.strip()),
                    'output_file': svg_filepath,
                    'agents_executed': ['gradient_parser_agent', 'svg_manipulator_agent', 'validation_agent']
                }
            }
            
        except Exception as e:
            error_svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="100%" height="100%" fill="#f8f8f8"/>
    <text x="20" y="100" font-family="Arial" font-size="14" fill="#d32f2f">
        Error: {str(e)}
    </text>
</svg>'''
            
            print(f"\n❌ Error in workflow: {str(e)}")
            
            return {
                'success': False,
                'error': str(e),
                'svg_output': error_svg,
                'svg_file': None
            }
