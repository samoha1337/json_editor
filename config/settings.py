"""
Модуль для управления настройками приложения с использованием QSettings
"""
from typing import Dict, Any, List
from PyQt5.QtCore import QSettings


class SettingsManager:
    """Менеджер настроек приложения с использованием QSettings"""
    
    def __init__(self):
        self.settings = QSettings("JSONEditorPro", "Settings")
        self.default_settings = {
            "font_family": "Consolas",
            "font_size": 12,
            "text_color": "#000000",
            "background_color": "#ffffff",
            "auto_validate": True,
            "validation_delay": 500,
            "window_geometry": {
                "width": 1400,
                "height": 800,
                "x": 100,
                "y": 100
            },
            "splitter_sizes": [700, 300],
            "recent_files": [],
            "max_recent_files": 10
        }
    
    def get(self, key: str, default=None):
        """Получает значение настройки"""
        if default is None:
            default = self.default_settings.get(key)
        
        # Специальная обработка для сложных типов
        if key == "window_geometry":
            return {
                "x": self.settings.value("window_geometry/x", self.default_settings["window_geometry"]["x"], int),
                "y": self.settings.value("window_geometry/y", self.default_settings["window_geometry"]["y"], int),
                "width": self.settings.value("window_geometry/width", self.default_settings["window_geometry"]["width"], int),
                "height": self.settings.value("window_geometry/height", self.default_settings["window_geometry"]["height"], int)
            }
        elif key == "splitter_sizes":
            sizes_str = self.settings.value("splitter_sizes", "")
            if sizes_str:
                try:
                    return [int(x) for x in sizes_str.split(",")]
                except ValueError:
                    return self.default_settings["splitter_sizes"]
            return self.default_settings["splitter_sizes"]
        elif key == "recent_files":
            files_str = self.settings.value("recent_files", "")
            if files_str:
                return files_str.split("|") if files_str else []
            return []
        elif key in ["auto_validate"]:
            return self.settings.value(key, default, bool)
        elif key in ["font_size", "validation_delay", "max_recent_files"]:
            return self.settings.value(key, default, int)
        else:
            return self.settings.value(key, default)
    
    def set(self, key: str, value: Any):
        """Устанавливает значение настройки"""
        # Специальная обработка для сложных типов
        if key == "window_geometry":
            if isinstance(value, dict):
                self.settings.setValue("window_geometry/x", value.get("x", 100))
                self.settings.setValue("window_geometry/y", value.get("y", 100))
                self.settings.setValue("window_geometry/width", value.get("width", 1400))
                self.settings.setValue("window_geometry/height", value.get("height", 800))
        elif key == "splitter_sizes":
            if isinstance(value, list):
                self.settings.setValue("splitter_sizes", ",".join(map(str, value)))
        elif key == "recent_files":
            if isinstance(value, list):
                self.settings.setValue("recent_files", "|".join(value))
        else:
            self.settings.setValue(key, value)
        
        # Синхронизируем настройки
        self.settings.sync()
    
    def add_recent_file(self, file_path: str):
        """Добавляет файл в список недавних"""
        recent_files = self.get_recent_files()
        if file_path in recent_files:
            recent_files.remove(file_path)
        recent_files.insert(0, file_path)
        
        max_files = self.get("max_recent_files", 10)
        recent_files = recent_files[:max_files]
        
        self.set("recent_files", recent_files)
    
    def get_recent_files(self) -> List[str]:
        """Получает список недавних файлов"""
        return self.get("recent_files", [])
    
    def clear_recent_files(self):
        """Очищает список недавних файлов"""
        self.set("recent_files", [])
    
    def reset_to_defaults(self):
        """Сбрасывает настройки к значениям по умолчанию"""
        self.settings.clear()
        self.settings.sync()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Получает все настройки"""
        result = {}
        for key in self.default_settings.keys():
            result[key] = self.get(key)
        return result


# Глобальный экземпляр менеджера настроек
settings_manager = SettingsManager()


