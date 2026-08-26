from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.all_models import Category, MenuItem

INITIAL_DATA = [
    {
        "category": "1. Первые блюда",
        "category_ko": "1. 국물 요리",
        "items": [
            {
                "name": "Кукси",
                "name_ko": "쿡시",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAPnaXJd8E7OnLmPWO9IKuoqiZft2cIAAo4MaxtcSZlXYNiSnntti2MBAAMCAAN5AAM4BA",
                "description": "Холодная лапша по-корейски с насыщенным бульоном, свежими овощами и ароматными приправами. Легкое, освежающее блюдо, идеально подходит в любое время года.",
                "description_ko": "진한 육수와 신선한 채소, 향긋한 양념이 어우러진 고려식 냉면. 가볍고 상쾌해서 사계절 언제 먹어도 좋은 요리입니다."
            },
            {
                "name": "Шурпа",
                "name_ko": "슈르파",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAPzaXJeBdZkzWMMIYfAhRqo1NxeQzoAAo8MaxtcSZlXm2ux6GxTIS0BAAMCAAN5AAM4BA",
                "description": "Наваристый мясной суп с крупными кусками мяса и овощей. Ароматный бульон, насыщенный вкус и сытность по-домашнему.",
                "description_ko": "큼직한 고기와 채소가 듬뿍 들어간 진한 고기 수프. 향긋한 육수와 깊은 맛, 집에서 먹는 듯한 든든함이 느껴집니다."
            },
            {
                "name": "Солянка",
                "name_ko": "솔랸카",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAP_aXJeGC8yWnIo4ZYWZ5QoeHctC4AAApAMaxtcSZlXbWf3Gpd6f4MBAAMCAAN5AAM4BA",
                "description": "Густой, насыщенный суп с ярким вкусом. Несколько видов мяса, солёные нотки, специи и лёгкая кислинка. Сытно и очень ароматно.",
                "description_ko": "진하고 풍미 가득한 수프. 여러 종류의 고기와 짭짤한 감칠맛, 향신료, 은은한 새콤함이 어우러져 든든하고 향기롭습니다."
            },
            {
                "name": "Суйру лагман",
                "name_ko": "수이루 라그만",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Сочный лагман с тянущейся лапшой и густым подливом из мяса и овощей. Насыщенный вкус, аромат специй и по-настоящему сытное блюдо.",
                "description_ko": "쫄깃하게 늘어나는 면발과 고기, 채소로 만든 걸쭉한 소스가 어우러진 촉촉한 라그만. 진한 맛과 향신료 향이 가득한 든든한 한 그릇입니다."
            }
        ]
    },
    {
        "category": "2. Вторые блюда",
        "category_ko": "2. 메인 요리",
        "items": [
            {
                "name": "Плов",
                "name_ko": "플로프",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Классический узбекский плов с рассыпчатым рисом, сочным мясом и ароматными специями. Готовится по традиционному рецепту, с насыщенным вкусом и аппетитным ароматом.",
                "description_ko": "고슬고슬한 밥과 육즙 가득한 고기, 향긋한 향신료가 어우러진 정통 우즈벡식 플로프. 전통 레시피로 조리하여 깊은 맛과 식욕을 돋우는 향이 특징입니다."
            },
            {
                "name": "Казан Кабоб",
                "name_ko": "카잔 카봅",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Обжаренное в казане сочное мясо с картофелем и специями. Хрустящая корочка, насыщенный аромат и вкус настоящей узбекской классики.",
                "description_ko": "가마솥(카잔)에 구운 육즙 가득한 고기와 감자, 향신료 요리. 바삭한 겉면과 진한 향, 정통 우즈벡 클래식의 맛을 그대로 담았습니다."
            },
            {
                "name": "Манты",
                "name_ko": "만티",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Большие сочные манты с нежной начинкой из мяса и лука. Готовятся на пару, сохраняют насыщенный вкус и остаются особенно мягкими и ароматными.",
                "description_ko": "부드러운 고기와 양파 소를 가득 채운 큼직하고 촉촉한 만티. 찜으로 조리해 진한 맛을 살리고 특히 부드럽고 향긋합니다."
            },
            {
                "name": "Цыплята табака",
                "name_ko": "타바카 치킨",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBDWlyXkGvyaKKuVn3D5zylGglhCJuAAKRDGsbXEmZV--CzXWL6S8jAQADAgADeQADOAQ",
                "description": "Целый цыплёнок обжаренный до хрустящей корочки. Нежное мясо, аромат чеснока и специй, подаётся горячим и очень сочным.",
                "description_ko": "바삭하게 튀긴 통닭 요리. 부드러운 육질과 마늘, 향신료의 향이 어우러지며 뜨겁고 육즙 가득한 상태로 제공됩니다."
            },
            {
                "name": "Жареный лагман",
                "name_ko": "볶음 라그만",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBGmlyXlabV5DZJJG4pft4u0210KwqAAKSDGsbXEmZVzIJqRDnCgeEAQADAgADeQADOAQ",
                "description": "Обжаренная лапша с сочным мясом и овощами на сильном огне. Яркий вкус, аромат специй и сытно по-настоящему.",
                "description_ko": "센 불에 볶아낸 면과 육즙 가득한 고기, 채소 요리. 풍부한 맛과 향신료 향이 가득해 든든한 한 끼입니다."
            }
        ]
    },
    {
        "category": "3. Салаты",
        "category_ko": "3. 샐러드",
        "items": [
            {
                "name": "Морков-ча",
                "name_ko": "당근채",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBJ2lyXnbWCSAb7q82TX7DyAABu1O84gACkwxrG1xJmVdNgED2raYOEwEAAwIAA3kAAzgE",
                "description": "Пикантная закуска из сочной моркови с чесноком, специями и ароматным маслом. Лёгкая острота и яркий вкус.",
                "description_ko": "아삭한 당근에 마늘, 향신료, 향긋한 기름을 더한 매콤한 밑반찬. 살짝 매콤하면서도 풍미가 살아있습니다."
            },
            {
                "name": "Винегрет",
                "name_ko": "비네그레트",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBNGlyXpaDJPPO0LYcnrWazmcIfDamAAKUDGsbXEmZV7zKeq4mopF5AQADAgADeQADOAQ",
                "description": "Классический овощной салат из свёклы, картофеля и солёных овощей. Лёгкий, освежающий и по-домашнему вкусный.",
                "description_ko": "비트, 감자, 절인 채소로 만든 정통 채소 샐러드. 가볍고 상쾌하며 집밥처럼 편안한 맛입니다."
            },
            {
                "name": "Ачичук",
                "name_ko": "아치축",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Свежий узбекский салат из спелых помидоров и лука с острым перцем. Лёгкий, сочный и идеально дополняет горячие блюда.",
                "description_ko": "잘 익은 토마토와 양파, 매운 고추로 만든 신선한 우즈벡식 샐러드. 가볍고 촉촉해 따뜻한 요리와 잘 어울립니다."
            },
            {
                "name": "Помидоры квашеные",
                "name_ko": "절임 토마토",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Домашние квашеные помидоры с насыщенным вкусом и лёгкой кислинкой. Отличная закуска к горячим блюдам.",
                "description_ko": "깊은 맛과 은은한 새콤함이 있는 홈메이드 절임 토마토. 따뜻한 요리와 곁들이기 좋은 밑반찬입니다."
            },
            {
                "name": "Оливье",
                "name_ko": "올리비에 샐러드",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAICMWlycEL2LFYJ7Vk7x7UNJRTgwXGiAALmDGsbXEmZV3EBah2iQc7RAQADAgADeQADOAQ",
                "description": "Классический салат с отварным картофелем, яйцом, огурцом, зелёным горошком и нежным мясом. Заправлен мягким майонезом. Домашний, сытный, знакомый с детства. 🥗",
                "description_ko": "삶은 감자, 달걀, 오이, 완두콩, 부드러운 고기가 들어간 정통 샐러드. 부드러운 마요네즈로 버무려 어릴 적 추억이 떠오르는 든든한 집밥 샐러드입니다. 🥗"
            }
        ]
    },
    {
        "category": "4. Хлеб, выпечка",
        "category_ko": "4. 빵 및 제과류",
        "items": [
            {
                "name": "Лепешка",
                "name_ko": "레표시카",
                "price": 10000,
                "is_available": True,
                "image_url": "https://api.telegram.org/file/bot/AgACAgUAAxkBAAIBf2lyYUPBi7AqF--JZ6tPPJfh524IAAKcDGsbXEmZV0Z0FQSvmHkhAQADAgADeQADOAQ",
                "description": "Свежая узбекская лепёшка с хрустящей корочкой и мягкой серединкой. Идеально к любому блюду.",
                "description_ko": "겉은 바삭하고 속은 부드러운 신선한 우즈벡식 빵. 어떤 요리와도 잘 어울립니다."
            }
        ]
    },
    {
        "category": "5. Закуски",
        "category_ko": "5. 에피타이저",
        "items": [
            {
                "name": "Бастурма",
                "name_ko": "바스투르마",
                "price": 10000,
                "is_available": True,
                "image_url": None,
                "description": "Идеальная закуска к любому блюду",
                "description_ko": "어떤 요리와도 잘 어울리는 훌륭한 안주"
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
            category = Category(name=cat_data["category"], name_ko=cat_data.get("category_ko"), sort_order=sort_order)
            session.add(category)
            await session.commit()
            await session.refresh(category)

            for item in cat_data["items"]:
                menu_item = MenuItem(
                    category_id=category.id,
                    name=item["name"],
                    name_ko=item.get("name_ko"),
                    description=item["description"],
                    description_ko=item.get("description_ko"),
                    price=item["price"],
                    image_url=item["image_url"],
                    is_available=item["is_available"]
                )
                session.add(menu_item)

            await session.commit()
            sort_order += 1

        print("Menu items seeded successfully!")
