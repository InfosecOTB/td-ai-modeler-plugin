# 🤖 AI-Powered Threat Modeling Tool

An intelligent threat modeling application that uses Large Language Models (LLMs) to automatically generate security threats for Threat Dragon models using the STRIDE framework.

## ✨ Features

- **🤖 AI-Powered Threat Generation**: Uses state-of-the-art LLMs to analyze system components and generate comprehensive security threats
- **🛡️ STRIDE Framework**: Implements the industry-standard STRIDE methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)
- **🔧 Multi-LLM Support**: Compatible with OpenAI, Anthropic, Google, xAI, Azure OpenAI, Cohere, Hugging Face, and Ollama
- **📊 Threat Dragon Integration**: Works seamlessly with Threat Dragon JSON models
- **🎯 Smart Filtering**: Automatically skips out-of-scope components
- **✅ Data Validation**: Built-in Pydantic validation ensures data integrity
- **🎨 Visual Indicators**: Automatically adds visual cues (red strokes) to components with threats

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API key for your chosen LLM provider

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd td-ai-modeler
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration:
   ```env
   # Choose your LLM provider (uncomment one)
   LLM_MODEL_NAME=openai/gpt-4o
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Input files
   INPUT_THREAT_SCHEMA_JSON=owasp.threat-dragon.schema.V2.json
   INPUT_THREAT_MODEL_JSON=your-model.json
   ```

4. **Prepare input files**
   - Place your Threat Dragon schema file in `./input/`
   - Place your threat model JSON file in `./input/`

5. **Run the application**
   ```bash
   python src/main.py
   ```

6. **Check results**
   - Updated model with AI-generated threats will be in `./output/`

## 🔧 Configuration

### Supported LLM Providers

| Provider | Model Example | API Key Variable |
|----------|---------------|------------------|
| **OpenAI** | `openai/gpt-4o` | `OPENAI_API_KEY` |
| **Anthropic** | `anthropic/claude-3-5-sonnet-20241022` | `ANTHROPIC_API_KEY` |
| **Google** | `gemini/gemini-1.5-pro` | `GOOGLE_API_KEY` |
| **xAI** | `xai/grok-3-mini-beta` | `XAI_API_KEY` |
| **Azure OpenAI** | `azure/gpt-4o` | `AZURE_API_KEY` |
| **Cohere** | `cohere/command-r-plus` | `COHERE_API_KEY` |
| **Hugging Face** | `huggingface/meta-llama/Llama-2-7b-chat-hf` | `HUGGINGFACE_API_KEY` |
| **Ollama** | `ollama/llama2` | `OLLAMA_API_BASE` |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `LLM_MODEL_NAME` | LLM model identifier | `openai/gpt-4o` |
| `INPUT_THREAT_SCHEMA_JSON` | Threat Dragon schema filename | `owasp.threat-dragon.schema.V2.json` |
| `INPUT_THREAT_MODEL_JSON` | Input threat model filename | `my-model.json` |

## 📁 Project Structure

```
ai-threat-modeling/
├── src/
│   ├── main.py              # Main application entry point
│   ├── ai_client.py         # LLM integration and threat generation
│   ├── utils.py             # File operations and model updates
│   └── models.py            # Pydantic data models
├── input/                   # Input files directory
│   ├── owasp.threat-dragon.schema.V2.json
│   └── your-model.json
├── output/                  # Generated output directory
├── prompt.txt               # STRIDE threat modeling prompt template
├── env.example              # Environment configuration template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔍 How It Works

1. **📥 Input Processing**: Loads Threat Dragon schema and model files
2. **🔍 Component Analysis**: Filters out-of-scope components automatically
3. **🤖 AI Threat Generation**: Uses LLM to analyze components and generate STRIDE threats
4. **✅ Data Validation**: Ensures all generated threats have required fields
5. **📝 Model Update**: Updates the threat model while preserving original formatting
6. **✅ Final Validation**: Validates the updated model structure

## 🛠️ Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### Code Structure

- **`main.py`**: Orchestrates the entire threat modeling process
- **`ai_client.py`**: Handles LLM communication and threat generation
- **`utils.py`**: File operations and model manipulation utilities
- **`models.py`**: Pydantic models for data validation


## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Threat Dragon](https://threatdragon.org/) for the excellent threat modeling framework
- [LiteLLM](https://github.com/BerriAI/litellm) for seamless multi-LLM support
- [Pydantic](https://pydantic.dev/) for robust data validation

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/ai-threat-modeling/issues) page
2. Create a new issue with detailed information
3. Include your configuration and error messages

---

**Built for security professionals and threat modeling practitioners**