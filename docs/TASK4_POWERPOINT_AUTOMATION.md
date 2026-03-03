# Задание 4 (автомобиль + светофор) — автоматизация через Python

Скрипт `scripts/build_traffic_presentation.py` автоматически собирает презентацию по методичке:

- 1 слайд (пустой)
- дуговая трасса
- автомобиль (простая векторная фигура)
- светофор из фигур
- 9 эффектов анимации (движение, повороты, смена цветов)

## Требования

- Windows
- Microsoft PowerPoint
- Python 3.10+
- пакет `pywin32`

## Установка

```bash
pip install pywin32
```

## Запуск

```bash
python scripts/build_traffic_presentation.py --output task4_traffic.pptx
```

После запуска будет создан файл `task4_traffic.pptx`.

## Примечание

Анимации заданы через COM API PowerPoint (win32). На Linux/macOS без PowerPoint скрипт не запускается.

Скрипт содержит fallback для эффекта смены цвета (разные сборки Office по-разному обрабатывают `ColorEffect`).

## Проверка готового файла (`.pptx` или `.zip`)

Если файл загружен на сайт как `task4_traffic.zip`, можно проверить его локально:

```bash
python scripts/validate_task4_submission.py task4_traffic.zip
```

Для обычного `.pptx`:

```bash
python scripts/validate_task4_submission.py task4_traffic.pptx
```
