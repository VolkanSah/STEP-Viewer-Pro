import sys
import os
from pathlib import Path
import cadquery as cq
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QFileDialog, QMessageBox, QProgressDialog, 
                              QComboBox, QLabel, QHBoxLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer
import vtk

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

# Sprachdaten
TRANSLATIONS = {
    "de": {
        "title": "STEP Viewer Pro",
        "btn_load": "STEP Datei öffnen",
        "btn_save": "Screenshot speichern",
        "language": "Sprache",
        "select_file": "STEP-Datei auswählen",
        "step_files": "STEP Files (*.stp *.step);;Alle Dateien (*)",
        "save_screenshot": "Screenshot speichern",
        "png_files": "PNG Bilder (*.png);;Alle Dateien (*)",
        "error": "Fehler",
        "loading": "Lade STEP-Datei...",
        "processing": "Verarbeite 3D-Daten...",
        "load_error": "Fehler beim Laden",
        "save_error": "Speicherfehler",
        "no_solids": "Die Datei enthält keine 3D-Körper",
        "unsupported": "Nicht unterstützter Dateityp"
    },
    "en": {
        "title": "STEP Viewer Pro",
        "btn_load": "Open STEP File",
        "btn_save": "Save Screenshot",
        "language": "Language",
        "select_file": "Select STEP File",
        "step_files": "STEP Files (*.stp *.step);;All Files (*)",
        "save_screenshot": "Save Screenshot",
        "png_files": "PNG Images (*.png);;All Files (*)",
        "error": "Error",
        "loading": "Loading STEP file...",
        "processing": "Processing 3D data...",
        "load_error": "Error loading file",
        "save_error": "Error saving file",
        "no_solids": "File contains no 3D bodies",
        "unsupported": "Unsupported file type"
    }
}

