# Задание 4 (автомобиль + светофор) — автоматизация через Python

Скрипт `scripts/build_traffic_presentation.py` собирает презентацию по методичке:

- 1 слайд (пустой)
- вертикальная дуговая трасса (ориентация как на рис. 3.11)
- автомобиль (векторные фигуры)
- светофор из фигур
- 9 эффектов анимации (пути перемещения, повороты, смена цветов)

## Требования

- Python 3.10+
- пакет `python-pptx`

## Установка

```bash
pip install python-pptx
```

## Запуск

```bash
python scripts/build_traffic_presentation.py --output task4_traffic.pptx
```

По умолчанию скрипт использует `task4_traffic.pptx` как источник шаблона таймингов
(берётся только XML-блок `<p:timing>`, затем подставляются ID созданных фигур и новые
вертикальные траектории движения).

При необходимости можно явно указать шаблон:

```bash
python scripts/build_traffic_presentation.py --output task4_traffic.pptx --timing-template task4_traffic.pptx
```

## Проверка готового файла (`.pptx` или `.zip`)

Если файл загружен на сайт как `task4_traffic.zip`, можно проверить его локально:

```bash
python scripts/validate_task4_submission.py task4_traffic.zip
```

Для обычного `.pptx`:

```bash
python scripts/validate_task4_submission.py task4_traffic.pptx
```
