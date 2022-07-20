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
from os.path import join, dirname
from typing import Any, Text, Dict, List
from unittest import result

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
from dotenv import load_dotenv
from pathlib import Path
import os 
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
'''os.getenv() used to read varibles from .env file'''
main_url=os.getenv("MAIN_URL")
search_path = os.getenv("SEARCH_PATH")
search_by_author_path = os.getenv("SEARCH_BY_AUTHOR_PATH")
os.environ['NO_PROXY'] = '127.0.0.1'
SEARCH_URL = f'{main_url}{search_path}'
SEARCH_BY_AUTHOR_URL = f'{main_url}{search_by_author_path}'


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

class ActionSearch(Action):
    
    def name(self) -> Text:
        return "action_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message['text']
        # type = tracker.get_slot('search_type_choice')
        params = {'q': message, 'type': 1}
        response = requests.get(url=f'{SEARCH_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra')
            return []
        dispatcher.utter_message(response.content)
        return [SlotSet("book_name", None)]

class ActionGetAuthor(Action):
    def name(self) -> Text:
        return "action_search_author"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
          
        message = tracker.latest_message['text']

        params = {'q': message,'type': 2}   
        response = requests.get(url=f'{SEARCH_URL}', params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            dispatcher.utter_message('Đã có lỗi xảy ra')
            return []

        content = json.loads(response.content)
        listItem = []
        counter = 1
        for item in content:
            listItem.append(f"{counter} - {item['name']}")
            item['index'] = counter
            counter = counter + 1
        tracker.slots['saved_author'] = json.dumps(content)
        dispatcher.utter_message('\n'.join(listItem))
        return [SlotSet("book_author", None), SlotSet("saved_author", json.dumps(content))]

class ActionGetBookByAuthor(Action):
    def name(self) -> Text:
        return "action_search_book_by_author"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:   
          
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
            dispatcher.utter_message('Đã có lỗi xảy ra')
            return []

        counter = 1
        content = json.loads(response.content)

        for item in content:
            item['index'] = counter
            counter = counter + 1
        result = Service.productObjectToString(content)
        dispatcher.utter_message(result)
        print(result)
        return [SlotSet("book_author", None), SlotSet("saved_author", None)]