# Практическая работа №2: граф зависимостей NuGet

Вариант 31, дисциплина «Конфигурационное управление».
Python 3.11+, только стандартная библиотека для получения зависимостей.

## Этап 1: конфигурация

```sh
./run.sh --package Serilog --version 4.0.0 --stage 1
./scripts/check_stage1.sh
python3 -m unittest discover -s tests -v
```

Прототип принимает `--package`, `--version`, `--repository`,
`--test-repo`, `--output`, `--max-depth`, `--exclude` и `--stage`.
По умолчанию используется NuGet V3 index; `--output` задаёт PNG-файл,
`--max-depth` задаёт глубину 0–100, `--exclude` задаёт подстроку фильтра.
Режим `--test-repo` требует локальный JSON и имя пакета от A до Z.
Программа выводит настройки в формате `ключ=значение`.
Ошибки параметров дают код завершения 2, ошибки выполнения дают код 1.

## Структура проекта

- `src/config.py`: функции `package_id`, `package_version`, `depth`,
  `nonempty`, `image_path`, `create_parser`, `validate_source`,
  `parse_arguments`;
- `src/main.py`: функция `main` и точка запуска приложения;
- `tests/`: модульные тесты;
- `scripts/check_stage1.sh`: локальная демонстрация этапа;
- `run.sh`: запуск программы.

Сборка не нужна: Python исполняет исходный код непосредственно.
Сгенерированные изображения, PDF, служебные файлы и настройки IDE
исключены из Git с помощью `.gitignore`.
