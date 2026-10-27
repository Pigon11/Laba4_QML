import sys
import os
import base64
from datetime import datetime

from PyQt5.QtCore import QUrl, QObject, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtGui import QImage, QPainter

# --- ФИКС ПУТЕЙ К ПЛАГИНАМ
import PyQt5

pyqt_path = os.path.dirname(PyQt5.__file__)
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(pyqt_path, 'Qt5', 'plugins', 'platforms')
os.environ['QT_PLUGIN_PATH'] = os.path.join(pyqt_path, 'Qt5', 'plugins')
os.environ['QML2_IMPORT_PATH'] = os.path.join(pyqt_path, 'Qt5', 'qml')


# ----------------------------------------------------


class Interface(QObject):
    def __init__(self):
        super().__init__()
        # Создаем папку для сохранений
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.save_dir = os.path.join(base_dir, "saves")
        os.makedirs(self.save_dir, exist_ok=True)

    @pyqtSlot(str)
    def saveImage(self, data_url):
        """Принимает картинку в формате base64 из QML и сохраняет в файл."""
        if not data_url:
            return

        # Отрезаем заголовок и декодируем
        _, _, b64 = data_url.partition(",")
        img = QImage.fromData(base64.b64decode(b64), "PNG")

        if img.isNull():
            print("Ошибка: не удалось прочитать изображение с доски")
            return

        # Накладываем на белый фон (чтобы не было прозрачности)
        result = QImage(img.size(), QImage.Format_RGB32)
        result.fill(Qt.white)
        painter = QPainter(result)
        painter.drawImage(0, 0, img)
        painter.end()

        # Формируем имя файла с текущей датой и временем
        name = datetime.now().strftime("drawing_%Y-%m-%d_%H-%M-%S.png")
        path = os.path.join(self.save_dir, name)

        if result.save(path):
            print("Сохранено:", path)
        else:
            print("Ошибка сохранения:", path)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    interface = Interface()
    engine = QQmlApplicationEngine()

    # Регистрируем объект в QML, чтобы таймер мог вызвать saveImage
    engine.rootContext().setContextProperty("_backend", interface)

    # Загружаем QML
    engine.load("mainWindow.qml")

    if not engine.rootObjects():
        print("Ошибка: Не удалось загрузить QML файл!")
        sys.exit(-1)

    sys.exit(app.exec())