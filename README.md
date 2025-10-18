<div align="center">

# 🧾 JSON Editor Pro

Редактор JSON с деревом, подсветкой и проверкой данных.

![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41CD52.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

---

## ✨ Возможности

### 🎨 Интерфейс
-  Подсветка синтаксиса JSON  
-  Древовидная визуализация данных  
-  Адаптивный интерфейс с настраиваемыми панелями  

### 🔧 Функциональность
-  **Валидация** и проверка корректности JSON  
-  **Форматирование / минификация**  
-  **Поиск и замена** с поддержкой регулярных выражений  
-  Экспорт в другие форматы: **XML**, **YAML**  
-  Автосохранение настроек (цвета, шрифты, размеры окон)  
-  История последних открытых файлов

### ⌨️ Удобство использования
-  Горячие клавиши для всех действий  
-  Удобное меню и панель инструментов  
-  Поддержка Unicode и эмодзи

---

## 🛠️ Технологический стек

| Компонент        | Технология                  |
|-------------------|------------------------------|
| **Frontend**      | PyQt5, Python 3.12+          |
| **Backend**       | JSON, pathlib, typing        |
| **Архитектура**   | Модульная (MVC)             |

---

## 📦 Установка и запуск

Вариант А. Быстрый запуск из исходников (Windows)

1) Установите Python 3.12 с сайта python.org. На шаге установки включите «Add Python to PATH».

2) Скачайте проект и распакуйте в папку, например `C:\JSONEditor`.

3) Откройте PowerShell в папке проекта и выполните по очереди:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.bat
pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Вариант Б. Сборка «портативного» .exe выполните по очереди:
Активация окружения
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.bat
pip install --upgrade pip
pip install -r requirements.txt
```
Конвертация кода в .exe
```powershell
pip install pyinstaller
pyinstaller --name "JSON Editor Pro" --noconsole --onefile `
  --collect-all PyQt5 `
  --add-data "ui\mainwindow.ui;ui" `
  --add-data "icons;icons" `
  main.py

```

Файл появится: `dist/JSON Editor Pro.exe` — запускайте двойным кликом.

Если EXE не стартует, попробуйте без `--onefile` (получится папка со всеми файлами):
```powershell
pyinstaller --name "JSON Editor Pro" --noconsole --collect-all PyQt5 `
  --add-data "ui\\mainwindow.ui;ui" --add-data "icons;icons" main.py
```

---

---

## 🚀 Использование

### 📂 Основные операции

| Действие                  | Горячая клавиша      | Меню / Кнопка                  |
|----------------------------|-----------------------|-------------------------------|
| Открыть файл               | `Ctrl+O`             | 📂 *Файл → Открыть*            |
| Сохранить                  | `Ctrl+S`             | 💾 *Сохранить*                |
| Поиск                      | `Ctrl+F`             | 🔍 *Поиск*                    |
| Замена                     | `Ctrl+H`             | ✏️ *Замена*                   |
| Форматирование             | —                    | ✨ *Форматировать JSON*       |
| Проверка корректности     | —                    | ✔️ *Проверить JSON*          |

---

### ⚙️ Настройки

-  **Шрифт** — выбор семейства и размера  
-  **Цвета** — настройка текста и фона  
-  Автосохранение параметров через `QSettings`

---

## 🌍 Экспорт данных

1. Откройте меню **«Инструменты» → «Экспорт»**  
2. Выберите нужный формат: **XML** или **YAML**  
3. Предпросмотр результата  
4. Укажите путь и сохраните 📝

---

## 🧱 Структура проекта

```
project_root/
├── main.py
├── requirements.txt
├── README.md
├── icons/
│   └── appp.png
├── ui/
│   └── mainwindow.ui
├── widgets/
│   ├── __init__.py
│   ├── json_tree_widget.py
│   └── syntax_highlighter.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── dialogs/
│   ├── about_dialog.py
│   ├── export_dialog.py
│   └── search_dialog.py
└── test_json_editor.py
```

---

## 🧪 Тестирование
Выполните эту команду в папке проекта 
```powershell
pytest -q
```

`pytest.ini` включает цветной, подробный вывод, и топ-10 самых долгих тестов.

---

## 🧰 Горячие клавиши

| Команда                    | Комбинация            |
|----------------------------|-----------------------|
| Открыть файл               | `Ctrl+O`             |
| Сохранить                  | `Ctrl+S`             |
| Сохранить как              | `Ctrl+Shift+S`       |
| Поиск                      | `Ctrl+F`             |
| Замена                     | `Ctrl+H`             |
| Выход                      | `Ctrl+Q`             |

---

## 📜 Лицензия

Этот проект распространяется под лицензией **MIT**.  
Подробнее см. файл [`LICENSE`](LICENSE).

---

<div align="center">

✨ Приятной работы с JSON Editor Pro! ✨

</div>
