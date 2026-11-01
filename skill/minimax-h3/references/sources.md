# Происхождение и границы адаптации

## Источник 1 — MiniMax-AI/MiniMax-H3, каталог skills

Проверенная ревизия: `199b7d0e1fd95e7b3eafa8c15eca692534142427`. Все девять SKILL.md прочитаны.

| Upstream | Использование в адаптере |
|---|---|
| `h3-prompt-writing` (+ `base-en.txt`, `ref-en.txt`) | Режимы, точные строки привязки кадров, секции, камера, реплики, звук, Ref2VA → `prompt-guide.md` |
| `minimalist-product-ad-generator` | Рецепт в `style-recipes.md`; Hub-вызовы не переносятся |
| `3d-animation-short-generator` (+ `shot-table-spec.md`) | Рецепт и таблица планов → `style-recipes.md`, `continuity.md` |
| `papercraft-stop-motion-explainer` | Рецепт в `style-recipes.md` |
| `brand-promo-video-generator` | Рецепт в `style-recipes.md` |
| `music-video-subtitle-generator` | Рецепт в `style-recipes.md` |
| `co-op-game-intro-generator` | Рецепт в `style-recipes.md` |
| `paper-collage-explainer-generator` | Рецепт в `style-recipes.md` |
| `handdrawn-live-video-generator` | Рецепт в `style-recipes.md` |

Ссылки: `https://raw.githubusercontent.com/MiniMax-AI/MiniMax-H3/199b7d0e1fd95e7b3eafa8c15eca692534142427/skills/<имя>/SKILL.md`; гайды — `.../skills/h3-prompt-writing/references/base-en.txt` и `ref-en.txt`.

## Источник 2 — встроенная справка FreeVideo

`GET /freevideo/agent/v1/guide`, `/schema`, `/capabilities` (FreeVideo 0.4.x). Отсюда: уровни качества и `sampling`, LoRA, сетка кадров 17n+5, части и продолжение (`continue_from`, `part_prompts`, `first_frame_reference`), формы `media.first`, субтитры и музыка в многоплановом фильме, правило «новый план по умолчанию», оценка времени. Справка сама ссылается на `h3-prompt-writing` как на основу формата промптов.

## Источник 3 — практика

`practice.md`: обезличенные итоги реальных генераций на локальном движке (наблюдения, не гарантии).

## Что является локальной адаптацией

HTTP-клиент, контроль разрешений, работа с заданиями и скачиванием, ограничения секретов и проверки — адаптация к FreeVideo, а не свойства MiniMax Hub. Полные upstream-файлы в пакет не вложены: использованы краткие пересказы, имена форматов, точные служебные строки формата и оригинальные примеры. Лицензию модели и права на входные материалы этот пакет не заменяет.
