import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
import json



def get_main_description(userprompt,temp=0.5,model='yandexgpt/latest'):
    prompt = {
        "modelUri": "gpt://b1g5du6ksd646nmsi6do/"+model,
        "completionOptions": {
            "stream": False,
            "temperature": temp,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": '''Сформируй качественное текстовое описание товара, отвечающее на запросы пользователей по сценариям использования, преимуществам, отличиям с точки зрения потребителя, его жизненным ситуациям и сценариям использования. Описание должно быть пригодно для размещения на публичных сайтах для целей привлечения трафика (SEO оптимизации), улучшения поиска товара и помощи потребителям в выборе. 
Описание должно включать:
- Как продукт полезен и какие проблемы он решает.
- Основные характеристики продукта.
- Отличительные параметры по сравнению с другими продуктами.
- Указание сегмента, к которому относится продукт, с ясным отображением преимуществ, характерных для этого сегмента.

Объем текста должен быть от 500 до 3000 символов. Текст должен быть сплошным и связным. 
                '''            
            },
            {
                "role": "system",
                "text":
            '''Структура текста:
•	Абзацы размером не более 3-4 предложений каждый
•	Маркированные и/или нумерованные списки
•	В начале описания приводите название товара —связку «Тип товара» + «Бренд» + «Модель».
•	Способ применения, Состав, Комплектация, должны быть вынесены в отдельные характеристики.
Недопустимые действия:
•	Нельзя преподносить обычное свойство товара в качестве преимущества. Если у товара нет отстройки от конкурентов по этому параметру, не надо выдавать его за особенность. Если товар сделан из пластика, не надо писать «сделан из высококачественного пластика». Упомяните материал корпуса, только если клиенты подчеркивают его надежность или он важен для совершения покупки.
•	Нельзя вызывать ярко выраженные отрицательные эмоции у покупателя, стыдить или запугивать его. Акцент должен быть сделан именно на благополучном решении проблемы и повышении качества жизни.
•	Нельзя использовать более 2-3 восклицательных знаков на весь текст. Текст должен быть позитивным, но не экзальтированным.
•	Уникальность описания должна быть не менее 80%
Стоп-слова:
•	«скидка», «распродажа», «дешевый», «подарок» (кроме подарочных категорий), «бесплатно», «акция», «специальная цена», «новинка», «new», «аналог», «заказ», «хит».
Исключаем штампы. Не используй много прилагательных и канцеляризмов. 
'''
            },
            {
                "role": "user",
                "text": userprompt
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVNx0lYxBvh9dDYtZJx2ewQ__y3vS6uLtR1WDYo"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    
    try:
        x=json.loads(result)
        return x["result"]["alternatives"][0]["message"]['text']
    except:
        print(result)
        return None


# In[190]:


def get_snippet(userprompt,temp=0.5,model='yandexgpt/latest'):
    prompt = {
        "modelUri": "gpt://b1g5du6ksd646nmsi6do/"+model,
        "completionOptions": {
            "stream": False,
            "temperature": temp,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": '''Создай короткий SEO сниппет из описания товара. Сниппет должен быть информативным, содержать ключевые преимущества и отличия товара, а также быть привлекательным для пользователей. Объем сниппета должен быть от 150 до 160 символов.'''            
            },
            {
                "role": "user",
                "text": userprompt
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key AQVNx0lYxBvh9dDYtZJx2ewQ__y3vS6uLtR1WDYo"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    
    try:
        x=json.loads(result)
        return x["result"]["alternatives"][0]["message"]['text']
    except:
        print(result)
        return None


def get_seo(sour): # это основная функция 
    res=get_main_description(sour,temp=0.75)
    res2=get_snippet(res,temp=0.75)
    goal_2 = (res,res2)
    descriptions = {'main_description': goal_2[0], 'snippet': goal_2[1]}
    descriptions = json.dumps(descriptions) # dict to string
    descriptions = json.loads(descriptions) # string to json    
    return descriptions
