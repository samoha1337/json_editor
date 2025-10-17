"""
Модуль подсветки синтаксиса JSON
"""
import re
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtCore import QObject


class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Подсветка синтаксиса JSON"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_rules()
    
    def setup_rules(self):
        # Простые цвета без тем
        theme_colors = {
            "keyword": "#0066CC",
            "string": "#00AA00", 
            "number": "#FF6600",
            "boolean": "#CC0066",
            "null": "#999999"
        }
        
        self.key_format = QTextCharFormat()
        self.key_format.setForeground(QColor(theme_colors["keyword"]))
        self.key_format.setFontWeight(QFont.Bold)
        
        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor(theme_colors["string"]))
        
        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor(theme_colors["number"]))
        
        self.bool_format = QTextCharFormat()
        self.bool_format.setForeground(QColor(theme_colors["boolean"]))
        self.bool_format.setFontWeight(QFont.Bold)
        
        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor(theme_colors["null"]))
        self.null_format.setFontItalic(True)
    
    
    def highlightBlock(self, text):
        """Выполняет подсветку блока текста"""
        # Ключи JSON
        for match in re.finditer(r'"([^"]+)"\s*:', text):
            self.setFormat(match.start(), match.end() - match.start(), self.key_format)
        
        # Строковые значения
        for match in re.finditer(r':\s*"([^"]*)"', text):
            start = match.start() + text[match.start():].index('"')
            length = match.end() - start
            self.setFormat(start, length, self.string_format)
        
        # Числа
        for match in re.finditer(r'\b\d+\.?\d*\b', text):
            self.setFormat(match.start(), match.end() - match.start(), self.number_format)
        
        # Boolean и null
        for match in re.finditer(r'\b(true|false|null)\b', text):
            if 'null' in match.group():
                self.setFormat(match.start(), match.end() - match.start(), self.null_format)
            else:
                self.setFormat(match.start(), match.end() - match.start(), self.bool_format)


