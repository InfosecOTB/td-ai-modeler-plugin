# AI-Powered Threat Modeling Tool

![td-ai](assets/td-ai-part2.png)

An intelligent threat modeling application that uses Large Language Models (LLMs) to automatically generate security threats and their mitigation proposals for Threat Dragon models.

## Features

- **AI-Powered Threat Generation**: Uses state-of-the-art LLMs to analyze system components and generate comprehensive security threats
- **Threat Framework Support**: Supports STRIDE threat modeling framework, however the code can be adjusted for others as well
- **Multi-LLM Support**: Tested on OpenAI, Anthropic, Google, Novita, and xAI. As the code uses LiteLLM library, it should work with other models as well.
- **Threat Dragon Integration**: Works seamlessly with Threat Dragon JSON models
- **Smart Filtering**: Automatically skips out-of-scope components
- **Data Validation**: Built-in Pydantic validation for threat data integrity
- **Response Validation**: Comprehensive validation of AI responses against original models
- **Validation Logging**: Timestamped validation logs with detailed coverage reports (DEBUG mode only)
- **Visual Indicators**: Automatically adds visual cues (red strokes) to components with threats
- **Command-Line Interface**: Flexible command-line arguments for configuration

## Quick Start

### Prerequisites

- Python 3.8+
- API key for your chosen LLM provider

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd td-ai-modeler-plugin
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your API key:
   ```env
   API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python src/main.py --llm-model openai/gpt-5 --model-file path/to/your-model.json
   ```

5. **Check results**
   - The input model file is updated directly with AI-generated threats
   - Validation logs are generated in `./logs/` directory (DEBUG mode only)

## Usage

### Basic Usage

```bash
python src/main.py --llm-model openai/gpt-5 --model-file path/to/your-model.json
```

### Available Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--llm-model` | Yes | - | LLM model identifier (e.g., "openai/gpt-5", "anthropic/claude-sonnet-4-5-20250929") |
| `--model-file` | Yes | - | Input threat model JSON file path (full path including filename) |
| `--temperature` | No | 0.1 | LLM temperature for randomness (range: 0-2) |
| `--response-format` | No | False | Enable structured JSON response format |
| `--api-base` | No | None | Custom API base URL |
| `--log-level` | No | INFO | Logging level (INFO or DEBUG) |

### Examples

**Basic usage with OpenAI GPT-5:**
```bash
python src/main.py --llm-model openai/gpt-5 --model-file input/my-model.json
```

**Enable structured JSON format for better response quality:**
```bash
python src/main.py --llm-model openai/gpt-5 --model-file input/my-model.json --response-format
```

**Use custom temperature for more creative responses:**
```bash
python src/main.py --llm-model anthropic/claude-sonnet-4-5-20250929 --model-file input/my-model.json --temperature 0.3
```

**Enable DEBUG logging for detailed logs:**
```bash
python src/main.py --llm-model openai/gpt-5 --model-file input/my-model.json --log-level DEBUG
```

**Use custom API endpoint:**
```bash
python src/main.py --llm-model openai/gpt-5 --model-file input/my-model.json --api-base https://your-custom-endpoint.com
```

## Configuration

### Tested LLM Providers

| Provider | Model | API Key Variable | Recommended Configuration |
|----------|-------|------------------|---------------------------|
| **Anthropic** | `anthropic/claude-sonnet-4-5-20250929` | `API_KEY` | `--temperature 0.1` |
| **Anthropic** | `anthropic/claude-opus-4-1-20250805` | `API_KEY` | `--temperature 0.1` |
| **Novita** | `novita/deepseek/deepseek-r1` | `API_KEY` | `--temperature 0.1` |
| **Novita** | `novita/qwen/qwen3-coder-480b-a35b-instruct` | `API_KEY` | `--temperature 0.1` |
| **Novita** | `novita/deepseek/deepseek-v3.1-terminus` | `API_KEY` | `--temperature 0.1` |
| **Local Ollama** | `ollama/gemma3:27b` | None | `--response-format` |
| **xAI** | `xai/grok-4-fast-reasoning-latest` | `API_KEY` | `--temperature 0.1 --response-format` |
| **xAI** | `xai/grok-4-latest` | `API_KEY` | `--temperature 0.1 --response-format` |
| **OpenAI** | `openai/gpt-5` | `API_KEY` | `--temperature 0.1 --response-format` |
| **OpenAI** | `openai/gpt-5-mini` | `API_KEY` | `--temperature 0.1 --response-format` |
| **Google** | `gemini/gemini-2.5-pro` | `API_KEY` | `--temperature 0.1` |

### Configuration Parameters

- **`--temperature`**: Controls the randomness and creativity of AI responses (0.0 = deterministic, 1.0 = very random). Lower values (0.1) provide more consistent, focused responses ideal for threat modeling.

