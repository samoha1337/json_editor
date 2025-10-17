"""
Модуль виджета дерева для визуализации JSON структуры
"""
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt
import json
from pathlib import Path
from PyQt5.QtGui import QIcon


class JsonTreeWidget(QTreeWidget):
    """Виджет дерева для визуализации структуры JSON"""

    # Эмитируем путь как список ключей/индексов и индекс вхождения
    itemSelected = pyqtSignal(list, int)
    # Сигнал при редактировании значения: (path, new_text)
    itemEdited = pyqtSignal(list, str)

    def __init__(self):
        super().__init__()
        self.setHeaderLabel("Структура JSON")
        # Обработчики событий
        self.itemClicked.connect(self.on_item_clicked)
        self.itemChanged.connect(self.on_item_changed)
        # Вспомогательная карта для подсчета вхождений представлений значений
        self._repr_counts = {}
        # Подсчет по паре ключ-значение (для объектов), чтобы различать одинаковые значения в разных ключах
        self._kv_repr_counts = {}

    def _get_type_emoji(self, value) -> str:
        """Возвращает эмодзи в зависимости от типа значения"""
        if isinstance(value, dict):
            return "📑"  # Словарь
        elif isinstance(value, list):
            return "📋"  # Список 
        elif isinstance(value, bool):
            return "✓" if value else "❌"  # Логическое
        elif isinstance(value, (int, float)):
            return "🔢"  # Число
        elif isinstance(value, str):
            return "📝"  # Строка
        elif value is None:
            return "❓"  # None
        return "📄"  # Прочее

    def load_json(self, data):
        """Загружает JSON данные в дерево"""
        # Блокируем сигналы на время построения, чтобы избежать ложных срабатываний
        self.blockSignals(True)
        try:
            self.clear()
            self._repr_counts = {}
            self._kv_repr_counts = {}
            if isinstance(data, dict):
                self.add_dict_items(self.invisibleRootItem(), data, [])
            elif isinstance(data, list):
                self.add_list_items(self.invisibleRootItem(), data, [])
            self.expandAll()
        finally:
            self.blockSignals(False)

    def add_dict_items(self, parent, data, path):
        """Добавляет элементы словаря в дереве"""
        for key, value in data.items():
            item = QTreeWidgetItem(parent)
            emoji = self._get_type_emoji(value)
            item.setText(0, f"🔑 {key} {emoji}")
            current_path = path + [key]
            item.setData(0, Qt.UserRole, current_path)

            if isinstance(value, dict):
                self.add_dict_items(item, value, current_path)
            elif isinstance(value, list):
                self.add_list_items(item, value, current_path)
            else:
                child = QTreeWidgetItem(item)
                # Отображаем значение (чтобы редактировать без диалогов)
                repr_text = json.dumps(value, ensure_ascii=False)
                child.setText(0, repr_text)
                child.setData(0, Qt.UserRole, current_path)
                # Делаем элемент редактируемым
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                # Иконка для значения
                val_icon = self._get_icon('value')
                if val_icon:
                    child.setIcon(0, val_icon)
                # Считаем вхождение для пары ключ-значение
                key_literal = json.dumps(key, ensure_ascii=False)
                kv_key = f"{key_literal}:{repr_text}"
                kv_cnt = self._kv_repr_counts.get(kv_key, 0)
                self._kv_repr_counts[kv_key] = kv_cnt + 1
                child.setData(0, Qt.UserRole + 1, kv_cnt)
                # Сохраняем отдельно value и имя ключа, чтобы строить поиск с контекстом
                child.setData(0, Qt.UserRole + 2, repr_text)  # value repr
                child.setData(0, Qt.UserRole + 3, key)        # key name
                child.setData(0, Qt.UserRole + 4, tuple(path))  # путь контейнера (родителя)

    def add_list_items(self, parent, data, path):
        """Добавляет элементы списка в дереве"""
        for i, value in enumerate(data):
            item = QTreeWidgetItem(parent)
            emoji = self._get_type_emoji(value)
            item.setText(0, f"📌 [{i}] {emoji}")
            current_path = path + [i]
            item.setData(0, Qt.UserRole, current_path)

            if isinstance(value, dict):
                self.add_dict_items(item, value, current_path)
            elif isinstance(value, list):
                self.add_list_items(item, value, current_path)
            else:
                child = QTreeWidgetItem(item)
                repr_text = json.dumps(value, ensure_ascii=False)
                emoji = self._get_type_emoji(value)
                child.setText(0, f"{emoji} {repr_text}")
                child.setData(0, Qt.UserRole, current_path)
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                cnt = self._repr_counts.get(repr_text, 0)
                self._repr_counts[repr_text] = cnt + 1
                child.setData(0, Qt.UserRole + 1, cnt)
                child.setData(0, Qt.UserRole + 2, repr_text)
                child.setData(0, Qt.UserRole + 3, None)       # у списка нет имени ключа
                child.setData(0, Qt.UserRole + 4, tuple(path)) # путь контейнера (родительский список)

    def on_item_clicked(self, item, column):
        """Обработчик клика по элементу дерева"""
        data = item.data(0, Qt.UserRole)
        if data is None:
            return
        path = data
        # Получаем индекс вхождения, если есть
        idx = item.data(0, Qt.UserRole + 1)
        if idx is None:
            # Пытаемся взять индекс из первого листового потомка
            idx = self._find_occurrence_index_from_children(item)
            if idx is None:
                idx = 0
        self.itemSelected.emit(path, int(idx))

    def on_item_changed(self, item, column):
        """Обработчик изменения текста элемента дерева"""
        path = item.data(0, Qt.UserRole)
        if path is None:
            return

        text = item.text(0)
        new_text = text

        self.itemEdited.emit(path, new_text)

    def _find_occurrence_index_from_children(self, item):
        """Ищет у потомков первый сохраненный индекс вхождения значения в тексте.
        Возвращает int или None, если не найдено."""
        # Поиск в ширину, чтобы ближние потомки имели приоритет
        queue = [item]
        while queue:
            current = queue.pop(0)
            # Проверяем самого current, вдруг это лист
            idx = current.data(0, Qt.UserRole + 1)
            if idx is not None:
                return int(idx)
            # Добавляем детей в очередь
            for i in range(current.childCount()):
                queue.append(current.child(i))
        return None

    def _get_icon(self, name: str):
        # Иконки можно подключить позже; пока возвращаем None
        try:
            return QIcon()
        except Exception:
            return None


