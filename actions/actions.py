# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []
import json
from operator import index
from os.path import join, dirname
from typing import Any, Text, Dict, List
from unittest import result

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, FollowupAction, ActionExecuted
import requests
from dotenv import load_dotenv
from pathlib import Path
import os 
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
'''os.getenv() used to read varibles from .env file'''
main_url=os.getenv("MAIN_URL")
client_url=os.getenv("CLIENT_URL")
search_path = os.getenv("SEARCH_PATH")
search_by_author_path = os.getenv("SEARCH_BY_AUTHOR_PATH")
search_by_category_path = os.getenv("SEARCH_BY_CATEGORY_PATH")
os.environ['NO_PROXY'] = '127.0.0.1'
SEARCH_URL = f'{main_url}{search_path}'
SEARCH_BY_AUTHOR_URL = f'{main_url}{search_by_author_path}'
SEARCH_BY_CATEGORY_URL = f'{main_url}{search_by_category_path}'
BOT_PUSH_CART_URL = f'{main_url}/bot-push-cart'
BOT_GET_ORDER_DETAIL_URL = f'{main_url}/bot-order-detail/'

class Service():
    def productObjectToString(p : List[Dict[Text, Any]]) -> Text:
        listAttr = ['index', 'name', 'short_description']
        listItem = []
        for item in p:
            attrValueList = []
            for attr in listAttr:
                print(attr)
                print(item[attr])
                attrValueList.append(item[attr])
            listItem.append(' - '.join(str(x) for x in attrValueList))

        return '\n'.join(listItem) 

class ActionAskBook(Action):
    def name(self) -> Text:
        return "action_ask_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message['intent'].get('name')
        tracker.latest_message['text']
        print(tracker.latest_message.keys())

        # headers = {
        #     'Content-Type': 'application/json; charset=utf-8',
        # }

        # payload = {"message": message}
        # payload = json.dumps(payload)
        # response = requests.get("http://127.0.0.1:8080/api/ask-totalinfect",
        #                             data=payload,
        #                      headers=headers)

        # data = response.json()['data']
        print(message)
        dispatcher.utter_message("hello world")
        return []

