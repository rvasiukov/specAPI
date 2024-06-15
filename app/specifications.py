import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import xml.etree.ElementTree as ET
import json

from rapidfuzz import fuzz #!pip install rapidfuzz
import pickle
from urllib import request


def search(q='apple macbook air m1',testmode=False):
    if testmode:
        ans=open('testsearch.txt').read()
    else:
        response = requests.get(f'https://yandex.com/search/xml?folderid=b1g5du6ksd646nmsi6do&apikey=AQVNx0lYxBvh9dDYtZJx2ewQ__y3vS6uLtR1WDYo&query={q}')
        ans=response.text
    results=[]
    ans=ans.replace('<hlword>','').replace('</hlword>','')
    root = ET.fromstring(ans)
    for type_tag in root.findall('response/results/grouping/group/doc'):
        value = [type_tag.find('domain').text,type_tag.find('title').text,type_tag.find('url').text]
        results.append(value)
    return results


def parsewebpage(url):
    html = requests.get(url).text
    try:
        soup = BeautifulSoup(html,"html.parser",from_encoding="utf-8")
    except:
        return 'Protected'
    alltext = soup.findAll('div')
    simple=[i.text.replace('\n',' ') for i in alltext]
    site=' '.join(simple)
    site=' '.join(site.split())
    is_protected = False
    red_flags = ['VPN','CAPTCHA','captcha','Captcha']
    for rf in red_flags:
        if rf in site: 
            is_protected = True
            break
    if not(is_protected) and len(site) != 0:
        sys_prompt = f'Предоставь среднюю по размеру выдержку по содержимому текста, обращения от первого лица запрещены, в выдержку необходимо включить характеристики продукта, о котором идёт речь, необходимо добавить в выдержку ссылку на информацию: {url}'
        user_prompt = f'Предоставь среднюю по размеру выдержку по содержимому текста, обращения от первого лица запрещены, в выдержку необходимо включить характеристики продукта, о котором идёт речь, необходимо добавить в выдержку ссылку на информацию: {url}'
        #print(site,'p')
        site = yagpt_webpage(' '.join(site[:99401].split()[:3250]),sys_prompt,user_prompt,temp=0.75)
        return site
    else:
        site = 'Protected'
        return site


