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
    SEARCH_URL = f'{main_url}{search_path}'
    def name(self) -> Text:
        return "action_search"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = tracker.latest_message['text']
        os.environ['NO_PROXY'] = '127.0.0.1'
        response = requests.get(url=f'{self.SEARCH_URL}{message}')
        print(response.url)
        print(response.content)
        dispatcher.utter_message(response.content)
        return [SlotSet("book_name", None)]
