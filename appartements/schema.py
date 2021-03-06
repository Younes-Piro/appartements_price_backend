import graphene
from .models import Appartement
from .mutation import AppartementsType, Dictionary, InnerItem
from django.db.models import Avg, Max, Min, Count
from django.db.models import FloatField
from graphene_django import DjangoListField, DjangoObjectType
import json
# query are useful to query the data from our database


class Query(graphene.ObjectType):

    all_appartements = graphene.List(AppartementsType)
    single_appartement = graphene.List(AppartementsType)
    cards = graphene.List(Dictionary)
    details_grouping = graphene.List(Dictionary)
    number_rooms_count = graphene.List(Dictionary)
    surface_distribution = graphene.List(Dictionary)
    every_city_num_rooms = graphene.List(Dictionary, city=graphene.String())

    # details of pricing

    def resolve_cards(self, info):
        example_dict = {
            "NUMBER APPARTEMENT": {"value": Appartement.objects.aggregate(Count('price')).get('price__count')},
            "MINIMAL PRICE": {"value": Appartement.objects.aggregate(Min('price')).get('price__min')},
            "AVERAGE PRICE": {"value": Appartement.objects.aggregate(Avg('price')).get('price__avg')},
            "MAX PRICE": {"value": Appartement.objects.aggregate(Max('price')).get('price__max')}
        }

        results = []        # Create a list of Dictionary objects to return

        # Now iterate through your dictionary to create objects for each item
        for key, value in example_dict.items():
            inner_item = InnerItem(value['value'])
            dictionary = Dictionary(key, inner_item)
            results.append(dictionary)

        return results

    # details after grouping
    def resolve_details_grouping(self, info):

        diction = Appartement.objects.values('city').annotate(
            avg_rooms=Avg('nmbr_of_rooms'),
            avg_surface=Avg('surface')
        ).order_by()

        Dict = {}
        for single_dic in diction:
            Dict[single_dic.get('city')] = single_dic

        results = []        # Create a list of Dictionary objects to return
        # Now iterate through your dictionary to create objects for each item
        for key, value in Dict.items():
            inner_item = InnerItem(
                value['avg_rooms'], value['avg_surface'])
            dictionary = Dictionary(key, inner_item)
            results.append(dictionary)

        return results

    # number of rooms count
    def resolve_number_rooms_count(self, info):
        diction = Appartement.objects.values('nmbr_of_rooms').annotate(
            count_rooms=Count('nmbr_of_rooms'),
        ).order_by('-count_rooms')[:5]

        all_number_rooms = Appartement.objects.aggregate(
            count_total_rooms=Count('nmbr_of_rooms'))
        print('******************')
        print(all_number_rooms.get("count_total_rooms"))

        Dict = {}
        for single_dic in diction:
            Dict[single_dic.get('nmbr_of_rooms')] = single_dic

        results = []        # Create a list of Dictionary objects to return
        for key, value in Dict.items():
            inner_item = InnerItem(value['count_rooms'])
            dictionary = Dictionary(key, inner_item)
            results.append(dictionary)

        print(diction)

        return results

    def resolve_surface_distribution(self, info, **kwargs):
        diction = Appartement.objects.values('surface').annotate(
            count_surface=Count('surface'),
        ).order_by('-count_surface')[:10]

        Dict = {}
        for single_dic in diction:
            Dict[single_dic.get('surface')] = single_dic

        results = []        # Create a list of Dictionary objects to return
        for key, value in Dict.items():
            inner_item = InnerItem(value['count_surface'])
            dictionary = Dictionary(key, inner_item)
            results.append(dictionary)

        print(diction)
        return results

    def resolve_single_appartement(self, info, **kwargs):
        return Appartement.objects.total_price().first()

    def resolve_all_appartements(self, info, **kwargs):
        return Appartement.objects.all()

    def resolve_every_city_num_rooms(root, info, city):
        diction = Appartement.objects.values('nmbr_of_rooms').filter(city=city).annotate(
            count_rooms=Count('nmbr_of_rooms'),
        ).order_by('-count_rooms')[:5]

        all_number_rooms = Appartement.objects.aggregate(
            count_total_rooms=Count('nmbr_of_rooms'))
        print('******************')
        print(all_number_rooms.get("count_total_rooms"))

        Dict = {}
        for single_dic in diction:
            Dict[single_dic.get('nmbr_of_rooms')] = single_dic

        results = []        # Create a list of Dictionary objects to return
        for key, value in Dict.items():
            inner_item = InnerItem(value['count_rooms'])
            dictionary = Dictionary(key, inner_item)
            results.append(dictionary)

        print(diction)

        return results


# importing the schema
schema = graphene.Schema(query=Query)
