from django.db import migrations
def seed_shop(apps, schema_editor):
    ProductCategory = apps.get_model("base", "ProductCategory")
    Product = apps.get_model("base", "Product")

    categories_payload = [
        {
            "slug": "kotly-i-otoplenie",
            "name": "Котлы и отопление",
            "description": "Котлы, радиаторы, тёплый пол и комплектующие для отопления.",
            "products": [
                ("gazovye-kotly", "Газовые котлы", "Настенные и напольные газовые котлы."),
                ("tverdotoplivnye-kotly", "Твердотопливные котлы", "Решения для частных домов и котельных."),
                ("radiatory-otopleniya", "Радиаторы отопления", "Стальные и биметаллические радиаторы."),
            ],
        },
        {
            "slug": "vodosnabzhenie-i-kanalizaciya",
            "name": "Водоснабжение и канализация",
            "description": "Трубы, фитинги, насосы и сантехнические решения.",
            "products": [
                ("truby-i-fitingi", "Трубы и фитинги", "Полипропилен, металлопласт и комплектующие."),
                ("nasosnye-stancii", "Насосные станции", "Насосы и автоматика для воды."),
                ("kanalizacionnye-sistemy", "Канализационные системы", "Трубы, ревизии и аксессуары."),
            ],
        },
        {
            "slug": "santehnika-i-servis",
            "name": "Сантехника и сервис",
            "description": "Смесители, сантехника и услуги монтажа.",
            "products": [
                ("smesiteli", "Смесители", "Для кухни, ванной и душевых."),
                ("dushevye-i-vanny", "Душевые и ванны", "Кабины, ванны, унитазы и аксессуары."),
                ("servisnoe-obsluzhivanie", "Сервисное обслуживание", "Промывка и обслуживание отопительных систем."),
            ],
        },
    ]

    for category_item in categories_payload:
        category, _ = ProductCategory.objects.update_or_create(
            slug=category_item["slug"],
            defaults={
                "name": category_item["name"],
                "description": category_item["description"],
                "is_active": True,
            },
        )
        for product_slug, product_name, product_desc in category_item["products"]:
            Product.objects.update_or_create(
                slug=product_slug,
                defaults={
                    "category": category,
                    "name": product_name,
                    "description": product_desc,
                    "is_active": True,
                },
            )


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0003_emailauthcode_productcategory_orderrequest_article_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_shop, migrations.RunPython.noop),
    ]
