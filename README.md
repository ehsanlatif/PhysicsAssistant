
# PhysicsAssistant: An LLM-Powered Interactive Learning Robot for Physics Lab Investigations

Welcome to the PhysicsAssistant repository! This project contains a Python script for building a multimodal interactive robot designed to assist students in physics lab investigations.

## Project Overview

### Abstract

This study proposes a multimodal interactive robot (PhysicsAssistant) built on YOLOv8 object detection, cameras, speech recognition, and chatbot using LLM to provide assistance to students’ physics labs. The system aims to provide timely and accurate responses to student queries, thereby offloading teachers' labor and assisting with repetitive tasks. The performance of PhysicsAssistant has been evaluated through user studies and compared with human experts and other advanced LLMs like GPT-4.

### Key Contributions

- **Multimodal Integration:** Combines YOLOv8 for visual data, GPT-3.5-turbo for language processing, and speech processing for audio input.
- **Timely Responses:** Demonstrates significantly faster response times compared to advanced LLMs like GPT-4, making it suitable for real-time applications.
- **Educational Impact:** Validated by human experts based on Bloom’s taxonomy, showing potential as a real-time lab assistant.

## Prerequisites

Ensure you have the following installed:
- Python 3.7 or higher
- PyTorch
- Transformers (HuggingFace library)
- OpenAI API key (for accessing GPT-3.5-turbo)

## Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/PhysicsAssistant.git
   cd PhysicsAssistant
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Script

1. **Set Up Environment Variables:**
   Ensure your OpenAI API key is set as an environment variable:
   ```bash
   export OPENAI_API_KEY='your_openai_api_key'
   ```

2. **Run the Script:**
   ```bash
   python physicsassistant.py
   ```

### Script Description

1. **physicsassistant.py:** This script integrates speech-to-text, image processing with YOLOv8, prompt designing for LLM, and text-to-speech modules to create an interactive learning assistant for physics lab investigations. The script captures audio and visual input, processes these inputs, generates responses using GPT-3.5-turbo, validates these responses, and provides auditory feedback.

## Citation

If you use this model or code in your research, please cite our paper:
```
@article{latif2024physicsassistant,
  title={PhysicsAssistant: An LLM-Powered Interactive Learning Robot for Physics Lab Investigations},
  author={Latif, Ehsan and Parasuraman, Ramviyas and Zhai, Xiaoming},
  journal={IEEE RO-MAN Special Session},
  year={2024}
}
```

Thank you for using PhysicsAssistant! If you have any questions or feedback, please feel free to open an issue in this repository.
