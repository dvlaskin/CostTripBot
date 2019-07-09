# -*- coding: utf-8 -*-
import helpers as hp
import json

print('Enter point A from where you will begin your trip')
pointA = str(input())
locA = hp.SearchLocation(pointA)

print('\r\nPick point A:')
aList = hp.LocationsInfoPrint(locA)
aItem = int(input())
aLocationPoint = locA["results"][aItem-1]["position"]
print(aLocationPoint)


print('\r\nEnter point B where you will end your trip')
pointB = str(input())
locB = hp.SearchLocation(pointB)

print('\r\nPick point B:')
bList = hp.LocationsInfoPrint(locB)
bItem = int(input())
bLocationPoint = locB["results"][bItem-1]["position"]
print(bLocationPoint)

print('\r\nInput Gas Mileage')
gasMileage = float(input())

print('\r\nInput Gas Price')
gasPrice = float(input())

routParams = hp.GetRouting(aLocationPoint,bLocationPoint)
hp.CalcCost(gasMileage, gasPrice, routParams)
