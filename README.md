# 🎨 AI-Driven SVG Gradient Editor

> Transform natural language into beautiful SVG gradients using intelligent AI agents

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![CrewAI](https://img.shields.io/badge/CrewAI-Latest-green.svg)](https://crewai.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Demo-red.svg)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal.svg)](https://fastapi.tiangolo.com)

## 🎥 Demo Video

[![Demo Video](https://github.com/user-attachments/assets/14377b4d-b9b7-4182-bfd6-87deb228a6c5)]


## 🏗️ How It Works

### Multi-Agent Pipeline
```
Natural Language → JSON Spec → SVG Generation → Quality Validation → File Output
     Agent 1         Agent 2       Agent 3         Saved to outputs/
```

### The Three Specialists

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| **🧠 Parser** | Language Understanding | `"sunset gradient orange to purple"` | `{"gradient_type": "linear", "colors": [...]}` |
| **⚙️ Generator** | SVG Creation | JSON specification | Complete SVG markup with gradients |
| **✅ Validator** | Quality Assurance | Raw SVG | Validated, accessible SVG file |

## 🎯 Key Features

- **🗣️ Natural Language Input** - No technical knowledge required
- **📁 File Output** - Generates actual SVG files, not just code
- **🎨 Smart Parsing** - Understands colors, directions, and gradient types
- **♿ Accessibility** - Validates color contrast and compliance
- **🔧 Dual Interface** - Streamlit demo + FastAPI for integration
- **📊 Workflow Transparency** - See exactly what each agent does

## 🛠️ Technical Stack

- **🤖 AI Framework**: CrewAI for agent orchestration
- **🧠 Language Model**: OpenAI GPT (configurable)
- **🎨 SVG Processing**: BeautifulSoup + lxml for parsing/validation
- **🌐 Web Interface**: Streamlit for demos
- **⚡ API Backend**: FastAPI for integration
- **📦 Package Manager**: UV for dependency management

## 📂 Project Structure

```
GradientEditor-CrewAI/
├── 🎯 main.py                    # Streamlit demo interface
├── ⚡ fastapi_app.py             # API server
├── 📁 src/gradient_editor/
│   ├── 🤖 crew.py               # Agent orchestration
│   └── 🛠️ tools/gradient_tools.py # Custom AI tools
├── 📊 outputs/                   # Generated SVG files
├── 🧠 knowledge/                 # Gradient examples database
└── 📋 requirements.txt           # Dependencies
```

## 🎨 Supported Gradient Types

### Linear Gradients
- Horizontal: `"red to blue going right"`
- Vertical: `"top to bottom dark to light"`
- Diagonal: `"45 degree gradient from yellow to green"`
- Custom angles: `"135 degree sunset gradient"`

### Radial Gradients
- Center fade: `"white center fading to black edges"`
- Color burst: `"rainbow burst from center"`
- Spotlight: `"bright center with dark edges"`

### Advanced Features
- **Multi-color**: `"gradient with red, orange, yellow, green, blue"`
- **Hex colors**: `"gradient from #ff6b6b to #4ecdc4"`
- **Element targeting**: `"apply gradient to circles only"`

## 🔧 Configuration

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-gradients`
3. Make changes and test with `streamlit run main.py`
4. Submit pull request

## 📄 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- **CrewAI** for agent orchestration framework
- **OpenAI** for language model capabilities
- **Streamlit** for rapid UI development
- **FastAPI** for modern API framework

---
