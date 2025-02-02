import sys
import cadquery as cq
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog
from cadquery.occ_impl.exporters.utils import get_occ_shape
from OCC.Display.qtDisplay import qtViewer3d

class STPViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("CadQuery STP Viewer")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # 3D-Viewer
        self.viewer = qtViewer3d(self)
        layout.addWidget(self.viewer)

        # Button zum Laden von STP-Dateien
        self.load_btn = QPushButton("STP-Datei öffnen")
        self.load_btn.clicked.connect(self.load_stp_file)
        layout.addWidget(self.load_btn)

        # Button zum Speichern der Vorschau als PNG
        self.save_btn = QPushButton("Vorschau speichern")
        self.save_btn.clicked.connect(self.save_screenshot)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)
        self.viewer.InitDriver()

    def load_stp_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "STP-Datei auswählen", "", "STEP Files (*.stp *.step)")
        if file_path:
            self.display_stp(file_path)

    def display_stp(self, file_path):
        try:
            # STP-Datei mit CadQuery laden
            shape = cq.importers.importStep(file_path)
            occ_shape = get_occ_shape(shape)

            # Im Viewer anzeigen
            self.viewer._display.DisplayShape(occ_shape, update=True)
        except Exception as e:
            print(f"Fehler beim Laden der Datei: {e}")

    def save_screenshot(self):
        self.viewer._display.View.Dump("preview.png")
        print("Screenshot gespeichert: preview.png")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = STPViewer()
    viewer.show()
    sys.exit(app.exec())
