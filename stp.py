# STEP Viewer Pro - Created By AI with help by a Human (me)
import sys
import os
import cadquery as cq
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkActor, vtkPolyDataMapper, vtkRenderer
import vtk

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"  # HighDPI-Fix für Windows

class STEPViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_actor = None
        self.init_ui()
        
    def init_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        self.setWindowTitle("STEP Viewer Pro")
        self.setGeometry(100, 100, 1024, 768)

        # VTK Widget
        self.vtk_widget = QVTKRenderWindowInteractor(self)
        self.renderer = vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.renderer.SetBackground(0.15, 0.15, 0.15)  # Dunkler Hintergrund

        # Steuerungselemente
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        btn_load = QPushButton("STEP Datei öffnen")
        btn_load.clicked.connect(self.load_step)
        layout.addWidget(btn_load)
        
        btn_save = QPushButton("Screenshot speichern")
        btn_save.clicked.connect(self.save_screenshot)
        layout.addWidget(btn_save)

        # Haupt-Layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self.vtk_widget)
        main_layout.addWidget(control_widget)
        
        self.setCentralWidget(central_widget)

        # VTK initialisieren
        self.vtk_widget.Initialize()
        self.vtk_widget.Start()

    def load_step(self):
        """Lädt und zeigt eine STEP-Datei an"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "STEP-Datei auswählen",
            "",
            "STEP Files (*.stp *.step);;Alle Dateien (*)"
        )
        
        if not path:
            return

        try:
            # Alte Darstellung entfernen
            if self.current_actor:
                self.renderer.RemoveActor(self.current_actor)
                self.current_actor = None

            # STEP-Datei importieren
            result = cq.importers.importStep(path)
            print(f"Importiertes Objekt-Typ: {type(result)}")  # Debug-Ausgabe

            # Solids extrahieren
            all_solids = []
            if isinstance(result, cq.Assembly):
                all_solids = [solid for child in result.children for solid in child.obj.Solids()]
            elif isinstance(result, cq.Workplane):
                all_solids = result.objects if result.objects else [result.val()]
            elif isinstance(result, (cq.Compound, cq.Shape)):
                all_solids = [result]
            else:
                raise ValueError(f"Nicht unterstützter Dateityp: {type(result)}")

            if not all_solids:
                raise ValueError("Die Datei enthält keine 3D-Körper")

            # Mesh für jeden Solid erstellen und kombinieren
            vertices = []
            triangles = []
            vertex_offset = 0

            for solid in all_solids:
                mesh = solid.tessellate(0.1)  # Tessellation mit 0.1mm Genauigkeit
                
                # Vertices hinzufügen
                vertices.extend(mesh[0])
                
                # Dreiecke mit Offset hinzufügen
                for triangle in mesh[1]:
                    triangles.append([idx + vertex_offset for idx in triangle])
                
                vertex_offset += len(mesh[0])

            # VTK-Datenstruktur erstellen
            points = vtk.vtkPoints()
            vtk_triangles = vtk.vtkCellArray()

            # Punkte hinzufügen
            for vertex in vertices:
                if isinstance(vertex, tuple):
                    points.InsertNextPoint(vertex[0], vertex[1], vertex[2])
                else:
                    points.InsertNextPoint(vertex.x, vertex.y, vertex.z)

            # Dreiecke hinzufügen
            for face in triangles:
                triangle = vtk.vtkTriangle()
                triangle.GetPointIds().SetId(0, face[0])
                triangle.GetPointIds().SetId(1, face[1])
                triangle.GetPointIds().SetId(2, face[2])
                vtk_triangles.InsertNextCell(triangle)

            # PolyData konfigurieren
            polydata = vtk.vtkPolyData()
            polydata.SetPoints(points)
            polydata.SetPolys(vtk_triangles)

            # Normalen berechnen
            normals = vtk.vtkPolyDataNormals()
            normals.SetInputData(polydata)
            normals.ComputePointNormalsOn()
            normals.Update()

            # Mapper und Actor erstellen
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(normals.GetOutputPort())

            self.current_actor = vtkActor()
            self.current_actor.SetMapper(mapper)
            self.current_actor.GetProperty().SetColor(0.9, 0.7, 0.2)  # Goldene Farbe

            # Zur Szene hinzufügen
            self.renderer.AddActor(self.current_actor)
            self.renderer.ResetCamera()
            self.vtk_widget.GetRenderWindow().Render()

        except Exception as e:
            self.show_error(f"Fehler beim Laden:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def save_screenshot(self):
        """Speichert einen Screenshot der aktuellen Ansicht"""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Screenshot speichern",
            "",
            "PNG Bilder (*.png);;Alle Dateien (*)"
        )
        
        if path:
            try:
                # Rendering erzwingen
                self.vtk_widget.GetRenderWindow().Render()
                
                # Bild erfassen
                w2if = vtk.vtkWindowToImageFilter()
                w2if.SetInput(self.vtk_widget.GetRenderWindow())
                w2if.SetScale(1)
                w2if.Update()

                # Datei speichern
                writer = vtk.vtkPNGWriter()
                writer.SetFileName(path)
                writer.SetInputConnection(w2if.GetOutputPort())
                writer.Write()

            except Exception as e:
                self.show_error(f"Speicherfehler:\n{str(e)}")

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Fehler")
        msg.setText(message)
        msg.exec()

if __name__ == "__main__":
    # HighDPI-Einstellungen für Windows
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    viewer = STEPViewer()
    viewer.show()
    sys.exit(app.exec())