- **`--response-format`**: Forces the AI to return structured JSON using Pydantic models. Recommended for OpenAI, xAI, and Ollama models.

- **`--api-base`**: Override default API endpoint for custom deployments or local models.

- **`--log-level`**: Set to `DEBUG` for detailed logging and validation reports.

### Environment Variables

Set your API key in the `.env` file:

```env
API_KEY=your_api_key_here
```

## Project Structure

```
td-ai-modeler-plugin/
├── src/
│   ├── main.py              # Main application entry point
│   ├── ai_client.py         # LLM integration and threat generation
│   ├── utils.py             # File operations and model updates
│   ├── models.py            # Pydantic data models
│   └── validator.py         # AI response validation
├── schema/                  # Schema directory
│   └── owasp.threat-dragon.schema.V2.json
├── logs/                    # Log files directory (DEBUG mode)
├── prompt.txt               # AI threat modeling prompt template
├── env.example              # Environment configuration template
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## How It Works

1. **Input Processing**: Loads Threat Dragon schema and model files
2. **AI Threat Generation**: Uses LLM to analyze components and generate threats
3. **Data Validation**: Ensures all generated threats have required fields
4. **Response Validation**: Validates AI response completeness and accuracy
5. **Model Update**: Updates the threat model file directly with generated threats
6. **Visual Updates**: Adds red stroke indicators to components with threats
7. **Validation Logging**: Generates detailed validation reports (DEBUG mode only)

## Validation Features

The tool includes comprehensive validation to ensure AI responses are complete and accurate:

### Validation Categories
- **INFO**: Elements in scope but missing threats (informational)
- **WARNINGS**: Out-of-scope elements or quality issues (non-blocking)
- **ERRORS**: Completely different IDs with no model overlap (blocking)

### Validation Checks
- **Coverage Validation**: Ensures all in-scope elements (outOfScope=false) have threats
- **ID Validation**: Verifies all response IDs correspond to valid model elements
- **Quality Validation**: Checks that threats include proper mitigation strategies (empty mitigations generate warnings)
- **Data Integrity**: Validates threat structure and required fields

### Validation Outputs
- **Console Summary**: Real-time validation results with coverage statistics
- **Detailed Logs**: Timestamped logs in `./logs/` directory (DEBUG mode only)
- **Error Reporting**: Specific details about missing elements and invalid IDs
- **Coverage Metrics**: Percentage of in-scope elements with generated threats

### Validation Notes
- Trust boundary boxes and curves are excluded from validation
- Missing elements are informational, not errors
- Invalid IDs (out of scope) are warnings, not errors
- Only completely different IDs are validation errors

Validation runs automatically during threat generation. Enable DEBUG logging for detailed logs.

## Troubleshooting

### Common Issues

#### LLM Response Errors
- **Invalid JSON**: The tool automatically attempts to extract JSON from malformed responses
- **Timeout Issues**: Request timeout is set to 4 hours for large models
- **Token Limits**: Token count is logged for monitoring

#### Validation Warnings
- **Missing Elements**: Normal for complex models - elements may be out of scope
- **Empty Mitigations**: Check AI response quality or adjust prompt template
- **Out-of-Scope Elements**: Elements not in scope but have threats generated
- **Invalid IDs**: Verify model structure and element IDs

#### Configuration Issues
- **API Key Errors**: Ensure `API_KEY` environment variable is set in `.env` file
- **Model Not Found**: Verify model name format matches provider requirements
- **Connection Issues**: Check `--api-base` URL for custom endpoints

### Performance Optimization

#### For Large Models
- Use lower temperature values (0.1) for more consistent responses
- Enable structured output with `--response-format` for better quality

#### For Local Models (Ollama)
- Ensure sufficient hardware (GPU, CPU, RAM)
- Monitor system resources during generation

## Development

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py --llm-model openai/gpt-5 --model-file input/your-model.json
```

### Code Structure

- **`main.py`**: Orchestrates the entire threat modeling process with argparse configuration
- **`ai_client.py`**: Handles LLM communication and threat generation
- **`utils.py`**: File operations and model manipulation utilities
- **`models.py`**: Pydantic models for threat data validation
- **`validator.py`**: Comprehensive validation of AI responses

### Customization

#### Modifying the AI Prompt
Edit `prompt.txt` to customize threat generation behavior:
- Add specific threat frameworks
- Modify threat categories
- Adjust output format requirements

#### Adding New LLM Providers
1. Add provider API key to `.env` file
2. Update provider table in README
3. Test with sample threat model

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/) for the excellent threat modeling framework
- [LiteLLM](https://github.com/BerriAI/litellm) for seamless multi-LLM support
- [Pydantic](https://pydantic.dev/) for robust data validation

## Additional Resources

For more information about cybersecurity and AI projects, visit my blog at [https://infosecotb.com](https://infosecotb.com).

---

**Built for security professionals and threat modeling practitioners**