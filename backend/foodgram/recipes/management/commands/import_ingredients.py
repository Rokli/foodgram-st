from django.core.management.base import BaseCommand
from recipes.models import IngredientModel
import json


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из файла ingredients.json'

    def handle(self, *args, **options):
        file_path = '../data/ingredients.json'

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

                ingredients = [
                    IngredientModel(
                        title=item['name'],
                        measurement_unit=item.get('measurement_unit', 'г.')
                    )
                    for item in data
                ]

                IngredientModel.objects.bulk_create(ingredients, ignore_conflicts=True)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Успешно импортировано {len(ingredients)} ингредиентов'
                    )
                )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
        except json.JSONDecodeError:
            self.stdout.write(
                self.style.ERROR('Ошибка: Некорректный формат JSON')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка: {str(e)}')
            )
