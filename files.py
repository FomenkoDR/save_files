import pandas as pd
from requests import Session
from bs4 import BeautifulSoup
import time



def get_files():
    
    s = Session() 

    #1
    s.get('https://authd.vsk.ru/auth/realms/users_auth/protocol/openid-connect/auth?client_id=prod-keycloak_users_auth_dmzwebtutor_elearning-1&redirect_uri=https%3A%2F%2Fe-learning.vsk.ru%2Fview_doc.html%3Fmode=default&response_type=code')

    #2
    res_1 = s.get('https://authd.vsk.ru/auth/realms/users_auth/protocol/openid-connect/auth?client_id=prod-keycloak_users_auth_dmzwebtutor_elearning-1&redirect_uri=https%3A%2F%2Fe-learning.vsk.ru%2Fview_doc.html%3Fmode=default&response_type=code')

    SAMLRequest = BeautifulSoup(res_1.text, 'lxml').find('div', class_='card-pf').find_all('input')[0].get('value')
    RelayState = BeautifulSoup(res_1.text, 'lxml').find('div', class_='card-pf').find_all('input')[1].get('value')

    #3
    res_2 = s.post('https://adfs.vsk.ru/adfs/ls/', data = {'SAMLRequest': SAMLRequest,'RelayState': RelayState} )

    client_request_id = BeautifulSoup(res_2.text, 'lxml').find('div', class_="groupMargin").find('form').get('action')

    #4

    res_3 = s.post('{}{}'.format('https://adfs.vsk.ru/adfs/ls/',client_request_id) , data={'UserName': 'DFomenko@vsk.ru','Password': '22119912051847fdR','AuthMethod': 'FormsAuthentication'})

    SAMLResponse = BeautifulSoup(res_3.text, 'lxml').find_all('input')[0].get('value')
    RelayState_2 = BeautifulSoup(res_3.text, 'lxml').find_all('input')[1].get('value')

    #5
    res_4 = s.post('https://authd.vsk.ru/auth/realms/users_auth/broker/adfs/endpoint', data={'SAMLResponse': SAMLResponse,'RelayState': RelayState_2}, allow_redirects=False)

    url_5 = res_4.headers['location']

    #6
    res_5 = s.get(url_5, allow_redirects=False)

    #7
    l = len(url_5) + 1 

    s.get("{}{}".format('https://e-learning.vsk.ru:444/view_doc.html?mode', url_5[l//5:])) #url_5[l//5:] = default&session_state=(...)&code=(...)

    #8
    s.get('https://e-learning.vsk.ru/')

    #9
    s.get('https://e-learning.vsk.ru:444/')

    #10
    start_date = '20.05.2024'
    finish_date = '21.05.2024'

    payload = {  
    "collection_code" : "CUSTOM_REPORT_DATA",
    "parameters" : "{}{}{}{}{}".format("sReportMode=table;context=%257B%2522bNotFirstLoad%2522%253A%25221%2522%252C%2522bForceCRRefresh%2522%253A%25221%2522%252C%2522p8_position_parent_id%2522%253A%2522%2522%252C%2522p7_person_id%2522%253A%2522%2522%252C%2522p6_lector_id%2522%253A%2522%2522%252C%2522p5_person_id%2522%253A%2522%2522%252C%2522p4_f_rnwz%2522%253A%2522%2522%252C%2522p3_education_method_id%2522%253A%2522%2522%252C%2522p2_finish_date%2522%253A%2522",(finish_date),"%252000%253A00%253A00%2522%252C%2522p1_start_date%2522%253A%2522",(start_date),"%252000%253A00%253A00%2522%252C%2522p0_event_id%2522%253A%2522%2522%257D;parameters_list=p0_event_id%2Cp1_start_date%2Cp2_finish_date%2Cp3_education_method_id%2Cp4_f_rnwz%2Cp5_person_id%2Cp6_lector_id%2Cp7_person_id%2Cp8_position_parent_id;int_id=;custom_report_id=7089354619627569456")
    }

    res_17 = s.post("{}{}".format("https://e-learning.vsk.ru:444/pp/Ext5/extjs_json_collection_data.html?_dc=",(round(time.time() * 1000))), data=payload)

    #декодируем полученный ответ
    res_17.encoding = res_17.apparent_encoding

    #записываем ответ в переменную
    data = res_17.json()

    #создаём датафрейм только с необходимыми строками
    events = pd.DataFrame(data['results']).filter(regex='c', axis=1)

    #переименовывам столбцы датафрейма
    events.columns = pd.DataFrame(data['columns'])['title'].to_list()

    events = events.iloc[:, 1:]
    
    events.to_csv('Events.csv')

    return events



if __name__ == "__main__":
    files = get_files()
