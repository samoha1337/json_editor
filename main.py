import sys
import json
import re
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,QWidget, QPushButton, QFileDialog, QMessageBox, QToolBar,QFontComboBox, QSpinBox, QColorDialog, QLabel, QStatusBar,
QAction, QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget, QMenu, QMenuBar)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor, QIcon
from PyQt5 import uic


# Импортируем наши модули
try:
    from config.settings import settings_manager
    from dialogs.about_dialog import AboutDialog
    from dialogs.search_dialog import SearchReplaceDialog
    from dialogs.export_dialog import ExportDialog
    from widgets.syntax_highlighter import JsonSyntaxHighlighter
    from widgets.json_tree_widget import JsonTreeWidget
except ImportError as e:
    print(f"Ошибка импорта модулей: {e}")
    # Создаем заглушки для модулей
    class DummySettings:
        def get(self, key, default=None):
            defaults = {
                "font_family": "Consolas",
                "font_size": 12,
                "text_color": "#000000",
                "background_color": "#ffffff",
                "window_geometry": {"x": 100, "y": 100, "width": 1400, "height": 800},
                "splitter_sizes": [700, 300],
                "recent_files": []
            }
            return defaults.get(key, default)
        def set(self, key, value): pass
        def add_recent_file(self, path): pass
        def get_recent_files(self): return []
        def clear_recent_files(self): pass
    
    settings_manager = DummySettings()
    AboutDialog = None
    SearchReplaceDialog = None
    ExportDialog = None
    JsonSyntaxHighlighter = None
    JsonTreeWidget = None



