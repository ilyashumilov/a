import csv

from django.core.management import BaseCommand

from api.models import City, Country


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open("files/cities.csv", newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                en, native = row
                city = City.objects.get(name=en.strip())
                city.native_name = native.strip()
                city.save()

        with open("files/countries.csv", newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                en, native = row
                country = Country.objects.get(name=en.strip())
                country.native_name = native.strip()
                country.save()
