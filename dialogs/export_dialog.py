"""
Модуль диалога экспорта данных
"""
import json
import xml.etree.ElementTree as ET
import io
from typing import Any, Dict, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFileDialog, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt


class ExportDialog(QDialog):
    """Диалог экспорта в другие форматы"""
    
    def __init__(self, json_data, parent=None):
        super().__init__(parent)
        self.json_data = json_data
        self.setWindowTitle("Экспорт данных")
        self.setFixedSize(500, 400)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Выбор формата
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Формат экспорта:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["XML", "YAML"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Предварительный просмотр
        layout.addWidget(QLabel("Предварительный просмотр:"))
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        layout.addWidget(self.preview_edit)
        
        # Обновляем предварительный просмотр при изменении формата
        self.format_combo.currentTextChanged.connect(self.update_preview)
        self.update_preview()
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        export_button = QPushButton("Экспортировать")
        export_button.clicked.connect(self.export_data)
        button_layout.addWidget(export_button)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def update_preview(self):
        """Обновляет предварительный просмотр"""
        format_type = self.format_combo.currentText()
        try:
            if format_type == "XML":
                preview = self.json_to_xml(self.json_data)
            elif format_type == "YAML":
                preview = self.json_to_yaml(self.json_data)
            else:
                preview = "Неподдерживаемый формат"
            
            self.preview_edit.setPlainText(preview)
        except Exception as e:
            self.preview_edit.setPlainText(f"Ошибка конвертации: {str(e)}")
    
    def json_to_xml(self, data, root_name="root"):
        """Конвертация JSON в XML"""
        def dict_to_xml(d, root):
            for key, value in d.items():
                if isinstance(value, dict):
                    child = ET.SubElement(root, str(key))
                    dict_to_xml(value, child)
                elif isinstance(value, list):
                    for item in value:
                        child = ET.SubElement(root, str(key))
                        if isinstance(item, dict):
                            dict_to_xml(item, child)
                        else:
                            child.text = str(item)
                else:
                    child = ET.SubElement(root, str(key))
                    child.text = str(value)
        
        root = ET.Element(root_name)
        if isinstance(data, dict):
            dict_to_xml(data, root)
        else:
            root.text = str(data)
        
        return ET.tostring(root, encoding='unicode')
    
    def json_to_yaml(self, data, indent=0):
        """Конвертация JSON в YAML"""
        result = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result.append("  " * indent + f"{key}:")
                    result.append(self.json_to_yaml(value, indent + 1))
                else:
                    result.append("  " * indent + f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    result.append("  " * indent + "-")
                    result.append(self.json_to_yaml(item, indent + 1))
                else:
                    result.append("  " * indent + f"- {item}")
        else:
            return "  " * indent + str(data)
        
        return "\n".join(result)
    
    def export_data(self):
        """Экспортирует данные в выбранный формат"""
        format_type = self.format_combo.currentText()
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Сохранить как {format_type}",
            "", f"{format_type} Files (*.{format_type.lower()})"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.preview_edit.toPlainText())
                QMessageBox.information(self, "Успешно!", f"Данные экспортированы в {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка!", f"Не удалось сохранить файл:\n{str(e)}")
