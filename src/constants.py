BIKE_CATEGORIES = {"moto", "moped", "quad"}

PRODUCT_CATEGORIES = {
    "helmets": "Мотошоломи",
    "gloves": "Рукавиці",
    "gear": "Екіпіровка",
    "parts_new": "Запчастини нові",
    "parts_used": "Запчастини б/у",
}

GEAR_CATEGORIES = {"helmets", "gloves", "gear"}
PARTS_CATEGORIES = {"parts_new", "parts_used"}

ALL_CATEGORIES = BIKE_CATEGORIES | set(PRODUCT_CATEGORIES)

BIKE_CONDITIONS = ["Нові", "Б/У"]
PRODUCT_CONDITIONS = ["Нове", "Відмінний", "Дуже добрий", "Добрий", "Задовільний"]

CATALOG_LABELS = {
    "moto": "Мотоцикли",
    "moped": "Мопеди",
    "quad": "Квадроцикли",
    **PRODUCT_CATEGORIES,
}

PARTS_SUBCATS = [
    {"key": "oils", "label": "Масла і Змазки"},
    {"key": "maintenance", "label": "Для ТО"},
    {"key": "intake", "label": "Впускна система"},
    {"key": "suspension", "label": "Підвіска"},
    {"key": "brakes", "label": "Гальмівна система"},
    {"key": "electronics", "label": "Електроніка"},
    {"key": "engine", "label": "Двигун та трансмісія"},
    {"key": "controls", "label": "Органи управління"},
]

OPENAPI_TAGS = [
    {"name": "Сайт — сторінки", "description": "Головна сторінка, бренди, контакти."},
    {
        "name": "Сайт — мотоцикли",
        "description": "Каталог мотоциклів, деталі оголошення.",
    },
    {
        "name": "Сайт — товари",
        "description": "Екіпіровка (шоломи, рукавиці, одяг) та запчастини.",
    },
    {"name": "Сайт — пошук", "description": "Повнотекстовий пошук по каталогу."},
    {
        "name": "Відгуки",
        "description": "Перегляд, додавання відгуків та відповіді на них.",
    },
    {"name": "Авторизація", "description": "Вхід та вихід з адмін-панелі."},
    {
        "name": "Адмін — мотоцикли",
        "description": "Додавання, редагування та видалення оголошень мотоциклів.",
    },
    {
        "name": "Адмін — товари",
        "description": "Управління екіпіровкою та запчастинами.",
    },
    {
        "name": "Адмін — відгуки",
        "description": "Модерація відгуків і відповіді від імені салону.",
    },
    {"name": "Адмін — бренди", "description": "Додавання та видалення брендів."},
    {
        "name": "Адмін — слайди",
        "description": "Управління слайдами на головній сторінці.",
    },
]

FALLBACK_SLIDES = [
    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80",
    "https://images.unsplash.com/photo-1449426468159-d96dbf08f19f?w=1400&q=80",
    "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=1400&q=80",
    "https://images.unsplash.com/photo-1609630875171-b1321377ee65?w=1400&q=80",
    "https://images.unsplash.com/photo-1591637333184-19aa84b3e01f?w=1400&q=80",
]
