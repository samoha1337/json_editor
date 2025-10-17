import pytest
import json
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from main import JsonEditor, JsonTreeWidget
from unittest.mock import patch

os.environ["PYTEST_RUNNING"] = "1"

@pytest.fixture(scope='session')
def qapp():
    """Фикстура для QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def editor(qapp):
    """Фикстура для создания экземпляра редактора"""
    window = JsonEditor()
    yield window
    window.close()


@pytest.fixture
def sample_json():
    """Образец валидного JSON"""
    return {
        "name": "Test User",
        "age": 30,
        "active": True,
        "address": {
            "city": "Moscow",
            "country": "Russia"
        },
        "hobbies": ["reading", "coding", "gaming"]
    }


@pytest.fixture
def temp_json_file(tmp_path, sample_json):
    """Временный JSON файл для тестов"""
    file_path = tmp_path / "test.json"
    with open(file_path, 'w') as f:
        json.dump(sample_json, f, indent=2)
    return file_path



@pytest.fixture(autouse=True)
def auto_mock_qmessagebox():
    with patch("PyQt5.QtWidgets.QMessageBox.information", return_value=None), \
         patch("PyQt5.QtWidgets.QMessageBox.warning", return_value=None), \
         patch("PyQt5.QtWidgets.QMessageBox.critical", return_value=None), \
         patch("PyQt5.QtWidgets.QMessageBox.question", return_value=3):
        yield

class TestJsonEditor:
    """Тесты для основного класса JsonEditor"""
    
    def test_editor_initialization(self, editor):
        """Тест инициализации редактора"""
        assert editor.windowTitle() == "JSON-Блокнот Pro"
        assert editor.current_file is None
        assert editor.is_modified is False
        assert editor.text_edit is not None
        assert editor.tree_widget is not None
    
    def test_text_modification_flag(self, editor):
        """Тест флага модификации при изменении текста"""
        assert editor.is_modified is False
        editor.text_edit.setPlainText('{"test": true}')
        assert editor.is_modified is True
        assert "*" in editor.windowTitle()
    
    def test_format_json(self, editor, sample_json):
        """Тест форматирования JSON"""
        # Минифицированный JSON
        minified = json.dumps(sample_json, separators=(',', ':'))
        editor.text_edit.setPlainText(minified)
        
        editor.format_json()
        
        formatted_text = editor.text_edit.toPlainText()
        parsed = json.loads(formatted_text)
        assert parsed == sample_json
        assert '\n' in formatted_text  # Проверка, что есть переносы строк
    
    def test_minify_json(self, editor, sample_json):
        """Тест минификации JSON"""
        formatted = json.dumps(sample_json, indent=2)
        editor.text_edit.setPlainText(formatted)
        
        editor.minify_json()
        
        minified_text = editor.text_edit.toPlainText()
        assert '\n' not in minified_text
        parsed = json.loads(minified_text)
        assert parsed == sample_json
    
    def test_save_to_file(self, editor, sample_json, tmp_path):
        """Тест сохранения в файл"""
        file_path = tmp_path / "output.json"
        editor.text_edit.setPlainText(json.dumps(sample_json, indent=2))
        
        result = editor._save_to_file(file_path)
        
        assert result is True
        assert file_path.exists()
        with open(file_path, 'r') as f:
            saved_data = json.load(f)
        assert saved_data == sample_json
        assert editor.is_modified is False
    
    def test_save_invalid_json(self, editor, tmp_path):
        """Тест попытки сохранения невалидного JSON"""
        file_path = tmp_path / "invalid.json"
        editor.text_edit.setPlainText('{"Некорректно": }')
        
        result = editor._save_to_file(file_path)
        
        assert result is False
        assert not file_path.exists()
    
    def test_font_change(self, editor):
        """Тест изменения шрифта"""
        original_font = editor.text_edit.font()
        new_size = 18
        
        editor.font_size.setValue(new_size)
        editor.change_font_size(new_size)
        
        current_font = editor.text_edit.font()
        assert current_font.pointSize() == new_size
    
    def test_validation_valid_json(self, editor, sample_json):
        """Тест валидации корректного JSON"""
        editor.text_edit.setPlainText(json.dumps(sample_json))
        editor.auto_validate()
        
        assert "✅ Корректный JSON" in editor.validation_label.text()
    
    def test_validation_invalid_json(self, editor):
        """Тест валидации некорректного JSON"""
        editor.text_edit.setPlainText('{"некорректного": }')
        editor.auto_validate()
        
        assert "❌" in editor.validation_label.text()
    
    def test_validation_empty_json(self, editor):
        """Тест валидации пустого документа"""
        editor.text_edit.setPlainText('')
        editor.auto_validate()
        
        assert "⚠️ Пустой" in editor.validation_label.text()

    def test_color_changes_and_persistence(self, editor):
        """Изменение цветов и применение стилей"""
        # Имитируем выбор цветов
        from config.settings import settings_manager
        settings_manager.set("text_color", "#112233")
        settings_manager.set("background_color", "#f0f0f0")
        editor.apply_colors()
        style = editor.text_edit.styleSheet()
        assert "#112233" in style and "#f0f0f0" in style

    def test_recent_files_menu_population(self, editor, tmp_path):
        """Пункты меню недавних файлов создаются"""
        file_a = tmp_path / "a.json"
        file_a.write_text('{"a":1}')
        from config.settings import settings_manager
        settings_manager.add_recent_file(str(file_a))
        editor.load_recent_files()
        assert editor.recent_files_menu is not None
        assert editor.recent_files_menu.actions()


class TestJsonTreeWidget:
    """Тесты для виджета дерева JSON"""
    
    def test_tree_initialization(self, qapp):
        """Тест инициализации дерева"""
        tree = JsonTreeWidget()
        assert tree.topLevelItemCount() == 0
    
    def test_load_dict(self, qapp, sample_json):
        """Тест загрузки словаря в дерево"""
        tree = JsonTreeWidget()
        tree.load_json(sample_json)
        
        assert tree.topLevelItemCount() > 0
    
    def test_load_list(self, qapp):
        """Тест загрузки списка в дерево"""
        tree = JsonTreeWidget()
        data = [1, 2, 3, {"key": "value"}]
        tree.load_json(data)
        
        assert tree.topLevelItemCount() > 0
    
    def test_nested_structure(self, qapp, sample_json):
        """Тест отображения вложенной структуры"""
        tree = JsonTreeWidget()
        tree.load_json(sample_json)
        
        # Проверяем, что есть дочерние элементы
        root_item = tree.topLevelItem(0)
        assert root_item.childCount() > 0


class TestJsonValidation:
    """Тесты валидации JSON"""
    
    @pytest.mark.parametrize("valid_json", [
        '{"key": "value"}',
        '[1, 2, 3]',
        '{"nested": {"data": true}}',
        '{"number": 42, "float": 3.14}',
        '{"null": null, "bool": false}',
    ])
    def test_valid_json_strings(self, editor, valid_json):
        """Тест различных валидных JSON строк"""
        editor.text_edit.setPlainText(valid_json)
        editor.auto_validate()
        assert "✅" in editor.validation_label.text()
    
    @pytest.mark.parametrize("invalid_json", [
        '{"key": }',
        '{key: "value"}',
        '{"key": "value",}',
        '[1, 2, 3,]',
        "{'key': 'value'}",  # Одинарные кавычки
    ])
    def test_invalid_json_strings(self, editor, invalid_json):
        """Тест различных невалидных JSON строк"""
        editor.text_edit.setPlainText(invalid_json)
        editor.auto_validate()
        assert "❌" in editor.validation_label.text()


class TestFileOperations:
    """Тесты файловых операций"""
    
    def test_update_title_with_file(self, editor):
        """Тест обновления заголовка с именем файла"""
        editor.current_file = Path("test.json")
        editor.update_title()
        assert "test.json" in editor.windowTitle()
    
    def test_update_title_modified(self, editor):
        """Тест обновления заголовка с флагом модификации"""
        editor.is_modified = True
        editor.update_title()
        assert "*" in editor.windowTitle()
    
    def test_json_roundtrip(self, editor, sample_json, tmp_path):
        """Тест полного цикла: загрузка -> изменение -> сохранение"""
        # Сохраняем
        file_path = tmp_path / "roundtrip.json"
        editor.text_edit.setPlainText(json.dumps(sample_json, indent=2))
        editor._save_to_file(file_path)
        
        # Создаем новый редактор и загружаем
        editor2 = JsonEditor()
        with open(file_path, 'r') as f:
            content = f.read()
        editor2.text_edit.setPlainText(content)
        
        # Проверяем
        loaded_data = json.loads(editor2.text_edit.toPlainText())
        assert loaded_data == sample_json
        editor2.close()


class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_very_large_json(self, editor):
        """Тест с большим JSON"""
        large_data = {"items": [{"id": i, "value": f"item_{i}"} for i in range(1000)]}
        editor.text_edit.setPlainText(json.dumps(large_data))
        editor.auto_validate()
        assert "✅" in editor.validation_label.text()
    
    def test_unicode_characters(self, editor):
        """Тест с Unicode символами"""
        unicode_data = {
            "russian": "Привет мир",
            "emoji": "🚀💻🎉",
            "chinese": "你好世界"
        }
        editor.text_edit.setPlainText(json.dumps(unicode_data, ensure_ascii=False))
        editor.auto_validate()
        assert "✅" in editor.validation_label.text()
    
    def test_deeply_nested_json(self, editor):
        """Тест с глубоко вложенным JSON"""
        nested = {"level": 1}
        current = nested
        for i in range(2, 10):
            current["nested"] = {"level": i}
            current = current["nested"]
        
        editor.text_edit.setPlainText(json.dumps(nested))
        editor.auto_validate()
        assert "✅" in editor.validation_label.text()


# Запуск тестов
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])