import qrcode
from ebooklib import epub
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
import sys

class QRCodeSlideshow(QWidget):
    def __init__(self):
        super().__init__()
        self.epub_file = None
        self.sentences = []
        self.current_sentence_index = 0

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.qr_code_label = QLabel(self)
        self.layout.addWidget(self.qr_code_label, alignment=Qt.AlignCenter)

        self.load_epub_button = QPushButton("EPUB-Datei laden")
        self.load_epub_button.clicked.connect(self.load_epub_file)
        self.layout.addWidget(self.load_epub_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_next_sentence)

    def load_epub_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "EPUB-Datei auswählen", "", "EPUB-Dateien (*.epub)", options=options)
        if file_name:
            self.epub_file = file_name
            self.book = epub.read_epub(self.epub_file)
            self.sentences = self.extract_sentences()
            if self.sentences:
                self.timer.start(10000)  # Starte den Timer mit einer Wartezeit von 10 Sekunden
                self.show_next_sentence()

    def extract_sentences(self):
        sentences = []
        for item in self.book.get_items():
            if isinstance(item, epub.EpubHtml):
                content = item.get_content().decode('utf-8')
                sentences.extend(content.split('.'))
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def generate_qr_code_image(self, text, size):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(text)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.convert('RGB')  # Konvertieren des Bildes in den RGB-Modus
        img = img.resize((size, size))  # Größenänderung des Bildes
        img_bytes = img.tobytes("raw", "RGB")
        qimage = QImage(img_bytes, img.size[0], img.size[1], QImage.Format_RGB888)
        return QPixmap.fromImage(qimage)

    def show_next_sentence(self):
        if self.current_sentence_index < len(self.sentences):
            sentence = self.sentences[self.current_sentence_index]
            # Berechnung der optimalen Größe des QR-Codes basierend auf der Fensterbreite
            window_width = self.width()
            qr_code_size = min(window_width * 0.8, 400)  # Maximale Größe von 400 Pixeln oder 80% der Fensterbreite
            qr_code_img = self.generate_qr_code_image(sentence, int(qr_code_size))
            self.qr_code_label.setPixmap(qr_code_img)
            self.current_sentence_index += 1

    def resizeEvent(self, event):
        # Wenn das Fenster neu skaliert wird, aktualisiere die Größe des QR-Codes
        self.show_next_sentence()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    slideshow = QRCodeSlideshow()
    slideshow.show()

    sys.exit(app.exec_())