import requests
import urllib
import json
import re

__appId = 'xLE54zcKJOWjPF0uuOdo'
__app_code = 'owgDiqgdobP3ASLuDDlvxw'

def GetOptionStr(dictParam):
        """
        Formated info about location
        """
        # return '\r\n' + str(dictParam["categoryTitle"]) + \
        # ' -> ' + dictParam["title"] + \
        # ' -> ' + dictParam["vicinity"] + \
        # ' -> ' + str(dictParam["position"])
        return '\r\n' + dictParam["title"] + ' -> ' + dictParam["vicinity"]

def GetOptionMsg(locList):
        """
        Formated info about location
        """
        counter = 1
        result = ''
        for item in locList:
                result += '\r\n'+ str(counter) + '. ' + item["title"] + ' -> ' + item["vicinity"]
                counter += 1
        return result

def LocationsInfo(jsonResult):
        """
        Print all variants of found locations
        and return List of locations
        """
        categoryTitleList = ['Building', 'Street or Square', 'City, Town or Village']

        aList = []
        counter = 1
        for items in jsonResult["results"]:
                if ('categoryTitle' in items 
                and categoryTitleList.count(items['categoryTitle']) != 0 
                and counter <= 5):   
                        aList.append(items)
                        counter += 1
        return aList

def LocationsInfoPrint(jsonResult):
        """
        Print all variants of found locations
        and return List of locations
        """
        categoryTitleList = ['Building', 'Street or Square', 'City, Town or Village']

        aList = []
        counter = 1
        for items in jsonResult["results"]:
                if ('categoryTitle' in items 
                and categoryTitleList.count(items['categoryTitle']) != 0                     
                and counter <= 5):
                        paramText = GetOptionStr(items)
                        aList.append(paramText)
                        print(counter, paramText)
                        counter += 1
        return aList

def SearchLocation(locationTex):
        """
        Search locations by input text
        """
        result = requests.get('https://places.cit.api.here.com/places/v1/autosuggest' +
        '?at=0,0' +
        '&q='+urllib.parse.quote(locationTex) +
        '&app_id={}'.format(__appId) +
        '&app_code={}'.format(__app_code))

        # print(result)
        jsonText = json.loads(result.text)
        # PrintJsonString(jsonText)
        return jsonText

def GetRouting(geoPointFrom, geoPointTo):
        """
        Method to get rout from point A to point B
        return List of summary infornation
        distance: in metr (to convert in km = distance/1000), 
        baseTime: in seconds (to convert in minutes = time/60, hours = time/120)
        """
        result = requests.get('https://route.api.here.com/routing/7.2/calculateroute.json'+
        '?waypoint0=' + urllib.parse.quote(','.join(str(x) for x in geoPointFrom)) +
        '&waypoint1=' + urllib.parse.quote(','.join(str(x) for x in geoPointTo)) +
        '&mode='+urllib.parse.quote('fastest;car;traffic:disabled')+
        '&app_id={}'.format(__appId) +
        '&app_code={}'.format(__app_code))

        # print(result)
        jsonText = json.loads(result.text)
        # PrintJsonString(jsonText)

        retVals = []
        if 'route' in jsonText['response']:                
                for resultItem in jsonText['response']['route']:
                        retVals.append(resultItem['summary'])
                
                return retVals
        else:
                print('not ok')
                return retVals

def CalcCost(gasMileage, gasPrice, distList):
        """
        Method to count a cost of trip from point A to poit B
        """
        counter = 0
        for item in distList:
                counter += 1
                print('\r\nvariant', counter)
                print(CleanHtml(item['text']))
                print('Cost trip will be $',  
                        round((item['distance']/1000) / 100 * gasMileage * gasPrice)
                ) 

def CalcCostResult(gasMileage, gasPrice, distList):
        """
        Method to count a cost of trip from point A to poit B
        """
        result = ''
        for item in distList:
                result += (CleanHtml(item['text']))
                result += '\r\nCost trip will be ${}'.format(
                        round((item['distance']/1000) / 100 * gasMileage * gasPrice)
                ) 
        return result

def PrintJsonString(jsonText):
        """
        Print formated json text
        """
        print(json.dumps(jsonText,indent=4, sort_keys=True))

def CleanHtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext