# -*- coding:utf-8 -*-
from rasa_core.actions import Action
from rasa_core.events import SlotSet


class ActionQueryInsurance(Action):
    def name(self):
        return 'action.ActionQueryInsurance'

    def run(self, dispatcher, tracker, domain):
        carno = tracker.get_slot('carno')
        if carno[0] == '沪':
            fee = 5000
            hu = '沪'
        else:
            fee = 6000
            hu = '外'
        msg = "您是平安的老客户了, " + \
              "去年你投保的项目如下车损险,不计免赔,三责险100万, " + \
              "车牌为%s牌, 总保费是%d元" % (hu, fee)
        dispatcher.utter_message(msg)
        return [SlotSet("fee", fee)]
