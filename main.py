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

# We check the data according to the conditions before sending
def check_posts_vk():
    response = get_data(bot_config.DOMAIN, bot_config.COUNT)
    response = reversed(response['items'])

    for post in response:

        # Reading the last known id from the file
        id = config.get('Settings', 'LAST_ID')

        # We compare the id, skip the already published ones
        if int(post['id']) <= int(id):
            continue

        print('-----------------------------------------')
        print(post)

        # text
        text = post['text']

        # We check if there is something attached to the post
        images = []
        links = []
        attachments = []
        if 'attachments' in post:
            attach = post['attachments']
            for add in attach:
                if add['type'] == 'photo':
                    img = add['photo']
                    images.append(img)
                elif add['type'] == 'audio':
                    continue
                elif add['type'] == 'video':
                    video = add['video']
                    if 'player' in video:
                        links.append(video['player'])
                else:
                    for (key, value) in add.items():
                        if key != 'type' and 'url' in value:
                            attachments.append(value['url'])

        if bot_config.INCLUDE_LINK:
            post_url = "https://vk.com/" + bot_config.DOMAIN + "?w=wall" + \
                str(post['owner_id']) + '_' + str(post['id'])
            links.insert(0, post_url)
        text = '\n'.join([text] + links)
        send_posts_text(text)

        if len(images) > 0:
            image_urls = list(map(lambda img: max(
                img["sizes"], key=lambda size: size["type"])["url"], images))
            print(image_urls)
            bot.send_media_group(bot_config.CHANNEL, map(
                lambda url: InputMediaPhoto(url), image_urls))

        # We check whether there is a repost of another record
        if 'copy_history' in post:
            copy_history = post['copy_history']
            copy_history = copy_history[0]
            print('--copy_history--')
            print(copy_history)
            text = copy_history['text']
            send_posts_text(text)

            # We check whether the repost has an attached message
            if 'attachments' in copy_history:
                copy_add = copy_history['attachments']
                copy_add = copy_add[0]

                # if links
                if copy_add['type'] == 'link':
                    link = copy_add['link']
                    text = link['title']
                    send_posts_text(text)
                    img = link['photo']
                    send_posts_img(img)
                    url = link['url']
                    send_posts_text(url)

                # if pics
                if copy_add['type'] == 'photo':
                    attach = copy_history['attachments']
                    for img in attach:
                        image = img['photo']
                        send_posts_img(image)

        # save id
        config.set('Settings', 'LAST_ID', str(post['id']))
        with open(config_path, "w") as config_file:
            config.write(config_file)

# text
def send_posts_text(text):
    if text == '':
        print('no text')
    else:
        # В телеграмме есть ограничения на длину одного сообщения в 4091 символ, разбиваем длинные сообщения на части
        for msg in split(text):
            bot.send_message(bot_config.CHANNEL, msg, disable_web_page_preview=not bot_config.PREVIEW_LINK)

def split(text):
    if len(text) >= max_message_length:
        last_index = max(
            map(lambda separator: text.rfind(separator, 0, max_message_length), message_breakers))
        good_part = text[:last_index]
        bad_part = text[last_index + 1:]
        return [good_part] + split(bad_part)
    else:
        return [text]

# images
def send_posts_img(img):
    url = max(img["sizes"], key=lambda size: size["type"])["url"]
    bot.send_photo(bot_config.CHANNEL, url)

if __name__ == '__main__':
    check_posts_vk()
