import streamlit as st
import os
from dotenv import load_dotenv
from src.gradient_editor import GradientEditorCrew
import json

load_dotenv()

def main():
    st.set_page_config(
        page_title="AI Gradient Editor",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎨 AI-Driven SVG Gradient Editor")
    st.markdown("Transform natural language descriptions into beautiful SVG gradients using CrewAI agents")
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        
        st.divider()
        

        model = st.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            index=0
        )
        os.environ["OPENAI_MODEL_NAME"] = model
        
        st.divider()
        

        st.header("💡 Example Instructions")
        examples = [
            "Create a linear gradient from red to blue going to the right",
            "Make a radial gradient with purple in the center fading to white",
            "Generate a diagonal gradient from #ff6b6b to #4ecdc4",
            "Create a sunset gradient with orange, pink, and purple colors",
            "Make a vertical gradient from dark blue at top to light blue at bottom"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{hash(example)}"):
                st.session_state.instruction = example
    

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Input")
        

        instruction = st.text_area(
            "Describe your gradient:",
            value=st.session_state.get('instruction', ''),
            height=100,
            placeholder="e.g., Create a linear gradient from red to blue going to the right"
        )
        

        st.subheader("📄 Existing SVG (Optional)")
        svg_input = st.text_area(
            "Paste existing SVG content:",
            height=200,
            placeholder="<svg>...</svg> (leave empty to create new SVG)"
        )
        

        generate_btn = st.button("🚀 Generate Gradient", type="primary", use_container_width=True)
    
    with col2:
        st.header("🎯 Output")
        
        if generate_btn and instruction:
            if not api_key:
                st.error("Please provide an OpenAI API key in the sidebar")
                return
            
            with st.spinner("🤖 AI agents are working on your gradient..."):
                try:
                    crew = GradientEditorCrew()
                    

                    result = crew.generate_gradient(instruction, svg_input)
                    
                    if result['success']:
                        st.success("✅ Gradient generated successfully!")
                        

                        workflow_log = result.get('workflow_log', {})
                        svg_file = result.get('svg_file')
                        
                        if svg_file:
                            st.info(f"📁 SVG saved to: `{svg_file}`")
                        

                        svg_output = result['svg_output']
                        st.subheader("🖼️ Generated SVG")
                        

                        st.components.v1.html(
                            f'<div style="text-align: center; padding: 20px; background: #f0f0f0; border-radius: 10px;">{svg_output}</div>',
                            height=400
                        )
                        

                        st.download_button(
                            label="📥 Download SVG",
                            data=svg_output,
                            file_name="gradient.svg",
                            mime="image/svg+xml"
                        )
                        

                        with st.expander("🔄 Workflow Details"):
                            st.write("**Agent Execution Flow:**")
                            agents = workflow_log.get('agents_executed', [])
                            for i, agent in enumerate(agents, 1):
                                st.write(f"{i}. **{agent.replace('_', ' ').title()}**")
                            
                            st.write("\n**Workflow Summary:**")
                            st.json(workflow_log)
                        
                     
                        with st.expander("📋 View SVG Code"):
                            st.code(svg_output, language="xml")
                        

                        if svg_input.strip():
                            with st.expander("🔄 Before/After Comparison"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write("**Before (Input SVG):**")
                                    st.code(svg_input[:500] + "..." if len(svg_input) > 500 else svg_input, language="xml")
                                with col2:
                                    st.write("**After (Generated SVG):**")
                                    st.code(svg_output[:500] + "..." if len(svg_output) > 500 else svg_output, language="xml")
                    
                    else:
                        st.error("❌ Failed to generate gradient")
                        if 'error' in result:
                            st.error(f"Error details: {result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)
        
        elif generate_btn and not instruction:
            st.warning("⚠️ Please provide a gradient description")
    

    st.divider()
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Built with CrewAI • Powered by OpenAI • Made with ❤️</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
