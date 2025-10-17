"""
Модуль диалога поиска и замены
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QGroupBox, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QTextCursor, QTextDocument


class SearchReplaceDialog(QDialog):
    """Диалог поиска и замены"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Поиск и замена")
        self.setFixedSize(400, 200)
        self.setModal(True)
        self.found_count = 0
        self.editor = None
        self.init_ui()
        
    def set_editor(self, editor):
        """Устанавливает редактор для поиска"""
        self.editor = editor

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Поиск ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Найти:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Введите текст для поиска...")
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # --- Замена ---
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Заменить на:"))
        self.replace_edit = QLineEdit()
        self.replace_edit.setPlaceholderText("Введите текст для замены...")
        replace_layout.addWidget(self.replace_edit)
        layout.addLayout(replace_layout)

        # --- Опции ---
        options_group = QGroupBox("Опции")
        options_layout = QFormLayout(options_group)

        self.case_sensitive = QCheckBox()
        options_layout.addRow("Учитывать регистр:", self.case_sensitive)

        self.whole_words = QCheckBox()
        options_layout.addRow("Только целые слова:", self.whole_words)

        layout.addWidget(options_group)

        # --- Кнопки ---
        button_layout = QHBoxLayout()

        find_button = QPushButton("Найти")
        find_button.clicked.connect(self.find_text)
        find_button.setDefault(True)
        button_layout.addWidget(find_button)

        replace_button = QPushButton("Заменить")
        replace_button.clicked.connect(self.replace_text)
        button_layout.addWidget(replace_button)

        replace_all_button = QPushButton("Заменить все")
        replace_all_button.clicked.connect(self.replace_all_text)
        button_layout.addWidget(replace_all_button)

        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def count_occurrences(self, text_edit, search_text):
        """Подсчитывает количество вхождений текста"""
        content = text_edit.toPlainText()
        if not content or not search_text:
            return 0

        # Создаем регулярное выражение для подсчета
        pattern = QRegularExpression.escape(search_text)

        if self.whole_words.isChecked():
            pattern = r'\b' + pattern + r'\b'

        options = QRegularExpression.PatternOption(0)
        if not self.case_sensitive.isChecked():
            options |= QRegularExpression.CaseInsensitiveOption

        regex = QRegularExpression(pattern, options)

        # Подсчитываем все вхождения
        count = 0
        iterator = regex.globalMatch(content)
        while iterator.hasNext():
            iterator.next()
            count += 1

        return count

    def find_text(self):
        """Выполняет поиск текста"""
        search_text = self.search_edit.text()
        if not search_text:
            QMessageBox.information(self, "Поиск", "Введите текст для поиска!")
            return

        parent = self.parent()
        if hasattr(parent, 'text_edit'):
            text_edit = parent.text_edit

            # Подсчитываем общее количество вхождений
            total_count = self.count_occurrences(text_edit, search_text)

            # Настраиваем флаги поиска
            flags = QTextDocument.FindFlag(0)
            if self.case_sensitive.isChecked():
                flags |= QTextDocument.FindCaseSensitively
            if self.whole_words.isChecked():
                flags |= QTextDocument.FindWholeWords

            # Пытаемся найти от текущего положения курсора
            if text_edit.find(search_text, flags):
                QMessageBox.information(self, "Найдено",
                                        f"Текст '{search_text}' найден!\nВсего найдено: {total_count}")
            else:
                # Если не нашли — переносим курсор в начало и пробуем снова
                cursor = text_edit.textCursor()
                cursor.movePosition(QTextCursor.Start)
                text_edit.setTextCursor(cursor)
                if text_edit.find(search_text, flags):
                    QMessageBox.information(self, "Найдено",
                                            f"Текст '{search_text}' найден!\nВсего найдено: {total_count}")
                else:
                    QMessageBox.information(self, "Не найдено",
                                            f"Текст '{search_text}' не найден!")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти текстовый редактор!")

    def replace_text(self):
        """Заменяет выделенный текст"""
        search_text = self.search_edit.text()
        replace_text = self.replace_edit.text()

        if not search_text:
            QMessageBox.information(self, "Замена", "Введите текст для поиска!")
            return

        parent = self.parent()
        if hasattr(parent, 'text_edit'):
            text_edit = parent.text_edit
            cursor = text_edit.textCursor()

            # Проверяем совпадение с учетом регистра
            selected_text = cursor.selectedText()
            if not self.case_sensitive.isChecked():
                match = selected_text.lower() == search_text.lower()
            else:
                match = selected_text == search_text

            if cursor.hasSelection() and match:
                cursor.insertText(replace_text)
                QMessageBox.information(self, "Заменено", "Текст заменен!")
            else:
                QMessageBox.information(self, "Не найдено", "Выделенный текст не совпадает с искомым!")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти текстовый редактор!")

    def replace_all_text(self):
        """Заменяет все вхождения текста"""
        search_text = self.search_edit.text()
        replace_text = self.replace_edit.text()

        if not search_text:
            QMessageBox.information(self, "Замена", "Введите текст для поиска!")
            return

        parent = self.parent()
        if hasattr(parent, 'text_edit'):
            text_edit = parent.text_edit
            content = text_edit.toPlainText()

            if self.case_sensitive.isChecked():
                new_content = content.replace(search_text, replace_text)
            else:
                import re
                pattern = re.escape(search_text)
                pattern = f"(?i){pattern}"
                new_content = re.sub(pattern, replace_text, content)

            text_edit.setPlainText(new_content)
            QMessageBox.information(self, "Заменено",
                                    f"Все вхождения '{search_text}' заменены!")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось найти текстовый редактор!")
