import csv

from api.models import Ingredient


def run():
    with open('C:/Dev/foodgram-project-react/data/ingredients.csv',
              mode='r', encoding='utf8') as file:
        reader = csv.reader(file)
        print(reader)
        for line in reader:
            Ingredient.objects.create(name=line[0], measurement_unit=line[1])