class JsonEditor(QMainWindow):
    """Главное окно редактора JSON"""
    
    def __init__(self):
        super().__init__()
        self.current_file: Optional[Path] = None
        self.is_modified = False
        
        # Устанавливаем иконку приложения (путь от корня проекта)
        app_dir = Path(__file__).resolve().parent
        icon_path = app_dir / "icons" / "appp.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
            
        self.init_ui()
        self.setup_auto_validation()
        self.load_settings()
        self.setup_shortcuts()
    
    def init_ui(self):
        # Загружаем UI из Qt Designer файла (ui/mainwindow.ui)
        app_dir = Path(__file__).resolve().parent
        ui_path = app_dir / "ui" / "mainwindow.ui"
        uic.loadUi(str(ui_path), self)

        # Загружаем геометрию окна из настроек
        geometry = settings_manager.get("window_geometry")
        self.setGeometry(
            geometry["x"], geometry["y"],
            geometry["width"], geometry["height"]
        )

        # Привязываем основные виджеты по objectName
        self.text_edit: QTextEdit = self.findChild(QTextEdit, "text_edit")
        self.splitter: QSplitter = self.findChild(QSplitter, "splitter")
        tree_placeholder: QTreeWidget = self.findChild(QTreeWidget, "tree_widget")
        self.tab_widget: QTabWidget = self.findChild(QTabWidget, "tab_widget")

        # Подключаем сигналы редактора
        self.text_edit.setFont(QFont("Consolas", 12))
        self.text_edit.textChanged.connect(self.on_text_changed)

        # Подсветка синтаксиса
        if JsonSyntaxHighlighter:
            self.highlighter = JsonSyntaxHighlighter(self.text_edit.document())
        else:
            self.highlighter = None

        # Заменяем QTreeWidget на наш JsonTreeWidget, если доступен
        if JsonTreeWidget:
            self.tree_widget = JsonTreeWidget()
            self.tree_widget.itemSelected.connect(self.on_tree_item_selected)
            self.tree_widget.itemEdited.connect(self.on_tree_item_edited)
            # Вставляем в сплиттер вместо placeholder
            # 0 - QTextEdit, 1 - placeholder tree
            # Удаляем placeholder и добавляем новый
            if tree_placeholder is not None and self.splitter is not None:
                # Сохраняем индекс
                idx = self.splitter.indexOf(tree_placeholder)
                tree_placeholder.setParent(None)
                self.splitter.insertWidget(idx if idx >= 0 else 1, self.tree_widget)
            else:
                self.splitter.addWidget(self.tree_widget)
        else:
            self.tree_widget = tree_placeholder
            if self.tree_widget is not None:
                self.tree_widget.setHeaderLabel("JSON Structure")

        # Загружаем размеры сплиттера из настроек
        splitter_sizes = settings_manager.get("splitter_sizes", [700, 300])
        if self.splitter is not None:
            self.splitter.setSizes(splitter_sizes)

        # Находим элементы управления из верхней панели
        self.font_combo: QFontComboBox = self.findChild(QFontComboBox, "font_combo")
        self.font_size: QSpinBox = self.findChild(QSpinBox, "font_size")
        text_color_btn: QPushButton = self.findChild(QPushButton, "text_color_btn")
        bg_color_btn: QPushButton = self.findChild(QPushButton, "bg_color_btn")
        close_doc_btn: QPushButton = self.findChild(QPushButton, "close_doc_btn")

        if self.font_combo:
            self.font_combo.setCurrentFont(QFont("Consolas"))
            self.font_combo.currentFontChanged.connect(self.change_font)
        if self.font_size:
            self.font_size.setRange(6, 72)
            self.font_size.setValue(12)
            self.font_size.valueChanged.connect(self.change_font_size)
        if text_color_btn:
            text_color_btn.clicked.connect(self.change_text_color)
        if bg_color_btn:
            bg_color_btn.clicked.connect(self.change_bg_color)
        if close_doc_btn:
            close_doc_btn.clicked.connect(self.close_document)

        # Действия меню и тулбара
        if hasattr(self, 'actionOpen'):
            self.actionOpen.triggered.connect(self.open_file)
        if hasattr(self, 'actionSave'):
            self.actionSave.triggered.connect(self.save_file)
        if hasattr(self, 'actionSaveAs'):
            self.actionSaveAs.triggered.connect(self.save_file_as)
        if hasattr(self, 'actionExit'):
            self.actionExit.triggered.connect(self.close)
        if hasattr(self, 'actionFind'):
            self.actionFind.triggered.connect(self.show_search_dialog)
        if hasattr(self, 'actionExport'):
            self.actionExport.triggered.connect(self.show_export_dialog)
        if hasattr(self, 'actionAbout'):
            self.actionAbout.triggered.connect(self.show_about_dialog)
        if hasattr(self, 'actionFormat'):
            self.actionFormat.triggered.connect(self.format_json)
        if hasattr(self, 'actionMinify'):
            self.actionMinify.triggered.connect(self.minify_json)
        if hasattr(self, 'actionValidate'):
            self.actionValidate.triggered.connect(self.validate_json)

        # Статус бар и информационные метки
        self.status_bar = self.statusBar() if hasattr(self, 'statusBar') else QStatusBar()
        if not self.status_bar:
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
        self.validation_label = QLabel("✅ Корректный JSON")
        self.validation_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.validation_label)
        self.info_label = QLabel("Готово")
        self.status_bar.addWidget(self.info_label)

        # Меню недавних файлов
        self.recent_files_menu = getattr(self, 'menuRecentFiles', None)
        self.update_title()
        self.load_recent_files()
    
    def create_menu_bar(self):
        """Совместимость: меню определяется в Qt Designer."""
        pass
    
    def create_toolbar(self):
        """Совместимость: панель инструментов определяется в Qt Designer."""
        pass
    
    def setup_auto_validation(self):
        """Автоматическая валидация при изменении текста"""
        self.validation_timer = QTimer()
        self.validation_timer.timeout.connect(self.auto_validate)
        self.validation_timer.setSingleShot(True)
    
    def on_text_changed(self):
        self.is_modified = True
        self.update_title()
        self.validation_timer.start(500)  # Валидация через 500мс после остановки печати
    
    def auto_validate(self):
        """Автоматическая валидация без сообщений"""
        try:
            text = self.text_edit.toPlainText().strip()
            if not text:
                self.validation_label.setText("⚠️ Пустой файл")
                self.validation_label.setStyleSheet("color: orange; font-weight: bold;")
                return
            
            data = json.loads(text)
            self.validation_label.setText("✅ Корректный JSON")
            self.validation_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Обновляем дерево
            self.tree_widget.load_json(data)
            
        except json.JSONDecodeError as e:
            self.validation_label.setText(f"❌ Ошибка: Line {e.lineno}")
            self.validation_label.setStyleSheet("color: red; font-weight: bold;")
            self.tree_widget.clear()
    
    def open_file(self):
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Файл изменен",
                "Хотите сохранить изменения?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open JSON File", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Проверяем валидность
                    json.loads(content)
                    self.text_edit.setPlainText(content)
                    self.current_file = Path(file_path)
                    self.is_modified = False
                    self.update_title()
                    self.info_label.setText(f"Opened: {file_path}")
                    
                    # Добавляем в недавние файлы
                    settings_manager.add_recent_file(file_path)
                    self.load_recent_files()
            except json.JSONDecodeError as e:
                QMessageBox.warning(
                    self, "Некорректный JSON",
                    f"Этот файл содержит некорректный JSON:\n{str(e)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Ошибка",
                    f"Не удается открыть:\n{str(e)}"
                )
    
    def save_file(self):
        if self.current_file:
            return self._save_to_file(self.current_file)
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как JSON File", "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            return self._save_to_file(Path(file_path))
        return False

    def close_document(self):
        """Закрывает текущий документ"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Документ изменен",
                "Хотите сохранить изменения перед закрытием?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_file():
                    return
            elif reply == QMessageBox.Cancel:
                return

        self.text_edit.clear()
        self.tree_widget.clear()
        self.current_file = None
        self.is_modified = False
        self.update_title()
        self.validation_label.setText("⚠️ Пустой документ")
        self.validation_label.setStyleSheet("color: orange; font-weight: bold;")
        self.info_label.setText("Документ закрыт")
    
    def _save_to_file(self, file_path: Path):
        try:
            # Валидация перед сохранением
            content = self.text_edit.toPlainText()
            json.loads(content)  # Проверка валидности
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_file = file_path
            self.is_modified = False
            self.update_title()
            self.info_label.setText(f"Сохранено: {file_path}")
            
            # Добавляем в недавние файлы
            settings_manager.add_recent_file(str(file_path))
            self.load_recent_files()
            
            QMessageBox.information(self, "Успешно!", "Файл сохранен успешно!")
            return True
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self, "Некорректный JSON!",
                f"Не удалось сохранить JSON:\n{str(e)}"
            )
            return False
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка!",
                f"Не удалось сохранить по этому пути:\n{str(e)}"
            )
            return False
    
    def format_json(self):
        try:
            text = self.text_edit.toPlainText()
            data = json.loads(text)
            formatted = json.dumps(data, indent=2, ensure_ascii=False)
            self.text_edit.setPlainText(formatted)
            self.info_label.setText("JSON отформатирован успешно!")
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self, "Ошибка в форматировании в JSON!",
                f"Некорректный формат JSON:\n{str(e)}"
            )
    
    def minify_json(self):
        try:
            text = self.text_edit.toPlainText()
            data = json.loads(text)
            minified = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
            self.text_edit.setPlainText(minified)
            self.info_label.setText("JSON минифицировать успешно!")
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self, "Некорректный JSON",
                f"Не удалось минифицировать JSON:\n{str(e)}"
            )
    
    def validate_json(self):
        try:
            text = self.text_edit.toPlainText()
            if not text.strip():
                QMessageBox.warning(self, "Пустой документ!", "Этот документ пустой!")
                return
            
            data = json.loads(text)
            QMessageBox.information(
                self, "Корректный JSON",
                f"✅ Документ соответствует формату JSON!\n\nТип: {type(data).__name__}"
            )
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self, "Некорректный JSON",
                f"❌ JSON Ошибка:\n\nСтрока {e.lineno}, Столбец {e.colno}\n{e.msg}"
            )
    
    def change_font(self, font):
        current_font = self.text_edit.font()
        current_font.setFamily(font.family())
        self.text_edit.setFont(current_font)
        settings_manager.set("font_family", font.family())
    
    def change_font_size(self, size):
        current_font = self.text_edit.font()
        current_font.setPointSize(size)
        self.text_edit.setFont(current_font)
        settings_manager.set("font_size", size)

    def change_text_color(self):
        """Изменяет цвет текста"""
        color = QColorDialog.getColor()
        if color.isValid():
            settings_manager.set("text_color", color.name())
            self.apply_colors()

    def change_bg_color(self):
        """Изменяет цвет фона"""
        color = QColorDialog.getColor()
        if color.isValid():
            settings_manager.set("background_color", color.name())
            self.apply_colors()
    
    def apply_colors(self):
        """Применяет сохраненные цвета"""
        text_color = settings_manager.get("text_color", "#000000")
        bg_color = settings_manager.get("background_color", "#ffffff")
        
        # Применяем цвета к текстовому редактору
        self.text_edit.setStyleSheet(
            f"QTextEdit {{ color: {text_color}; background-color: {bg_color}; }}"
        )
    
    def load_settings(self):
        """Загружает настройки приложения"""
        # Загружаем настройки шрифта
        font_family = settings_manager.get("font_family", "Consolas")
        font_size = settings_manager.get("font_size", 12)
        
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        
        # Применяем сохраненные цвета
        self.apply_colors()
        
        # Обновляем элементы управления
        if hasattr(self, 'font_combo'):
            self.font_combo.setCurrentFont(font)
        if hasattr(self, 'font_size'):
            self.font_size.setValue(font_size)
    
    def setup_shortcuts(self):
        """Настраивает горячие клавиши"""
        # Ctrl+Shift+F - замена (Ctrl+F уже определен в меню)
        replace_action = QAction(self)
        replace_action.setShortcut("Ctrl+Shift+F")
        replace_action.triggered.connect(self.show_search_dialog)
        self.addAction(replace_action)
        
        # Ctrl+W - закрыть документ
        close_doc_shortcut = QAction(self)
        close_doc_shortcut.setShortcut("Ctrl+W")
        close_doc_shortcut.triggered.connect(self.close_document)
        self.addAction(close_doc_shortcut)
    
    def get_current_editor(self):
        """Возвращает текущий редактор текста для диалогов (поиск/замена и т.п.)"""
        return getattr(self, 'text_edit', None)
    
    def show_search_dialog(self):
        """Показывает диалог поиска и замены"""
        if not SearchReplaceDialog:
            QMessageBox.information(self, "Поиск", "Функция поиска недоступна в базовой версии")
            return
            
        editor = self.get_current_editor()
        if not editor:
            QMessageBox.warning(self, "Поиск", "Сначала откройте файл для поиска")
            return
            
        dialog = SearchReplaceDialog(self)
        dialog.set_editor(editor)
        dialog.exec_()
    
    def show_export_dialog(self):
        """Показывает диалог экспорта"""
        if ExportDialog:
            try:
                text = self.text_edit.toPlainText()
                if not text.strip():
                    QMessageBox.warning(self, "Пустой документ", "Нет данных для экспорта!")
                    return
                
                data = json.loads(text)
                dialog = ExportDialog(data, self)
                dialog.exec_()
            except json.JSONDecodeError:
                QMessageBox.warning(self, "Некорректный JSON", "Не удалось экспортировать некорректный JSON!")
        else:
            QMessageBox.information(self, "Экспорт", "Функция экспорта недоступна в базовой версии")
    
    def show_about_dialog(self):
        """Показывает диалог 'О программе'"""
        if AboutDialog:
            dialog = AboutDialog(self)
            dialog.exec_()
        else:
            QMessageBox.about(self, "О программе", 
                "JSON Editor Pro v2.0.0\n\n"
                "Профессиональный редактор JSON файлов\n"
                "Создан для разработчиков и тестировщиков\n\n"
                "© 2025 JSON Editor Pro Team")
    
    def load_recent_files(self):
        """Загружает список недавних файлов в меню"""
        recent_files = settings_manager.get_recent_files()
        if self.recent_files_menu is None:
            # Если меню недавних файлов не найдено из UI, создадим временное
            menubar = self.menuBar()
            file_menu = None
            for a in menubar.actions():
                if a.text() == "Файл":
                    file_menu = a.menu()
                    break
            if file_menu is not None:
                self.recent_files_menu = file_menu.addMenu("Недавние файлы")
        if self.recent_files_menu is None:
            return
        self.recent_files_menu.clear()
        
        for file_path in recent_files:
            if Path(file_path).exists():
                action = QAction(Path(file_path).name, self)
                action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
                self.recent_files_menu.addAction(action)
        
        if recent_files:
            self.recent_files_menu.addSeparator()
            clear_action = QAction("Очистить список", self)
            clear_action.triggered.connect(self.clear_recent_files)
            self.recent_files_menu.addAction(clear_action)
    
    def open_recent_file(self, file_path):
        """Открывает недавний файл"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                json.loads(content)  # Проверка валидности
                self.text_edit.setPlainText(content)
                self.current_file = Path(file_path)
                self.is_modified = False
                self.update_title()
                self.info_label.setText(f"Opened: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удается открыть файл:\n{str(e)}")
    
    def clear_recent_files(self):
        """Очищает список недавних файлов"""
        settings_manager.clear_recent_files()
        self.load_recent_files()
    
    def _get_by_path(self, data, path):
        cur = data
        for p in path:
            cur = cur[p]
        return cur

    def _set_by_path(self, data, path, value):
        cur = data
        for p in path[:-1]:
            cur = cur[p]
        last = path[-1]
        cur[last] = value

    def on_tree_item_selected(self, path, occurrence=0):
        """Быстрое выделение значения в тексте без повторного парсинга JSON.
        При наличии у текущего элемента заранее сохраненного текста значения
        (JsonTreeWidget кладет в UserRole+2), используем его напрямую.
        """
        text = self.text_edit.toPlainText()
        rep = None
        try:
            current_item = self.tree_widget.currentItem()
            kv_key_literal = None
            if current_item is not None:
                rep = current_item.data(0, Qt.UserRole + 2)  # значение как JSON-строка
                key_name = current_item.data(0, Qt.UserRole + 3)
                container_path = current_item.data(0, Qt.UserRole + 4)  # путь родителя
                # Если есть имя ключа (объект), строим шаблон "\"key\": <value>"
                if key_name is not None and rep is not None:
                    key_literal = json.dumps(key_name, ensure_ascii=False)
                    kv_key_literal = f"{key_literal}: {rep}"
        except Exception:
            rep = None
            kv_key_literal = None

        if rep is None:
            # Фолбэк: парсим только если нужно
            try:
                data = json.loads(text)
                value = self._get_by_path(data, path)
                rep = json.dumps(value, ensure_ascii=False)
            except Exception:
                self.info_label.setText(f"Выбран: {path}")
                return

        # Поиск n-го вхождения. Сначала пробуем более точный паттерн ключ:значение,
        # чтобы не схватить чужие такие же значения под другим ключом.
        start = 0
        found_idx = -1
        target_string = kv_key_literal if kv_key_literal else rep
        for i in range(occurrence + 1):
            found_idx = text.find(target_string, start)
            if found_idx == -1:
                break
            start = found_idx + len(target_string)

        if found_idx != -1:
            cursor = self.text_edit.textCursor()
            cursor.setPosition(found_idx)
            cursor.setPosition(found_idx + len(target_string), QTextCursor.KeepAnchor)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.setFocus()
            self.info_label.setText(f"Выбран: {path} (#{occurrence + 1})")
        else:
            self.info_label.setText(f"Выбран: {path} (не найдено в тексте)")

    def on_tree_item_edited(self, path, new_text):
        """Обработчик редактирования значения в дереве — обновляет JSON в тексте"""
        try:
            text = self.text_edit.toPlainText()
            data = json.loads(text)

            # Пытаемся распарсить новое значение как JSON-литерал
            try:
                new_value = json.loads(new_text)
            except Exception:
                # Если не удалось — используем строку без дополнительной обработки
                new_value = new_text

            # Устанавливаем новое значение по пути
            self._set_by_path(data, path, new_value)

            # Обновляем текст редактора (форматируем красиво)
            new_text_repr = json.dumps(data, indent=2, ensure_ascii=False)
            self.text_edit.setPlainText(new_text_repr)
            self.is_modified = True
            self.update_title()
            self.info_label.setText(f"Значение обновлено: {path}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка обновления", f"Не удалось обновить значение: {str(e)}")
    
    def update_title(self):
        title = "JSON-Блокнот Pro"
        if self.current_file:
            title += f" - {self.current_file.name}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def closeEvent(self, event):
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Вы изменили файл.",
                "Хотите сохранить файлы перед изменением?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_file():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        
        # Сохраняем настройки окна
        geometry = self.geometry()
        settings_manager.set("window_geometry", {
            "x": geometry.x(),
            "y": geometry.y(),
            "width": geometry.width(),
            "height": geometry.height()
        })
        
        # Сохраняем размеры сплиттера
        if hasattr(self, 'splitter'):
            settings_manager.set("splitter_sizes", self.splitter.sizes())
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    editor = JsonEditor()
    editor.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

