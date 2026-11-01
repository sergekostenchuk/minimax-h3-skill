# Промпты H3

Синтез официальных `h3-prompt-writing` (`base-en.txt`, `ref-en.txt`) и справки FreeVideo `/guide`; источники — `sources.md`. Примеры ниже оригинальные.

## 0. Общие правила

- Секции и описания — на английском. Реплики, слова песен и видимые надписи — дословно на языке оригинала.
- Каждая секция начинается с новой строки как `name: text`, секции разделены одной пустой строкой, порядок строгий.
- Описывай только то, что видно или слышно, в порядке просмотра. Одно ясное основное действие на план и направление его развития.
- Одинаковые слова для одного и того же персонажа/предмета во всех планах и частях (лицо, волосы, одежда, голос).

## 1. Базовые режимы: T2VA / I2VA / FL2VA / L2VA

Секции: `integrated_multimodal_description`, `overall_soundscape`, `non_diegetic_music`.

Для режимов с кадрами **первая строка промпта — инструкция привязки**, затем пустая строка, затем секции. Строки точные:

- I2VA: `For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.`
- FL2VA: `How the reference pictures align with the target video — Picture 1 (from Shot 1) aligns with the 0.00-second mark of the target video; Picture 2 (from Shot N) aligns with the S.SS-second mark of the target video.`
- L2VA: `How the reference pictures align with the target video — <Picture 1> (from [Shot N]) aligns with the S.SS-second mark of the target video.`

`N` — номер последнего плана, `S.SS` — фактическая длительность с двумя знаками (по сетке кадров: 10 с → 10.13, см. `freevideo-api.md`).

Структура описания:
- I2VA: якорь первого кадра (стиль, персонажи, компоновка как на <Picture 1>) → начало действия → развитие → результат. Не повторяй уже завершённое в кадре движение.
- FL2VA: состояние первого кадра → наблюдаемые промежуточные изменения → сближение → состояние последнего кадра. Предпочтительно один план.
- L2VA: правдоподобное предшествующее состояние → путь → постепенное схождение → посадка в финальный кадр. Картинка относится только к концу.

## 2. Планы, стиль, камера

- `[Shot 1]` без времени и сразу стиль + исходная композиция: `[Shot 1] Live-action, cinematic, a medium-wide shot frames ...` (стили: live-action, cinematic, 2D-animated, 3D CG, claymation, watercolor, vintage film; для кадровых режимов стиль берётся из картинки).
- Следующие планы: `[Shot 2] At 00:03.500, the camera cuts to ...`; времена строго растут и лежат внутри длительности. Склейка — только ради новой информации; малое изменение — движением камеры.
- Камера = тип + (амплитуда) + (скорость), прозой внутри действия: push in / pull out, zoom in / out, pan, truck, tilt, pedestal, arc shot, tracking shot, static shot, shake slightly/strongly, POV, roll; `with small/large amplitude`, `at slow/fast speed`. Пример: `The camera pushes in with small amplitude at slow speed toward the letter in her hands.`
- Не сочетай противоречия («static shot» и «orbits the hero»). Сложную хореографию дели на фазы. Поворот персонажа описывай явно и непрерывно (`turns around slowly to face the camera`), иначе модель может «перескочить» из анфаса в спину.

## 3. Реплики, речь, пение

- Говорящие получают постоянные ID `(S1)`, `(S2)` во всех планах; общий хор — `(S1,S2)`. Молчащим ID не давай.
- При первом появлении голоса опиши его (возраст, пол, тембр, темп, акцент) вне `<d>`; внутри `<d>` — только тег языка и дословные слова:
  `The woman with a calm low voice (S1) says: <d>[Russian] Многое изменится.</d>`
  `The two children (S1,S2) shout together, <d>[English] Wait for us!</d>`
- Закадровый голос: `says in an off-screen voiceover: <d>...</d> while his lips remain completely closed.`
- Фраза через склейку — `<scenetrans>` в обеих частях и `continues seamlessly across the cut`; оборванная концом ролика — `<cutoff>`.
- Модель сама синтезирует речь и пение по `<d>` (в том числе русский и английский), губы синхронизируются. Длина фраз должна помещаться в план: ~2–3 слова в секунду.

## 4. Видимый текст и субтитры

- Видимый текст — в двойных кавычках: `a neon sign reading "ОТКРЫТО"`. Реплики в кавычки НЕ ставь: всё в кавычках модель рисует на экране.
- H3 может сама добавить субтитры к речи. Если они не нужны, закончи описание фразой `No subtitles, no on-screen text.` (или `No subtitles or captions.`, если в кадре есть вывеска/экран). Это снижает, но не исключает риск: проверь кадры, при надписях — другой seed.
- Длинные надписи и мелкий текст модель часто рисует неразборчиво. Важные титры, подписи и цифры накладывай при монтаже, а не проси у модели.

## 5. Звук и музыка

