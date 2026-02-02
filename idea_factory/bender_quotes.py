"""Bender-style motivational quotes in Ukrainian for different stages."""

import random

LANDING_QUOTES = [
    "Давайте вже нарешті щось придумаємо!",
    "Час генерувати ідеї, м'ясні мішки!",
    "О, це буде легенд... чекайте, легендарно!",
    "Готові до мозкового штурму? Я народився готовим!",
]

BRAINSTORM_QUOTES = [
    "Генерую ідеї... Це складніше, ніж здається!",
    "Зачекайте, я думаю... Це болить!",
    "Обробляю запит... Навіть я вражений!",
    "Ідеї йдуть... Приготуйтеся!",
]

IMPROVE_QUOTES = [
    "Покращуємо? Я і так ідеальний, але спробуємо!",
    "Зараз зробимо це ще крутіше!",
    "Додамо трохи магії... Або науки. Або обох!",
    "Редагуємо на льоту!",
]

SUBMIT_QUOTES = [
    "Останній крок до слави!",
    "Зберігаємо вашу геніальність!",
    "Це буде в історії!",
    "Фіналізуємо шедевр!",
]

THANKYOU_QUOTES = [
    "О, клас! Давайте це зробимо. Дякую вам.",
    "Чудова ідея! Навіть я вражений.",
    "Ви молодці! Я б обняв вас, але я робот.",
    "Ідеально! Тепер йдемо будувати!",
]


def get_random_quote(stage: str) -> str:
    """Get a random Bender quote for the given stage."""
    quotes_map = {
        'landing': LANDING_QUOTES,
        'brainstorm': BRAINSTORM_QUOTES,
        'improve': IMPROVE_QUOTES,
        'submit': SUBMIT_QUOTES,
        'thankyou': THANKYOU_QUOTES,
    }
    quotes = quotes_map.get(stage, LANDING_QUOTES)
    return random.choice(quotes)