class LoaderThread(QThread):
    """Thread für asynchrones Laden von STEP-Dateien"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, path):
        super().__init__()
        self.path = path
        
    def run(self):
        try:
            self.progress.emit("loading")
            result = cq.importers.importStep(self.path)
            
            self.progress.emit("processing")
            # Solids extrahieren
            all_solids = []
            if isinstance(result, cq.Assembly):
                all_solids = [solid for child in result.children for solid in child.obj.Solids()]
            elif isinstance(result, cq.Workplane):
                all_solids = result.objects if result.objects else [result.val()]
            elif isinstance(result, (cq.Compound, cq.Shape)):
                all_solids = [result]
            else:
                self.error.emit(f"unsupported:{type(result)}")
                return
                
            if not all_solids:
                self.error.emit("no_solids")
                return
                
            # Mesh kombinieren
            vertices = []
            triangles = []
            vertex_offset = 0
            
            for solid in all_solids:
                mesh = solid.tessellate(0.1)
                vertices.extend(mesh[0])
                
                for triangle in mesh[1]:
                    triangles.append([idx + vertex_offset for idx in triangle])
                vertex_offset += len(mesh[0])
                
            self.finished.emit((vertices, triangles))
            
        except Exception as e:
            self.error.emit(str(e))

class STEPViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_actor = None
        self.loader_thread = None
        self.lang = "de"  # Default
        self.init_ui()
        
    def tr(self, key):
        """Übersetzungs-Helfer"""
        return TRANSLATIONS[self.lang].get(key, key)
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle(self.tr("title"))
        self.setGeometry(100, 100, 1024, 768)

        # VTK Widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.renderer = vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.renderer.SetBackground(0.15, 0.15, 0.15)

        # Steuerungselemente
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # Sprach-Selektor
        lang_layout = QHBoxLayout()
        lang_label = QLabel()
        self.lang_label = lang_label
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Deutsch", "English"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        self.btn_load = QPushButton()
        self.btn_load.clicked.connect(self.load_step)
        layout.addWidget(self.btn_load)
        
        self.btn_save = QPushButton()
        self.btn_save.clicked.connect(self.save_screenshot)
        layout.addWidget(self.btn_save)

        # Haupt-Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.vtk_widget)
        main_layout.addWidget(control_widget)
        
        self.setCentralWidget(central_widget)
        self.update_ui_texts()

        # VTK initialisieren
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
        
    def update_ui_texts(self):
        """Aktualisiert alle UI-Texte"""
        self.setWindowTitle(self.tr("title"))
        self.lang_label.setText(self.tr("language") + ":")
        self.btn_load.setText(self.tr("btn_load"))
        self.btn_save.setText(self.tr("btn_save"))
        
    def change_language(self, idx):
        """Wechselt die Sprache"""
        self.lang = "de" if idx == 0 else "en"
        self.update_ui_texts()

    def load_step(self):
        """Lädt und zeigt eine STEP-Datei an (asynchron)"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("select_file"),
            "",
            self.tr("step_files")
        )
        
        if not path:
            return
            
        # Progress Dialog
        self.progress = QProgressDialog(self.tr("loading"), "", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setCancelButton(None)
        self.progress.show()
        
        # Thread starten
        self.loader_thread = LoaderThread(path)
        self.loader_thread.finished.connect(self.on_load_finished)
        self.loader_thread.error.connect(self.on_load_error)
        self.loader_thread.progress.connect(self.on_load_progress)
        self.loader_thread.start()
        
    def on_load_progress(self, status):
        """Update Progress"""
        self.progress.setLabelText(self.tr(status))
        
    def on_load_finished(self, data):
        """Callback nach erfolgreichem Laden"""
        self.progress.close()
        vertices, triangles = data
        
        try:
            # Alte Darstellung entfernen
            if self.current_actor:
                self.renderer.RemoveActor(self.current_actor)
                
            # VTK-Datenstruktur erstellen
            points = vtk.vtkPoints()
            vtk_triangles = vtk.vtkCellArray()
            
            for vertex in vertices:
                if isinstance(vertex, tuple):
                    points.InsertNextPoint(vertex[0], vertex[1], vertex[2])
                else:
                    points.InsertNextPoint(vertex.x, vertex.y, vertex.z)
                    
            for face in triangles:
                triangle = vtk.vtkTriangle()
                triangle.GetPointIds().SetId(0, face[0])
                triangle.GetPointIds().SetId(1, face[1])
                triangle.GetPointIds().SetId(2, face[2])
                vtk_triangles.InsertNextCell(triangle)
                
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(vtk_triangles)
            
            # Normalen berechnen
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputData(polydata)
            normals.ComputePointNormalsOn()
            normals.Update()
            
            # Mapper und Actor
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(normals.GetOutputPort())
            
            self.current_actor = vtkActor()
            self.current_actor.SetMapper(mapper)
            self.current_actor.GetProperty().SetColor(0.9, 0.7, 0.2)
            
            self.renderer.AddActor(self.current_actor)
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()
            
        except Exception as e:
            self.show_error(f"{self.tr('load_error')}:\n{str(e)}")
            
    def on_load_error(self, error):
        """Callback bei Ladefehler"""
        self.progress.close()
        if error.startswith("unsupported:"):
            msg = f"{self.tr('unsupported')}: {error.split(':')[1]}"
        elif error == "no_solids":
            msg = self.tr("no_solids")
        else:
            msg = f"{self.tr('load_error')}:\n{error}"
        self.show_error(msg)

    def save_screenshot(self):
        """Speichert einen Screenshot"""
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("save_screenshot"),
            "",
            self.tr("png_files")
        )
        
        if path:
            try:
                self.vtk_widget.GetRenderWindow().Render()
                
                w2if = vtk.vtkWindowToImageFilter()
                w2if.SetInput(self.vtk_widget.GetRenderWindow())
                w2if.SetScale(1)
                w2if.Update()

                writer = vtk.vtkPNGWriter()
                writer.SetFileName(path)
                writer.SetInputConnection(w2if.GetOutputPort())
                writer.Write()
                
            except Exception as e:
                self.show_error(f"{self.tr('save_error')}:\n{str(e)}")

    def show_error(self, message):
        """Zeigt Fehlermeldung"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(self.tr("error"))
        msg.setText(message)
        msg.exec()

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    viewer = STEPViewer()
    viewer.show()
    sys.exit(app.exec())
