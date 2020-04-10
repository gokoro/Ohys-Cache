# import modules
import requests
import json
import time
import threading
import re

def main():
    nowTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # Set API urls
    timetableURL = 'https://cryental.dev/api/ohys/timetable'
    searchURL = 'https://your-ohys-api-url/search'
    seriesURL = 'https://your-ohys-api-url/series'
    
    # It'll be main JSON file.
    timetableJSON = {'created_at':nowTime, 'Sunday': [], 'Monday':[], 'Tuesday':[], 'Wednesday':[], 'Thursday':[], 'Friday':[], 'Saturday':[] }

    # Request Timetable API
    timetableRes = requests.get(timetableURL)
    timetableGetJSON = json.loads(timetableRes.text)['database']

    # Loop!
    for dayProperty in timetableGetJSON:
        for item in timetableGetJSON[dayProperty]:
            
            # Set Fragment
            infoFragment = {}

            # Delete special char from title
            item['title'] = re.sub('[:]', '', item['title'])

            # Append title information
            infoFragment.update(item)

            # Set request form
            searchData = {
                'scope': 'series',
                'keyword': item['title']
            }
            # Request Search API
            searchOriginalRes = requests.post(searchURL, searchData).text
            srResponse = json.loads(searchOriginalRes)

            seriesData = {
                'series': item['title'] #srResponse[0]['series']
            }
            seriesOriginalRes = requests.post(seriesURL, seriesData).text
            seResponse = json.loads(seriesOriginalRes)
            
            # Get Episode Number
            try:
                # If not finished episode, and not single episode
                if srResponse[0]['videoFormat'] != 'torrent' and srResponse[0]['episode'] != '-1':
                    infoFragment.update({'episode': srResponse[0]['episode']})

                # If finished episode
                elif srResponse[0]['videoFormat'] == 'torrent' and srResponse[0]['episode'] == '-1':
                    infoFragment.update({'episode': 'Finished'})

                # If single episode
                elif srResponse[0]['videoFormat'] != 'torrent' and srResponse[0]['episode'] == '-1':
                    infoFragment.update({'episode': 'Single'})

                # others
                else:
                    infoFragment.update({'episode': 'N/A'})
            except:
                infoFragment.update({'episode': '0'})

            try:
                infoFragment.update({'info': {'series': seResponse[0]}})
            except:
                infoFragment.update({'info': {'series': ''}})
            
            # Append to Main JSON Object
            timetableJSON[dayProperty].append(infoFragment)

    # Make the main JSON object as file
    with open('episode.json', 'w', encoding='utf-8') as make_file:
        json.dump(timetableJSON, make_file, separators=(',',':'), ensure_ascii=False)

    print('Created JSON file! '+ nowTime)

    # Execute every 10minutes(600sec)
    threading.Timer(600,main).start()


main()