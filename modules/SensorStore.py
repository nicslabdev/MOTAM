#! /usr/bin/python3

#########################################################
# Python3 module for managing MOTAM BLE sensors         #
#  collected from multiple sources: BLE4 scanner, BLE5  #
#  scanner, simulation...                               #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import threading
import time
import struct

class SensorStore:

    # MOTAM constants

    # Beacon type identifiers
    beaconTypeIdentifiers = {
        "trafficSignBeaconId": 1,
        "roadStateBeaconId": 2,
        "bicycleBeaconId": 3,
        "seatBeaconId": 4,
        "intelligentTrafficLightBeaconId": 5,
        "infoPanelBeaconId": 6,
        "pedestrianBeaconId": 7,
        "slowVehicleBeaconId": 8,
        "emergencyVehicleBeaconId": 9
    }

    def __init__(self):
        # self.sensorList = {"id1": {"time": 12345, "payload": "ADE34"}}
        self.sensorList = {}

    # Add new beacon to beacon list or update the data. This will return a "sensors" dictionary
    def add (self,blePayload):

        # beaconId is the ID of the beacon (sometimes the gps coordinates, sometimes a random ID)
        beaconId = blePayload[0:18]

        # if this beacon is still in the dictionary...
        if beaconId in self.sensorList.keys():
            # if the beacon data is the same...
            if (blePayload == self.sensorList[beaconId]["payload"]):
                self.sensorList[beaconId]["time"] = time.time()

                # send exception: Empty Dict
                raise ValueError("Empty")

            # if the beacon data has changed...
            else:
                self.sensorList[beaconId]["time"] = time.time()
                self.sensorList[beaconId]["payload"] = blePayload

                # generates a presence True Dict (updated data beacon)
                sensorDict = {"sensors":[self.beaconDataToDict(blePayload, True)]}
                
                return sensorDict
        
        # if this beacon isn't in the dictionary...
        else:
            self.sensorList[beaconId]={"time": time.time(), "payload": blePayload}
            # generates a presence True Dict (new beacon)
            sensorDict = {"sensors":[self.beaconDataToDict(blePayload, True)]}

            return sensorDict

    # Check if some beacon info is timed out. This will return "sensors" dictionary
    def purge (self, beaconThreshold):

        beaconIdRemoveList = []

        # looking for timed out beacons
        for beaconId in self.sensorList.keys():
            if (time.time()-self.sensorList[beaconId]["time"] > beaconThreshold):
                beaconIdRemoveList.append (beaconId)
        
        # if there are elements to remove...
        if len(beaconIdRemoveList) > 0:
            # generates a presence False Dict (old beacon)
            sensorDict = self.beaconIdListToDict (beaconIdRemoveList, False)
            return sensorDict

        else:
            # send exception: Empty Dict
            raise ValueError("Empty")


    # this will be called only from purge functions
    def beaconIdListToDict ( self, beaconIdList, presence ):

        beaconDataParsed = {"sensors":[]}

        for beaconId in beaconIdList:
            beaconData = self.sensorList[beaconId]["payload"]
            beaconDataParsed["sensors"].append (self.beaconDataToDict(beaconData, presence))
            if (presence == False):
                self.sensorList.pop(beaconId)

        return beaconDataParsed


    def beaconDataToDict ( self, beaconData, presence ):

        beaconDataParsed = {}

        beaconType = int(beaconData[16:18])

        if beaconType == self.beaconTypeIdentifiers["trafficSignBeaconId"]:
            beaconDataParsed["presence"] = presence
            beaconDataParsed["type"] = beaconType
            beaconDataParsed["lat"] = struct.unpack('!f',bytes.fromhex(beaconData[0:8]))[0]
            beaconDataParsed["lon"] = struct.unpack('!f',bytes.fromhex(beaconData[8:16]))[0]
            beaconDataParsed["id"] = beaconData[0:8]+beaconData[8:16]
            beaconDataParsed["specificData"] = {}
            beaconDataParsed["specificData"]["trafficSign"] = int(beaconData[18:20])
        
        elif beaconType == self.beaconTypeIdentifiers["roadStateBeaconId"]:
            beaconDataParsed["presence"] = presence
            beaconDataParsed["type"] = beaconType
            beaconDataParsed["lat"] = struct.unpack('!f',bytes.fromhex(beaconData[0:8]))[0]
            beaconDataParsed["lon"] = struct.unpack('!f',bytes.fromhex(beaconData[8:16]))[0]
            beaconDataParsed["id"] = beaconData[0:8]+beaconData[8:16]
            beaconDataParsed["specificData"] = {}
            beaconDataParsed["specificData"]["roadState"] = int(beaconData[18:20])

        elif beaconType == self.beaconTypeIdentifiers["bicycleBeaconId"]:
            beaconDataParsed["presence"] = presence
            beaconDataParsed["type"] = beaconType
            beaconDataParsed["lat"] = None
            beaconDataParsed["lon"] = None
            beaconDataParsed["id"] = beaconData[0:8]+beaconData[8:16]
            beaconDataParsed["specificData"] = {}
            beaconDataParsed["specificData"]["bicycleState"] = int(beaconData[18:20])

        elif beaconType == self.beaconTypeIdentifiers["seatBeaconId"]:
            beaconDataParsed["presence"] = presence
            beaconDataParsed["type"] = beaconType
            beaconDataParsed["lat"] = None
            beaconDataParsed["lon"] = None
            beaconDataParsed["id"] = beaconData[0:8]+beaconData[8:16]
            beaconDataParsed["specificData"] = {}
            beaconDataParsed["specificData"]["kidPresence"] = int(beaconData[18:20])
            beaconDataParsed["specificData"]["lockState"] = int(beaconData[20:22])

        elif beaconType == self.beaconTypeIdentifiers["intelligentTrafficLightBeaconId"]:
            print ("intelligentTraffic")
        elif beaconType == self.beaconTypeIdentifiers["infoPanelBeaconId"]:
            print ("infoPanel")
        elif beaconType == self.beaconTypeIdentifiers["pedestrianBeaconId"]:
            print ("pedestrian")
        elif beaconType == self.beaconTypeIdentifiers["slowVehicleBeaconId"]:
            print ("slowVehicle")
        elif beaconType == self.beaconTypeIdentifiers["emergencyVehicleBeaconId"]:
            print ("emergencyVehicleBeacon")

        return beaconDataParsed
