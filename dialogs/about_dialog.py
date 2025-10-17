"""
Диалог "О программе"
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QTabWidget, QWidget, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QIcon


class AboutDialog(QDialog):
    """Диалог с информацией о программе"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("О программе - JSON Editor Pro")
        self.setFixedSize(600, 500)
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Создаем вкладки
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Вкладка "О программе"
        about_tab = self.create_about_tab()
        tab_widget.addTab(about_tab, "О программе")
        
        # Вкладка "Возможности"
        features_tab = self.create_features_tab()
        tab_widget.addTab(features_tab, "Возможности")
        
        # Вкладка "Технологии"
        tech_tab = self.create_tech_tab()
        tab_widget.addTab(tech_tab, "Технологии")
        
        
        # Кнопка закрытия
        button_layout = QHBoxLayout()
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        close_button.setDefault(True)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
    
    def create_about_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Заголовок
        title_label = QLabel("JSON Editor Pro")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Версия
        version_label = QLabel("Версия 2.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)
        
        # Описание
        description = QLabel("""
        <p align="center">
        <b>Профессиональный редактор JSON файлов</b><br><br>
        
        Мощный и удобный инструмент для работы с JSON данными.<br>
        Создан для разработчиков, тестировщиков и всех, кто работает с JSON.<br><br>
        
        <i>© 2025 JSON Editor Pro Зайцев Константин</i>
        </p>
        """)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        layout.addStretch()
        return widget
    
    def create_features_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setHtml("""
        <h3>🚀 Основные возможности:</h3>
        <ul>
        <li><b>Подсветка синтаксиса</b> - Красивое выделение JSON элементов</li>
        <li><b>Древовидная структура</b> - Визуализация JSON в виде дерева</li>
        <li><b>Автоматическая валидация</b> - Проверка корректности в реальном времени</li>
        <li><b>Форматирование</b> - Красивое форматирование и минификация</li>
        <li><b>Настройки внешнего вида</b> - Цвета, шрифты, темы</li>
        <li><b>Сохранение настроек</b> - Запоминание ваших предпочтений</li>
        <li><b>Недавние файлы</b> - Быстрый доступ к последним файлам</li>
        <li><b>Горячие клавиши</b> - Удобное управление</li>
        <li><b>Поиск и замена</b> - Поиск по содержимому</li>
        <li><b>Экспорт в другие форматы</b> - XML, YAML</li>
        <li><b>JSON Schema валидация</b> - Проверка по схеме</li>
        <li><b>Docker поддержка</b> - Запуск в контейнере</li>
        </ul>
        
        <h3>🎨 Интерфейс:</h3>
        <ul>
        <li>Современный дизайн с поддержкой тем</li>
        <li>Адаптивный интерфейс</li>
        <li>Поддержка Unicode и эмодзи</li>
        <li>Статус-бар с информацией</li>
        <li>Панель инструментов</li>
        </ul>
        """)
        layout.addWidget(features_text)
        return widget
    
    def create_tech_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        tech_text = QTextEdit()
        tech_text.setReadOnly(True)
        tech_text.setHtml("""
        <h3>🛠️ Технологический стек:</h3>
        
        <h4>Frontend:</h4>
        <ul>
        <li><b>PyQt5</b> - GUI фреймворк</li>
        <li><b>Python 3.11+</b> - Основной язык</li>
        <li><b>QSyntaxHighlighter</b> - Подсветка синтаксиса</li>
        </ul>
        
        <h4>Backend:</h4>
        <ul>
        <li><b>json</b> - Обработка JSON</li>
        <li><b>pathlib</b> - Работа с файлами</li>
        <li><b>typing</b> - Типизация</li>
        <li><b>re</b> - Регулярные выражения</li>
        </ul>
        
        <h4>DevOps:</h4>
        <ul>
        <li><b>Docker</b> - Контейнеризация</li>
        <li><b>pytest</b> - Тестирование</li>
        <li><b>Git</b> - Контроль версий</li>
        </ul>
        
        <h4>Архитектура:</h4>
        <ul>
        <li>Модульная структура</li>
        <li>MVC паттерн</li>
        <li>Настраиваемые компоненты</li>
        <li>Расширяемость</li>
        </ul>
        """)
        layout.addWidget(tech_text)
        return widget
    
