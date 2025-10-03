# v2. STEP-Viewer-Pro
import sys
import os
import pickle
import hashlib
from pathlib import Path
import cadquery as cq
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QPushButton, QFileDialog, QMessageBox, QProgressDialog, 
                              QComboBox, QLabel, QHBoxLayout, QSlider, QCheckBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer
import vtk

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

TRANSLATIONS = {
    "de": {
        "title": "STEP Viewer Pro",
        "btn_load": "STEP Datei öffnen",
        "btn_save": "Screenshot speichern",
        "btn_clear_cache": "Cache leeren",
        "language": "Sprache",
        "quality": "Qualität",
        "use_cache": "Cache nutzen (schneller)",
        "cache_hit": "Aus Cache geladen!",
        "cache_size": "Cache-Größe",
        "select_file": "STEP-Datei auswählen",
        "step_files": "STEP Files (*.stp *.step);;Alle Dateien (*)",
        "save_screenshot": "Screenshot speichern",
        "png_files": "PNG Bilder (*.png);;Alle Dateien (*)",
        "error": "Fehler",
        "loading": "Lade STEP-Datei...",
        "processing": "Verarbeite 3D-Daten...",
        "tessellating": "Tesselliere Geometrie (kann dauern)...",
        "load_error": "Fehler beim Laden",
        "save_error": "Speicherfehler",
        "no_solids": "Die Datei enthält keine 3D-Körper",
        "unsupported": "Nicht unterstützter Dateityp",
        "cache_cleared": "Cache geleert"
    },
    "en": {
        "title": "STEP Viewer Pro",
        "btn_load": "Open STEP File",
        "btn_save": "Save Screenshot",
        "btn_clear_cache": "Clear Cache",
        "language": "Language",
        "quality": "Quality",
        "use_cache": "Use cache (faster)",
        "cache_hit": "Loaded from cache!",
        "cache_size": "Cache size",
        "select_file": "Select STEP File",
        "step_files": "STEP Files (*.stp *.step);;All Files (*)",
        "save_screenshot": "Save Screenshot",
        "png_files": "PNG Images (*.png);;All Files (*)",
        "error": "Error",
        "loading": "Loading STEP file...",
        "processing": "Processing 3D data...",
        "tessellating": "Tessellating geometry (may take time)...",
        "load_error": "Error loading file",
        "save_error": "Error saving file",
        "no_solids": "File contains no 3D bodies",
        "unsupported": "Unsupported file type",
        "cache_cleared": "Cache cleared"
    }
}

class MeshCache:
    """Cache für tessellierte Meshes"""
    def __init__(self):
        self.cache_dir = Path.home() / ".step_viewer_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
    def get_cache_key(self, filepath, quality):
        """Generiert Cache-Key aus Dateipfad und Qualität"""
        file_stat = os.stat(filepath)
        key_str = f"{filepath}_{file_stat.st_mtime}_{file_stat.st_size}_{quality}"
        return hashlib.md5(key_str.encode()).hexdigest()
        
    def get(self, filepath, quality):
        """Lädt Mesh aus Cache"""
        key = self.get_cache_key(filepath, quality)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except:
                cache_file.unlink(missing_ok=True)
        return None
        
    def set(self, filepath, quality, data):
        """Speichert Mesh im Cache"""
        key = self.get_cache_key(filepath, quality)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f)
        except Exception as e:
            print(f"Cache-Fehler: {e}")
            
    def clear(self):
        """Löscht alle Cache-Dateien"""
        for f in self.cache_dir.glob("*.pkl"):
            f.unlink()
            
    def get_size(self):
        """Gibt Cache-Größe in MB zurück"""
        total = sum(f.stat().st_size for f in self.cache_dir.glob("*.pkl"))
        return total / (1024 * 1024)

class LoaderThread(QThread):
    """Thread für asynchrones Laden von STEP-Dateien"""
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    cache_hit = pyqtSignal()
    
    def __init__(self, path, quality, use_cache):
        super().__init__()
        self.path = path
        self.quality = quality
        self.use_cache = use_cache
        self.cache = MeshCache()
        
    def run(self):
        try:
            # Cache-Check
            if self.use_cache:
                cached = self.cache.get(self.path, self.quality)
                if cached:
                    self.cache_hit.emit()
                    self.finished.emit(cached)
                    return
            
            self.progress.emit("loading")
            result = cq.importers.importStep(self.path)
            
            self.progress.emit("processing")
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
            
            self.progress.emit("tessellating")
            vertices = []
            triangles = []
            vertex_offset = 0
            
            for solid in all_solids:
                mesh = solid.tessellate(self.quality)
                vertices.extend(mesh[0])
                
                for triangle in mesh[1]:
                    triangles.append([idx + vertex_offset for idx in triangle])
                vertex_offset += len(mesh[0])
            
            data = (vertices, triangles)
            
            # Cache speichern
            if self.use_cache:
                self.cache.set(self.path, self.quality, data)
                
            self.finished.emit(data)
            
        except Exception as e:
            self.error.emit(str(e))

class STEPViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_actor = None
        self.loader_thread = None
        self.lang = "de"
        self.cache = MeshCache()
        self.init_ui()
        
    def tr(self, key):
        return TRANSLATIONS[self.lang].get(key, key)
        
    def init_ui(self):
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
        
        # Sprache
        lang_layout = QHBoxLayout()
        self.lang_label = QLabel()
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Deutsch", "English"])
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_layout.addWidget(self.lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Qualitäts-Slider
        quality_layout = QHBoxLayout()
        self.quality_label = QLabel()
        self.quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.quality_slider.setRange(1, 10)
        self.quality_slider.setValue(5)
        self.quality_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.quality_value = QLabel("0.1")
        self.quality_slider.valueChanged.connect(self.update_quality_label)
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.quality_value)
        layout.addLayout(quality_layout)
        
        # Cache-Option
        self.cache_check = QCheckBox()
        self.cache_check.setChecked(True)
        layout.addWidget(self.cache_check)
        
        # Cache-Info
        self.cache_info = QLabel()
        layout.addWidget(self.cache_info)
        
        # Buttons
        self.btn_load = QPushButton()
        self.btn_load.clicked.connect(self.load_step)
        layout.addWidget(self.btn_load)
        
        self.btn_save = QPushButton()
        self.btn_save.clicked.connect(self.save_screenshot)
        layout.addWidget(self.btn_save)
        
        self.btn_clear_cache = QPushButton()
        self.btn_clear_cache.clicked.connect(self.clear_cache)
        layout.addWidget(self.btn_clear_cache)

        # Haupt-Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.vtk_widget)
        main_layout.addWidget(control_widget)
        
        self.setCentralWidget(central_widget)
        self.update_ui_texts()
        self.update_cache_info()

        self.vtk_widget.Initialize()
        self.vtk_widget.Start()
        
    def update_quality_label(self):
        val = self.quality_slider.value()
        quality = val / 10.0
        self.quality_value.setText(f"{quality:.1f}")
        
    def update_cache_info(self):
        size = self.cache.get_size()
        self.cache_info.setText(f"{self.tr('cache_size')}: {size:.1f} MB")
        
    def update_ui_texts(self):
        self.setWindowTitle(self.tr("title"))
        self.lang_label.setText(self.tr("language") + ":")
        self.quality_label.setText(self.tr("quality") + ":")
        self.cache_check.setText(self.tr("use_cache"))
        self.btn_load.setText(self.tr("btn_load"))
        self.btn_save.setText(self.tr("btn_save"))
        self.btn_clear_cache.setText(self.tr("btn_clear_cache"))
        self.update_cache_info()
        
    def change_language(self, idx):
        self.lang = "de" if idx == 0 else "en"
        self.update_ui_texts()
        
    def clear_cache(self):
        self.cache.clear()
        self.update_cache_info()
        QMessageBox.information(self, self.tr("title"), self.tr("cache_cleared"))

    def load_step(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("select_file"),
            "",
            self.tr("step_files")
        )
        
        if not path:
            return
            
        self.progress = QProgressDialog(self.tr("loading"), "", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress.setCancelButton(None)
        self.progress.show()
        
        quality = self.quality_slider.value() / 10.0
        use_cache = self.cache_check.isChecked()
        
        self.loader_thread = LoaderThread(path, quality, use_cache)
        self.loader_thread.finished.connect(self.on_load_finished)
        self.loader_thread.error.connect(self.on_load_error)
        self.loader_thread.progress.connect(self.on_load_progress)
        self.loader_thread.cache_hit.connect(self.on_cache_hit)
        self.loader_thread.start()
        
    def on_cache_hit(self):
        self.progress.setLabelText(self.tr("cache_hit"))
        
    def on_load_progress(self, status):
        self.progress.setLabelText(self.tr(status))
        
    def on_load_finished(self, data):
        self.progress.close()
        self.update_cache_info()
        vertices, triangles = data
        
        try:
            if self.current_actor:
                self.renderer.RemoveActor(self.current_actor)
                
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
            
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputData(polydata)
            normals.ComputePointNormalsOn()
            normals.Update()
            
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
        self.progress.close()
        if error.startswith("unsupported:"):
            msg = f"{self.tr('unsupported')}: {error.split(':')[1]}"
        elif error == "no_solids":
            msg = self.tr("no_solids")
        else:
            msg = f"{self.tr('load_error')}:\n{error}"
        self.show_error(msg)

    def save_screenshot(self):
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
