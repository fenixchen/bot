# -*- coding:utf-8 -*-
from rasa_core.actions import Action


class ActionQueryInsurance(Action):
    def name(self):
        return 'action_query_insurance'

    def run(self, dispatcher, tracker, domain):
        carno = tracker.get_slot('carno')
        if carno[0] == '沪':
            fee = 5000
            dispatcher.utter_message("你好,你是沪牌,保险费5000")
        else:
            fee = 6000
            dispatcher.utter_message("你好,你是外牌,保险费6000")
        self._set_slot("fee", fee)
        return []

