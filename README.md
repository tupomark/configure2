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

## Этап 2: получение прямых зависимостей

```sh
./run.sh --package Serilog --version 4.0.0 --stage 2
./scripts/check_stage2.sh
```

NuGet V3 Service Index предоставляет ресурс `PackageBaseAddress`.
`NugetRepository` читает список версий и `.nuspec` указанного пакета.
`parse_nuspec` выделяет прямые зависимости из XML; `--framework`
позволяет выбрать точную группу целевой платформы.
`version_key`, `normalize`, `parse_bounds`, `satisfies`, `select_version`
проверяют версии и выбирают совместимую версию согласно диапазону.
`fetch_bytes` выполняет ограниченные по времени и размеру HTTP-запросы.

Проверка этапа 2 использует локальный HTTP-сервер и настоящий CLI:
пакет A версии 1 зависит от B, A версии 2 зависит от C, а зависимости
пакета B не выводятся как прямые зависимости A.
