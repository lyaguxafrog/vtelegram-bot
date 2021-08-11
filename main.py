import os
import sys
import vk_api
import telebot
import configparser
import logging
from telebot.types import InputMediaPhoto

import bot_config

bot = telebot.TeleBot(bot_config.BOT_TOKEN) # Initializing the telegram bot

# Getting data from vk.com
def get_data(domain_vk, count_vk):
    vk_session = vk_api.VkApi(bot_config.LOGIN, bot_config.PASSWORD)
    vk_session.auth()
    vk = vk_session.get_api()
    response = vk.wall.get(domain=domain_vk, count=count_vk) # We use the wall method.get from the API documentation vk.com
    return response