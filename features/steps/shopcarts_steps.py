# spell: ignore shopcarts shopcart
"""
Shopcart Steps

Steps file for shopcart.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204

@given('the following shopcarts')
def step_impl(context):
    """ Delete all shopcarts and load new ones """

    # List all of the shopcarts and delete them one by one
    rest_endpoint = f"{context.base_url}/api/shopcarts"
    context.resp = requests.get(rest_endpoint)
    assert(context.resp.status_code == HTTP_200_OK)
    for shopcart in context.resp.json():
        context.resp = requests.delete(f"{rest_endpoint}/{shopcart['id']}")
        assert(context.resp.status_code == HTTP_204_NO_CONTENT)

    # load the database with new shopcarts
    for row in context.table:
        payload = {
            "user_id": row['user_id'],
            "name": row['name'],
            "total_price": row['total_price'],
            "status": row['status']
            #"items": row['items']
        }
        context.resp = requests.post(rest_endpoint, json=payload)
        assert(context.resp.status_code == HTTP_201_CREATED)