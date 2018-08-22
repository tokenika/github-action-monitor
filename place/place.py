import json
import os
import urllib.request
import urllib.parse
import time


def get_producers_part(lower_bound=None, limit=200):
    TOKENIKA_ENDPOINT = 'https://api.tokenika.io'
    GET_PRODUCERS_ENDPOINT = '/v1/chain/get_table_rows'
    post_data = {
        "json": True,
        "code": "eosio",
        "scope": "eosio",
        "table": "producers",
        "limit": limit,
        'lower_bound': lower_bound,
    }
    post_data = json.dumps(post_data).encode()
    request = urllib.request.Request(urllib.parse.urljoin(TOKENIKA_ENDPOINT, GET_PRODUCERS_ENDPOINT), data=post_data)
    response = urllib.request.urlopen(request)
    response = json.load(response)
    return response['rows'], response['more']


def get_producers():
    producers_part, more = get_producers_part(None)
    producers = producers_part
    lower_bound = producers_part[-1]['owner']
    while more:
        producers_part, more = get_producers_part(lower_bound)
        producers_part = producers_part[1:]  # skip first producer as it's same as last from previous query
        producers.extend(producers_part)
        lower_bound = producers_part[-1]['owner']
    return producers


def get_producer_place(producer_name):
    producers = get_producers()
    producers.sort(key=lambda x: float(x['total_votes']), reverse=True)
    producers = [e for e in producers if e['is_active'] == 1] # filter out inactive producers
    try:
        return [i for i, producer in enumerate(producers) if producer['owner'] == producer_name][0] + 1
    except IndexError:
        print([e['owner'] for e in producers])
        print(len(producers))
        exit(1)

def send_info_to_slack(msg):
    slack_webhook = os.environ['PLACE_SLACK_WEBHOOK']
    post_data = {'text': msg}
    post_data = json.dumps(post_data).encode()
                                                                                                                     
    request = urllib.request.Request(slack_webhook, data=post_data)
    response = urllib.request.urlopen(request)
    return response                          

producer_name = 'tokenika4eos'
                                                   
with open('place', 'r') as fp:
    producer_place = int(fp.read())          
               
while True:                                                   
    try:                                                                                                   
        check_producer_place = get_producer_place(producer_name)
    except:                             
        pass                                     
    if check_producer_place != producer_place:
        producer_place = check_producer_place
        with open('place', 'w') as fp:
            fp.write(str(producer_place))
                               
        msg = f'{producer_name} #{producer_place}'                     
        print(msg)                                                                           
        try:
            send_info_to_slack(msg)                                                                    
        except:       
            pass                              
                             
    time.sleep(5)