class ActionAnswerOrder(Action):
    def name(self) -> Text:
        return "action_answer_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        message = tracker.latest_message['intent'].get('name')
        orderId = tracker.get_slot('cust_order')

        response = requests.get(url=f'{BOT_GET_ORDER_DETAIL_URL}{orderId}')
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]

        content = json.loads(response.content)
        if not content:
            dispatcher.utter_message('Không có đơn hàng nào phù hợp, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]
        
        order = content['order']
        info = content['info']
        orderValue = content['orderValue']
        items = content['items']
        result = f"Mã đơn hàng: {orderId}\nThông tin người nhận: \n  + Tên người nhận: {info['name']}\n  + Số điện thoại nhận hàng: {info['phone']}\n  + Địa chỉ nhận hàng: {info['address']}\nGiá trị đơn hàng: {orderValue} VND\nTrạng thái đơn hàng: {order['message']}\nSản phẩm: \n"
        for item in items:
            result = result + f"  + {item['name']} - Số lượng: {item['quantity']}\n"
        dispatcher.utter_message(result)
        return [AllSlotsReset()]

class ActionSearch(Action):
    
    def name(self) -> Text:
        return "action_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print("action", self.name())
        message = tracker.latest_message['text']
        # type = tracker.get_slot('search_type_choice')
        params = {'q': message, 'type': 1}
        response = requests.get(url=f'{SEARCH_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]

        counter = 1
        content = json.loads(response.content)
        if not content:
            dispatcher.utter_message('Không có kết quả nào, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]

        for item in content:
            item['index'] = counter
            counter = counter + 1
        result = Service.productObjectToString(content)
        dispatcher.utter_message(result)

        return [AllSlotsReset(), SlotSet("saved_product", json.dumps(content))]

class ActionGetAuthor(Action):
    def name(self) -> Text:
        return "action_search_author"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
        print("action", self.name())
        message = tracker.latest_message['text']

        params = {'q': message,'type': 2}   
        response = requests.get(url=f'{SEARCH_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]

        content = json.loads(response.content)
        if not content:
            dispatcher.utter_message('Không có kết quả nào, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]
        listItem = []
        counter = 1
        for item in content:
            listItem.append(f"{counter} - {item['name']}")
            item['index'] = counter
            counter = counter + 1
        tracker.slots['saved_author'] = json.dumps(content)
        print('\n'.join(listItem))
        dispatcher.utter_message('\n'.join(listItem))
        return [SlotSet("search_type_choice", None), SlotSet("book_author", None), SlotSet("saved_author", json.dumps(content))]

class ActionGetBookByAuthor(Action):
    def name(self) -> Text:
        return "action_search_book_by_author"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
        print("action", self.name())
        message = tracker.latest_message['text']
        saved_author = tracker.get_slot('saved_author')
        target_id = None
        content = json.loads(saved_author)
        for item in content:
            if item['index'] == int(message):
                target_id = item['id']

        params = {'authorId': target_id} 
        response = requests.get(url=f'{SEARCH_BY_AUTHOR_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [AllSlotsReset()]

        counter = 1
        content = json.loads(response.content)
        if not content:
            dispatcher.utter_message('Không có kết quả nào, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]
        for item in content:
            item['index'] = counter
            counter = counter + 1
        result = Service.productObjectToString(content)
        dispatcher.utter_message(result)
        print(content[0])
        return [AllSlotsReset(), SlotSet("saved_product", json.dumps(content))]

class ActionGetCategory(Action):
    def name(self) -> Text:
        return "action_search_category"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
        print("action", self.name())
        message = tracker.latest_message['text']

        params = {'q': message,'type': 3}   
        response = requests.get(url=f'{SEARCH_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [AllSlotsReset()]

        content = json.loads(response.content)
        if not content:
            dispatcher.utter_message('Không có kết quả nào, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]

        listItem = []
        counter = 1
        for item in content:
            listItem.append(f"{counter} - {item['name']}")
            item['index'] = counter
            counter = counter + 1
        tracker.slots['saved_category'] = json.dumps(content)
        print('\n'.join(listItem))
        dispatcher.utter_message('\n'.join(listItem))
        return [SlotSet("search_type_choice", None), SlotSet("book_category", None), SlotSet("saved_category", json.dumps(content))]

class ActionGetBookByCategory(Action):
    def name(self) -> Text:
        return "action_search_book_by_category"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
        print("action", self.name())
        message = tracker.latest_message['text']
        saved_category = tracker.get_slot('saved_category')
        target_id = None
        content = json.loads(saved_category)
        for item in content:
            if item['index'] == int(message):
                target_id = item['id']

        params = {'categoryId': target_id} 
        response = requests.get(url=f'{SEARCH_BY_CATEGORY_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [AllSlotsReset()]

        counter = 1
        content = json.loads(response.content)
        if not content:
            dispatcher.utter_message('Không có kết quả nào, mời bạn hỏi tiếp')
            return [FollowupAction("action_restart")]
        for item in content:
            item['index'] = counter
            counter = counter + 1
        result = Service.productObjectToString(content)
        dispatcher.utter_message(result)
        return [AllSlotsReset(), SlotSet("saved_product", json.dumps(content))]

class ActionPushBookToCart(Action):
    def name(self) -> Text:
        return "action_push_book_to_cart"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]: 
        
        print("action", self.name())
        try:
            uid = int(tracker.current_state()['sender_id'])
        except:
            uid = 3
        
        print("uid",uid,tracker.current_state()['sender_id'])
        choice_book = tracker.get_slot('choice_book')
        quantity = tracker.get_slot('quantity')

        saved_book = json.loads(tracker.get_slot('saved_product'))
        book = {id:1}
        for item in saved_book:
            if item['index'] == int(choice_book):
                book = item

        data = {
            'uid': uid,
            'pid': book['id'],
            'quantity': quantity
        } 
        print("data",data)
        response = requests.post(url=f'{BOT_PUSH_CART_URL}', json=data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra trong quá trình tìm kiếm, mời bạn hỏi tiếp')
            return [ActionExecuted("action_listen")]

        content = json.loads(response.content)
        if content['status'] == 1:
            dispatcher.utter_message(f'Sách đã được đưa vào giỏ hàng thành công. Bạn có thể thực hiện đặt hàng ngay tại {client_url}/cart. Xin cảm ơn.')
        else:
            dispatcher.utter_message('Đã có lỗi xảy ra, mời bạn hỏi tiếp')
        return [AllSlotsReset()]