import os
import sys
import vk_api
import telebot
import configparser
import logging
from telebot.types import InputMediaPhoto

import bot_config

bot = telebot.TeleBot(bot_config.BOT_TOKEN) # Initializing the telegram bot


