# STEP Viewer Pro
AI-Contest Tool

- Prompt: Create a viewer for 3D model rendering with screenshot capture and export. Keep in mind that Windows doesn’t always play nice with all Python libraries! Achieve this with as little code as possible.
- Time Spent: ~3 Hours
- Human Interventions: Code needed repairs 12 times.
- Winner: ClaudeAI 🏆
- Silver: ChatGPT 🥈
- Bronze: DeepSeek 🥉

---

**STEP Viewer Pro** is a lightweight 3D model viewer designed to display STEP files (ISO 10303), with a focus on providing high-quality rendering of models for screenshots. This project was developed with the goal of enabling easy viewing and capturing of STEP files in customizable angles and resolutions, and it’s offered as a gift to the open-source community.

The tool was created through a collaboration between several AI models, where the development process was a competitive learning experience among the leading AI systems. In the end, **Claude** came out on top, helping to make the project a reality with its expertise. Special thanks also go to **Deepseek** and **ChatGPT**, who both contributed valuable assistance during the development process.

---

## Features

- **STEP File Loading**: Import and view STEP files (.stp, .step).
- **3D Model Rendering**: Visualize your 3D models with high-quality rendering.
- **Screenshot Capture**: Save screenshots of the rendered model in various angles and resolutions.
- **Easy-to-use Interface**: Intuitive GUI with buttons to load files and save images.

---

## Installation

To use **STEP Viewer Pro**, you need to install the following dependencies:

### Requirements

- **Python 3.x**  
- **PyQt6** (for the GUI)
- **CadQuery** (for STEP file handling and tessellation)
- **VTK** (for rendering and visualization)

### Installation Steps

1. Clone or download the repository.
2. Install the required dependencies by running:

```bash
pip install cadquery vtk PyQt6
```

---

## Usage

1. **Run the Viewer**: After installing the dependencies, simply run the `step_viewer.py` script.
2. **Open STEP File**: Click on "STEP Datei öffnen" to select and load your STEP file.
3. **Take Screenshot**: Click on "Screenshot speichern" to save a screenshot of the rendered model.

---

## How It Works

- **STEP File Loading**: The viewer uses **CadQuery** to import and process the STEP file into a 3D model, which is then tessellated to create a mesh for rendering.
- **Rendering**: The model is displayed using **VTK** for efficient 3D visualization. You can interact with the model, change angles, and capture screenshots.
- **Screenshot Capture**: The viewer allows you to take screenshots of your model at the desired angle and save them as PNG files.

---

## Contributing

This project is an open-source initiative, and contributions are welcome! Whether you want to improve the UI, optimize performance, or add new features, feel free to open issues or submit pull requests.

Remember, this tool was developed with a spirit of fair collaboration and open competition between powerful AI models, making it a true team effort, with contributions from **Claude**, **Deepseek**, and **ChatGPT**.

---

## License

This project is licensed under the **MIT License**.

---

## Acknowledgements

- **Claude.ai**: For winning the AI contest and helping to make this tool a reality.
- **Deepseek**: For the contributions and insights during the development process.
- **ChatGPT**: For contributing to the project and assisting in resolving technical challenges.
- **PyQt6, CadQuery, and VTK**: For the excellent libraries that powered the viewer.

Enjoy using **STEP Viewer Pro**—a gift to the open-source community from us!
