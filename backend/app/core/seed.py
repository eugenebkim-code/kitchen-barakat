from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.all_models import Category, MenuItem

INITIAL_DATA = [
    {
        "category": "1. Первые блюда",
        "items": [
            {
                "name": "Кукси",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAPnaXJd8E7OnLmPWO9IKuoqiZft2cIAAo4MaxtcSZlXYNiSnntti2MBAAMCAAN5AAM4BA",
                "description": "Холодная лапша по-корейски с насыщенным бульоном, свежими овощами и ароматными приправами. Легкое, освежающее блюдо, идеально подходит в любое время года."
            },
            {
                "name": "Шурпа",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAPzaXJeBdZkzWMMIYfAhRqo1NxeQzoAAo8MaxtcSZlXm2ux6GxTIS0BAAMCAAN5AAM4BA",
                "description": "Наваристый мясной суп с крупными кусками мяса и овощей. Ароматный бульон, насыщенный вкус и сытность по-домашнему."
            },
            {
                "name": "Солянка",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAP_aXJeGC8yWnIo4ZYWZ5QoeHctC4AAApAMaxtcSZlXbWf3Gpd6f4MBAAMCAAN5AAM4BA",
                "description": "Густой, насыщенный суп с ярким вкусом. Несколько видов мяса, солёные нотки, специи и лёгкая кислинка. Сытно и очень ароматно."
            },
            {
                "name": "Суйру лагман",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Сочный лагман с тянущейся лапшой и густым подливом из мяса и овощей. Насыщенный вкус, аромат специй и по-настоящему сытное блюдо."
            }
        ]
    },
    {
        "category": "2. Вторые блюда",
        "items": [
            {
                "name": "Плов",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Классический узбекский плов с рассыпчатым рисом, сочным мясом и ароматными специями. Готовится по традиционному рецепту, с насыщенным вкусом и аппетитным ароматом."
            },
            {
                "name": "Казан Кабоб",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Обжаренное в казане сочное мясо с картофелем и специями. Хрустящая корочка, насыщенный аромат и вкус настоящей узбекской классики."
            },
            {
                "name": "Манты",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Большие сочные манты с нежной начинкой из мяса и лука. Готовятся на пару, сохраняют насыщенный вкус и остаются особенно мягкими и ароматными."
            },
            {
                "name": "Цыплята табака",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBDWlyXkGvyaKKuVn3D5zylGglhCJuAAKRDGsbXEmZV--CzXWL6S8jAQADAgADeQADOAQ",
                "description": "Целый цыплёнок обжаренный до хрустящей корочки. Нежное мясо, аромат чеснока и специй, подаётся горячим и очень сочным."
            },
            {
                "name": "Жареный лагман",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBGmlyXlabV5DZJJG4pft4u0210KwqAAKSDGsbXEmZVzIJqRDnCgeEAQADAgADeQADOAQ",
                "description": "Обжаренная лапша с сочным мясом и овощами на сильном огне. Яркий вкус, аромат специй и сытно по-настоящему."
            }
        ]
    },
    {
        "category": "3. Салаты",
        "items": [
            {
                "name": "Морков-ча",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBJ2lyXnbWCSAb7q82TX7DyAABu1O84gACkwxrG1xJmVdNgED2raYOEwEAAwIAA3kAAzgE",
                "description": "Пикантная закуска из сочной моркови с чесноком, специями и ароматным маслом. Лёгкая острота и яркий вкус."
            },
            {
                "name": "Винегрет",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBNGlyXpaDJPPO0LYcnrWazmcIfDamAAKUDGsbXEmZV7zKeq4mopF5AQADAgADeQADOAQ",
                "description": "Классический овощной салат из свёклы, картофеля и солёных овощей. Лёгкий, освежающий и по-домашнему вкусный."
            },
            {
                "name": "Ачичук",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Свежий узбекский салат из спелых помидоров и лука с острым перцем. Лёгкий, сочный и идеально дополняет горячие блюда."
            },
            {
                "name": "Помидоры квашеные",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Домашние квашеные помидоры с насыщенным вкусом и лёгкой кислинкой. Отличная закуска к горячим блюдам."
            },
            {
                "name": "Оливье",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAICMWlycEL2LFYJ7Vk7x7UNJRTgwXGiAALmDGsbXEmZV3EBah2iQc7RAQADAgADeQADOAQ",
                "description": "Классический салат с отварным картофелем, яйцом, огурцом, зелёным горошком и нежным мясом. Заправлен мягким майонезом. Домашний, сытный, знакомый с детства. 🥗"
            }
        ]
    },
    {
        "category": "4. Хлеб, выпечка",
        "items": [
            {
                "name": "Лепешка",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBf2lyYUPBi7AqF--JZ6tPPJfh524IAAKcDGsbXEmZV0Z0FQSvmHkhAQADAgADeQADOAQ",
                "description": "Свежая узбекская лепёшка с хрустящей корочкой и мягкой серединкой. Идеально к любому блюду."
            }
        ]
    },
    {
        "category": "5. Закуски",
        "items": [
            {
                "name": "Бастурма",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Идеальная закуска к любому блюду"
            }
        ]
    }
]


async def seed_db():
    async with AsyncSessionLocal() as session:
        # Check if categories already exist
        res = await session.execute(select(Category))
        existing_cats = res.scalars().all()
        
        if existing_cats:
            print("Database already contains data, skipping seed.")
            return

        print("Seeding initial menu items...")
        sort_order = 1
        for cat_data in INITIAL_DATA:
            category = Category(name=cat_data["category"], sort_order=sort_order)
            session.add(category)
            await session.commit()
            await session.refresh(category)
            
            for item in cat_data["items"]:
                menu_item = MenuItem(
                    category_id=category.id,
                    name=item["name"],
                    description=item["description"],
                    price=item["price"],
                    image_url=item["image_url"],
                    is_available=item["is_available"]
                )
                session.add(menu_item)
            
            await session.commit()
            sort_order += 1
            
        print("Menu items seeded successfully!")