def yagpt_webpage(site,sysprompt,userprompt,temp=0.5,model='yandexgpt-lite/latest'):
    #print(site,'y')
    if site == 'Protected': return None
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
                "text": site
            },
            {
                "role": "system",
                "text": sysprompt
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


def lev_check(text, target):
    """Функция фналогична косинусному сходству только без векторизации"""
    score = 0
    pos = 0
    for i in range(len(text) - len(target)):
        # делим метрику на 100, т.к. данная метрика находится в пределах от 0 до 100
        current_score = fuzz.ratio(text[i: i + len(target)], target)/100
        if current_score > score:
            score = current_score
            pos = i
    return score, text[pos: pos + len(target)]


def searchlist(trusted_sources,brand = 'APPLE',model = 'MACBOOK PRO "MK183"',part_num = ''):
    if part_num!='': part_num = '+'+part_num
    trusted_sites = ['']
    search_mode = 'site:'
    search_range = 'trusted'
    if brand.upper() in trusted_sources.keys(): trusted_sites = trusted_sources[brand.upper()]
    else:
        search_mode = ''
        search_range = 'global'
    src_list=[]
    for j in trusted_sites:  
        a=search(q=search_mode+j+' +'+brand+' +'+model+' '+part_num+' +Technical Specifications')
        if search_range == 'global': 
            src_list = list([x[2] for x in a])
        else: 
            if len(a)!=0: src_list.append(a[0][2])
    return src_list


def construct(name, spec, source,i):
    new_dic = {'specification'+str(i): {} }
    values = [{'name': name}, {'value': spec}, {'source':source}]
    for val in values:
        new_dic['specification'+str(i)].update(val)
    return new_dic


def to_json(l):
    a_dict={'specifications': {} }
    i=0
    for xx in l:
        add_dict = construct(xx[0],xx[1],xx[2],i)
        a_dict['specifications'].update(add_dict)
        i+=1
    return a_dict


def find_spec(trusted_sources,src_count = 10,brand = 'APPLE',model = 'MACBOOK PRO "MK183"',part_num = ''):
    src_count = 10
    cn = 0
    parsed_list = ''
    srcs_list=searchlist(trusted_sources,brand,model,part_num)
    for m in srcs_list:
        sys=f'Проанализируй текст и дай четкий ответ к запросу в виде таблицы. Обращения от первого лица запрещены, без красочных описаний. В таблице должно быть 3 столбца: Характеристика; Значение; Ссылка, после каждой характеристики в столбе Ссылка напиши "{m}", сделать это - обязательно, ссылка должна быть написана точно также как и запросе'
        user=f'Напиши Характеристики товара {model} в виде таблицы, в ответе требуется только таблица, остальной текст строго запрещен, в таблице должно быть 3 столбца: Характеристика; Значение; Ссылка. После каждой характеристики в столбе Ссылка напиши "{m}", сделать это - обязательно, необходимо строго соблюдать формат таблицы, не должно оставаться пустых значений в таблице'
        if 'citilink' in m: continue
        parsed = yagpt_webpage(parsewebpage(m),sys,user,temp=0.75,model='yandexgpt/latest')
        if not(parsed in ('Protected',None)):
            parsed_list = parsed_list + parsed + '\n' + '=\n'
            cn+=1
        if cn>=src_count: break
    characyers = parsed_list.split('\n')
    characyers = list([x.replace('|','^',3).replace('|','').replace('(','').replace(')','').replace('[','').replace(']','').replace('{','').replace('{','').replace('<','').replace('>','').split('^') for x in characyers])
    true_list = []
    for x in characyers:
        if any('Характеристика' in y for y in x) or any('--' in y for y in x): continue
        else:
            ch = x
            while '' in ch: del ch[ch.index('')]
            true_list.append(ch)
    ch_mass=[]
    ch=list(set([' '.join(i[0].replace('*','').split()) for i in true_list if len(i) == 3 and ' '.join(i[0].replace('*','').split())!='']))
    for i in range(len(ch)):
        for j in range(len(ch)):
            v=lev_check(ch[i],ch[j])
            if v[0] >= 0.9:
                ch[j]=''
    ch=[i for i in ch if i!='']
    for i in ch:
        c=[]
        for j in true_list:
            if len(j)==3 and ' '.join(j[2].replace('*','').split())!='' and ' '.join(j[1].replace('*','').split())!='—':
                v=lev_check(j[0],i)
                if v[0] >= 0.8:
                    c.append([v[0],' '.join(j[1].replace('*','').split()),' '.join(j[2].replace('*','').split())])
        try:
            ch_mass.append([i]+max(c)[1:])
        except:
            ...
    for i in range(len(ch_mass)):
        c=[]
        for j in range(len(ch_mass)):
            v=lev_check(ch_mass[i][1],ch_mass[j][1])
            if v[0] >= 0.8:
                ch_mass[j][0]='del'
    ch_mass=[i for i in ch_mass if i[0]!='del']
    return to_json(ch_mass)

def similarity_check(specifications_input):
    import codecs
    import json
    import jellyfish 
    full_synonym_base = pickle.load(request.urlopen('https://storage.yandexcloud.net/trusted/full_synonym_base.pickle'))
    f = specifications_input #Спецификации от API
    out = {}
    for spec in f['specifications'].keys():
        nam, val, src = f['specifications'][spec]['name'],f['specifications'][spec]['value'],f['specifications'][spec]['source']
        f['specifications'][spec]['syns'] = []
        max_similarity = 0
        most_sim_spec = None
        l=''
        for similar_spec in full_synonym_base.keys():
            target_list = full_synonym_base[similar_spec]
            similarity = jellyfish.jaro_winkler_similarity(nam, similar_spec)
            if similarity >= 0.8 and (similarity == max(similarity,max_similarity)):
                max_similarity = similarity
                most_sim_spec = similar_spec
            for el in target_list:
                similarity = jellyfish.jaro_winkler_similarity(nam, el)
                if similarity >= 0.8 and (similarity == max(similarity,max_similarity)):
                    max_similarity = similarity
                    most_sim_spec = similar_spec
                    l = el
        if max_similarity != 0:
            out[spec] = {'name': most_sim_spec, 'value': val, 'source': src}
    print(out)

def get_spec(brand,model, part_num=''):
    trusted_sources = pickle.load(request.urlopen('https://storage.yandexcloud.net/trusted/sourses.pkl'))
    specifications_input = find_spec(trusted_sources,brand=brand,model=model,part_num=part_num)
    return similarity_check(specifications_input)
