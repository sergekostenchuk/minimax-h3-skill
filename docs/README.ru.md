# MiniMax H3 Skill — видео на вашей видеокарте

[![test](https://github.com/sergekostenchuk/minimax-h3-skill/actions/workflows/test.yml/badge.svg)](https://github.com/sergekostenchuk/minimax-h3-skill/actions/workflows/test.yml)
[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-blue)](https://agentskills.io)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](../LICENSE)

[English](../README.md) · Русский

[Agent Skill](https://agentskills.io), который учит любого ИИ-агента снимать видео моделью **MiniMax H3** на локальном **FreeVideo**: писать промпты в официальном формате H3, выбирать режим, проверять и запускать задания, собирать длинные ролики и проверять результат — на вашей собственной видеокарте.

## Что умеет

- **Промпты в официальном формате H3** для пяти режимов: T2VA (текст), I2VA (первый кадр), FL2VA (первый и последний), L2VA (последний), Ref2VA (персонажи, места и голоса по референсам). Точные строки привязки кадров, тайминги `[Shot N] At MM:SS.mmm`, камера, звук и музыка.
- **Речь делает сама модель.** Реплики в `<d>[Russian] …</d>` / `<d>[English] …</d>` с постоянными ID говорящих; H3 озвучивает их с движением губ. Правила против непрошеных субтитров.
- **Длинные ролики — по задаче:** новый план из референсов (по умолчанию для фильма), последний кадр → первый кадр следующего клипа, `continue_from`, или одна задача до 60 с, которую FreeVideo сам режет и склеивает. Как держать ровную скорость на стыках.
- **Движок FreeVideo:** уровни качества (`light` = два прохода 8+3 … `max` = 20 шагов), `sampling`, LoRA, сетка кадров 24 fps / 17n+5, оценка времени конкретной машины из `/capabilities`, повтор без дублей через `ref`.
- **Безопасный помощник** `freevideo.py` (только стандартная библиотека Python): только локальный адрес, токен не печатает, слепых повторов нет, запись — только с `--apply`.
- **Практика** реальных локальных генераций и восемь стилевых рецептов из официальных скиллов MiniMax-H3.

## Что нужно

- FreeVideo (локальная студия MiniMax H3 на ComfyUI) с Agent API (`http://127.0.0.1:8188/freevideo/agent/v1`) и файлом токена. О локальном запуске H3: [руководство MiniMax](https://platform.minimax.io/docs/guides/local-deploy-h3.md). Для одних промптов ничего не нужно.
- Python 3.10+ для помощника. Любая видеокарта, которую поддерживает FreeVideo; время генерации берётся из `/capabilities` вашей машины.

## Установка

```bash
git clone https://github.com/sergekostenchuk/minimax-h3-skill
cd minimax-h3-skill
python install.py --target agents        # ~/.agents/skills — Codex, Gemini CLI, Qwen Code, Kimi, pi, OpenCode, Cursor, Roo, Goose, Copilot, Devin, Grok Build
python install.py --target claude-code   # ~/.claude/skills
python install.py --all                  # agents + claude-code + hermes + antigravity + cline
python install.py --list                 # все цели и их папки
```

`--dry-run` покажет, что будет записано. Можно и вручную скопировать `skill/minimax-h3` в папку скиллов своего агента.

## С какими агентами работает

Claude Code · OpenAI Codex · Gemini CLI · Google Antigravity · Qwen Code · Kimi Code · Hermes Agent · pi · OpenCode · Cursor · Cline · Roo Code · Goose · GitHub Copilot · Devin / Windsurf · Grok Build — с любой моделью внутри (Claude, GPT, Gemini, Qwen, Kimi, DeepSeek, GLM, Grok, локальные модели через Ollama).
Папки, источники и запасные варианты: [harnesses.md](harnesses.md).

## Как пользоваться

Попросите агента обычными словами:

> Сделай видео на 10 секунд: женщина на пляже на закате смотрит в небо и говорит «Многое изменится». Камера медленно поднимается. Без музыки и субтитров.

Агент напишет промпт H3, выполнит `POST /plan` (фактическая длина, предупреждения, оценка времени), запустит генерацию только по вашей просьбе, дождётся, скачает и проверит результат. Скажите «только промпт» — получите текст без запуска.

## Тесты

```bash
python -B skill/minimax-h3/scripts/test_freevideo.py   # помощник, без GPU
python -B tools/test_install.py                         # установщик во временной домашней папке
python tools/validate_skill.py                          # заголовок, файлы, JSON, отсутствие личных данных
```

CI гоняет их на Linux, Windows и macOS с Python 3.10, 3.12 и 3.13.

## Источники и лицензия

Правила промптов — адаптация официальных [скиллов MiniMax-H3](https://github.com/MiniMax-AI/MiniMax-H3/tree/main/skills) и встроенной справки FreeVideo `/guide`; исходники пересказаны, а не скопированы (`references/sources.md`). Репозиторий — Apache-2.0; права на модель MiniMax H3 и на ваши материалы он не даёт.
