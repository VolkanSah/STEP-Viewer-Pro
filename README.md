
# STEP Viewer Pro (ISO 10303)

#### AI-Contest Tool (Created as a test because there's no real testing on social networks – only scam content!)

- **Basic-Prompt**: Create a .stp, .step file viewer for 3D model rendering with screenshot capture and export. Keep in mind that Windows doesn’t always play nice with all Python libraries! Achieve this with minimal code. Note: I need to capture the model from different angles!
- **Time Spent**: ~3 Hours
- **Human Interventions**: Code needed fixes 12 times.
- **Winner**: **ClaudeAI** 🏆 - Fixed errors but embraced the code! (Understands Error-Logs better)
- **Silver**: **ChatGPT** 🥈 - 80% of the code! But overcomplicated things!
- **Bronze**: **DeepSeek** 🥉 - Gave overly complex ideas, which broke the code!

---

**STEP Viewer Pro** is a lightweight 3D model viewer designed to display STEP files (ISO 10303), focused on high-quality rendering of models for easy screenshot capture and export. It allows users to view STEP files from customizable angles and resolutions, making it perfect for anyone who needs to capture models for presentations, reviews, or documentation.

This project was created through a competitive collaboration between several leading AI systems, testing their capabilities and learning from real-world development scenarios. **ClaudeAI** emerged as the winner, offering valuable fixes and optimizing the code to bring the project to life. Special thanks also go to **DeepSeek** and **ChatGPT**, who contributed meaningful insights during the process, though their approaches were sometimes more complex than needed.


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

### Basic Idea for Ais 

```
from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepTools import breptools_Write

# Datei einlesen
step_reader = STEPControl_Reader()
status = step_reader.ReadFile("deine_datei.stp")

if status == 1:  # 1 bedeutet Erfolg
    step_reader.TransferRoot()
    shape = step_reader.OneShape()

    # 3D-Viewer starten
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(shape, update=True)
    
    # Screenshot speichern
    display.View.Dump("preview.png")
    
    start_display()
else:
    print("Fehler: Datei konnte nicht geladen werden.")
```

### Screenshot
![STEP-VIEWER-PRO](step.jpg)