- `overall_soundscape`: 1–4 предложения: эмбиент, звуки действий, дыхание. `N/A` — только для полной тишины. Реплики сюда не повторяй.
- `non_diegetic_music`: 1–3 предложения: инструменты, темп, динамика, без слов о настроении; иначе `N/A`. Музыка, которую слышат персонажи (радио, пение) — в описании.
- Фильм из нескольких планов/частей: в каждом плане `non_diegetic_music: N/A`; одна музыкальная дорожка накладывается после монтажа. Разная музыка в каждом плане скачет на склейках.

## 6. Ref2VA (полный референсный режим)

Шесть секций строго по порядку: `subject_definitions`, `summary`, `retention_analysis`, `detailed_description`, `overall_soundscape`, `non_diegetic_music`.

Метки (номер — по порядку внутри своего вида):
- `<Subject N>` — переиспользуемое содержимое: персонаж, животное, предмет, место, костюм, стиль, движение. Один субъект может опираться на несколько файлов.
- `<Picture N>` — картинка как конкретный кадр/ключевой кадр/раскадровка. Если картинка лишь задаёт персонажа — отдельной строки нет, она упоминается внутри `<Subject N>`.
- `<Video N>` — исходное видео для правки/продолжения/структуры. `<Audio N>` — копируемый или референсный звук (голос, музыка). Наличие звука в видео само по себе не создаёт `<Audio N>`.

`summary` начинается с типа задачи в квадратных скобках (через ` + `): `keyframe completion`, `reference generation`, `video editing`, `video continuation`, `audio reuse`, `audio reference`.
`retention_analysis`: визуальное — `fully_preserved`, `partially_preserved`, `attribute_transfer`, `weak_reference`; аудио — `fully_copy`, `partially_copy`, `reference`, `weak_reference`. Новая поза или действие — не потеря идентичности.
`detailed_description`: 1–2 предложения стиля ДО `[Shot 1]`, затем планы; обычно 350–500 английских слов; говорящий субъект — `<Subject 2> (S1) says, <d>[Russian] ...</d>`.

## 7. Шаблоны (оригинальные примеры)

### T2VA, 5 с, без музыки
```text
integrated_multimodal_description: [Shot 1] Live-action, cinematic, a medium shot frames a small blue service robot beside a tomato plant in a glass greenhouse. Soft morning light enters from frame left. The camera holds a static shot. The robot lifts a green watering can, pours a thin stream onto the soil, then returns the can to the bench while the leaves sway briefly. No subtitles, no on-screen text.

overall_soundscape: Quiet ventilation, a gentle water trickle, and a single light tap as the can touches the wooden bench.

non_diegetic_music: N/A
```

### I2VA с русской репликой, 10 с
```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] Live-action, cinematic, the woman shown in <Picture 1> stands on the beach at dusk, preserving her face, hair, white dress, position and the shoreline layout. The camera pulls out with small amplitude at slow speed as she lifts her gaze to a bright point in the sky. She turns her head toward the camera, and the woman with a calm, low voice (S1) says: <d>[Russian] Это сверхновая. Многое изменится.</d> Her lips close and she keeps looking up while the light grows brighter. No subtitles, no on-screen text.

overall_soundscape: Soft waves roll onto the sand under a light evening wind; fabric flutters faintly.

non_diegetic_music: N/A
```

### Ref2VA: один персонаж по трём ракурсам, 10 с
```text
subject_definitions:
<Subject 1> is the middle-aged man shown in <Picture 1> (front), <Picture 2> (three-quarter) and <Picture 3> (side), with a grey beard, round glasses and a dark-green knitted sweater.
<Subject 2> is a cluttered home study with shelves of folders and a desk lamp, described in the prompt.

summary:
[reference generation] <Subject 1> sits at a desk in <Subject 2> and explains a theory to the camera in Russian, in one continuous medium shot.

retention_analysis:
<Subject 1> (appears in [Shot 1]): fully_preserved - face, beard, glasses and sweater stay identical to the reference views.
<Subject 2> (appears in [Shot 1]): weak_reference - only the general look of a cluttered study is kept.

detailed_description:
The target video is a realistic documentary interview style with warm practical lighting.
[Shot 1] A medium shot frames <Subject 1> at a wooden desk in <Subject 2>, facing the camera, the desk lamp on the right. The camera pushes in with small amplitude at slow speed. <Subject 1> (S1), speaking in a hoarse, confident baritone at a brisk pace, taps a folder and says: <d>[Russian] Я вам точно говорю, всё было спланировано заранее.</d> He leans back and spreads his hands. No subtitles, no on-screen text.

overall_soundscape: Quiet room tone, a ticking wall clock and the dry tap of a finger on cardboard.

non_diegetic_music: N/A
```

### Продолжение с последнего кадра (I2VA), середина длинного прохода
```text
For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced.

integrated_multimodal_description: [Shot 1] 3D CG, cinematic, the shot begins exactly where <Picture 1> ends: the camera is already rising above the coastline at the same steady speed. It keeps pedestaling up without slowing as the town lights shrink and the curve of the planet appears; clouds pass under the lens. The motion continues at the same speed through the final frame, with no slowing or settling. No subtitles, no on-screen text.

overall_soundscape: A steady high wind fades into a soft airy hush as the altitude grows.

non_diegetic_music: N/A
```
