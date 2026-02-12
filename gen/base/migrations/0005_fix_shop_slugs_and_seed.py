from django.db import migrations


def fix_shop_seed(apps, schema_editor):
    ProductCategory = apps.get_model("base", "ProductCategory")
    Product = apps.get_model("base", "Product")

    # Clean up broken slugs from previous seed attempt.
    ProductCategory.objects.filter(slug="").delete()
    Product.objects.filter(slug="").delete()

    payload = [
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

    for item in payload:
        category, _ = ProductCategory.objects.update_or_create(
            slug=item["slug"],
            defaults={
                "name": item["name"],
                "description": item["description"],
                "is_active": True,
            },
        )
        for product_slug, product_name, product_desc in item["products"]:
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
        ("base", "0004_seed_shop_data"),
    ]

    operations = [
        migrations.RunPython(fix_shop_seed, migrations.RunPython.noop),
    ]
