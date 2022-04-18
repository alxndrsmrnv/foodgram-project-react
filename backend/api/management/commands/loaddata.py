import csv
from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('ingredients.csv', 'r', encoding='utf8') as file:
            reader = csv.reader(file)
            print(reader)
            for line in reader:
                Ingredient.objects.create(name=line[0],
                                          measurement_unit=line[1])
