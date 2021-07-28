from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from xlsxwriter import workbook

from api.models import RecipeComponent


class ShoppingCartDL(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        shop_list = {}
        cart = user.author.all()
        for record in cart:
            recipe = record.recipe
            ingredients = RecipeComponent.objects.filter(recipe=recipe)
            for ingredient in ingredients:
                amt = ingredient.amount
                name = ingredient.ingredient.name
                units = ingredient.ingredient.units
                if name not in shop_list:
                    shop_list[name] = {
                        'measurement_unit': units,
                        'amount': amt
                    }
                else:
                    shop_list[name]['amount'] = (
                                shop_list[name]['amount'] +
                                amt)
        wishlist = []
        for item in shop_list:
            wishlist.append(
                f'{item} - {shop_list[item]["amount"]} '
                f'{shop_list[item]["measurement_unit"]} \n'
            )
        wishlist.append('\n')
        wishlist.append('FoodGram, 2021')
        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
