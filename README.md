# STEP Viewer Pro

STEP Viewer Pro is a Python-based desktop application designed for visualizing STEP (STP) files, commonly used in 3D CAD modeling. This viewer utilizes the power of VTK (Visualization Toolkit) for rendering and CadQuery for importing STEP files. The application provides an interactive interface with basic functionality for loading STEP files, visualizing them in 3D, and saving screenshots of the rendered view.

## Features

- **Load and View STEP Files**: Open STEP files (.stp, .step) and display them in a 3D interactive viewer.
- **3D Visualization**: Leverage VTK for rendering the 3D geometry with dynamic interactions.
- **Screenshot Capture**: Save a screenshot of the rendered view to your local machine.
- **Cross-Platform**: Works on systems supporting Python and Qt.

## Requirements

To run this project, the following Python modules must be installed:

- `cadquery`: Used for importing and working with STEP files.
- `PyQt6`: Provides the GUI components for the application.
- `vtk`: The core library for 3D rendering.
- `os`: Used for environment configuration.
- `sys`: For system-specific parameters and functions.

### Installation

1. Ensure that you have Python 3.7 or higher installed. You can download it from [here](https://www.python.org/downloads/).
   
2. Install the necessary dependencies by running the following command:

```bash
pip install cadquery PyQt6 vtk
```

If you encounter issues installing `vtk`, please check the official [VTK installation guide](https://vtk.org/download/).

## Usage

1. **Run the Application**: Open a terminal or command prompt, navigate to the directory where the script is located, and run:

```bash
python stp.py
```

2. **Load STEP File**: After launching the application, click the "STEP Datei öffnen" button to open a file dialog. Select a STEP file (.stp or .step) from your system to load it into the viewer.

3. **View the 3D Model**: The 3D model will be displayed in the VTK viewer window. You can rotate, zoom, and pan the view using mouse controls.

4. **Save Screenshot**: To save a screenshot of the rendered view, click the "Screenshot speichern" button, select the file location, and save the image as a PNG file.

## Code Overview

### Main Components:

1. **CadQuery Import**: 
    - Used for importing the STEP file using `cq.importers.importStep()`.
    - The STEP file is processed to extract the 3D solids for rendering.

2. **VTK Rendering**: 
    - The 3D objects are tessellated into vertices and triangles using `cadquery`.
    - These are then passed to VTK for rendering through the `vtkPoints` and `vtkCellArray` objects.

3. **User Interface**:
    - Built using `PyQt6`, which provides buttons for loading files and saving screenshots.
    - The VTK rendering window is integrated into the Qt GUI via `QVTKRenderWindowInteractor`.

4. **Screenshot Functionality**:
    - A screenshot of the rendered 3D view can be captured and saved using `vtkWindowToImageFilter` and `vtkPNGWriter`.

## Troubleshooting

### Common Issues

1. **File Not Opening**:
    - Ensure that the file path to the STEP file is correct and that the file is not corrupted.
    - The application supports both `.stp` and `.step` file formats.

2. **Performance with Large Files**:
    - Large STEP files may take longer to load due to the tessellation process. Be patient while the file is being processed and rendered.

3. **Dependencies**:
    - Ensure all required dependencies are installed by running the installation command. If you face any issues with `vtk` installation, refer to the [VTK installation guide](https://vtk.org/download/).

## License

This project is open-source and licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- **CadQuery**: A powerful parametric 3D CAD scripting API used for importing and working with STEP files.
- **VTK**: A powerful 3D rendering library used for visualizing 3D models.
- **PyQt6**: The Qt bindings for Python that help build the GUI interface.

## Contact

For any questions, suggestions, or issues, feel free to reach out or open an issue on GitHub.



