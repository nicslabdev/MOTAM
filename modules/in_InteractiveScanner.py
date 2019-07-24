#! /usr/bin/python3

#########################################################
# Python3 module for simulating BLE scanner (both BLE4  #
# and BLE5) in real time.                               #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import threading
import struct
from modules import SensorStore

class InteractiveScanner:

    def __init__ (self, threadStopEvent, beaconsQueue, beaconThreshold, coordinates):
        self.threadStopEvent = threadStopEvent                          # Event from main thread in order to stop all threads
        self.beaconsQueue = beaconsQueue
        self.sensorStore = SensorStore.SensorStore()
        self.beaconThreshold = beaconThreshold                          # Seconds after the beacon will be removed from list
        
        self.dataBeaconSamples = {
            1: ("Sillita sentado sin abrochar", "0400010002000300040100"),
            2: ("Sillita sentado abrochado", "0400010002000300040101"),
            3: ("Sillita sin sentar no abrochado", "0400010002000300040000"),
            4: ("Semáforo normal rojo",  "014212DDEDC09004EC0118000A00"),
            5: ("Semáforo normal ambar", "014212DDEDC09004EC0118000A01"),
            6: ("Semáforo normal verde", "014212DDEDC09004EC0118000A02"),
            7: ("Semáforo int rojo 16s",  "054212dd41c08fee72010e005a0010"),
            8: ("Semáforo int ambar 5s",  "054212dd41c08fee72010e005a0105"),
            9: ("Semáforo int verde 29s",  "054212dd41c08fee72010e005a02s1D"),
            10: ("Carretera seca", "024212DD69C08FF46901"),
            11: ("Carretera mojada", "024212DD69C08FF46902"),
            12: ("Carretera nieve", "024212DD69C08FF46903"),
            13: ("Bicicleta en movimiento", "03000100020003000402"),
            14: ("Bicicleta accidentada", "03000100020003000403")
            # 14: ("infoPanel Incendio", "01"),
            # 15: ("infoPanel Carrera ciclista", "01"),
            # 16: ("Peatón cerca", "01"),
            # 17: ("Vehículo lento", "01"),
            # 18: ("Vehículo de emergencia", "01")
        }

        # Check if new coordinates has been given
        if len(coordinates) is 2:
            newLat = str(hex(struct.unpack('<I', struct.pack('<f', coordinates[0]))[0])).split('x')[1].upper()
            newLon = str(hex(struct.unpack('<I', struct.pack('<f', coordinates[1]))[0])).split('x')[1].upper()

            for element in self.dataBeaconSamples:
                newBeaconData = newLat + newLon + self.dataBeaconSamples[element][1][16:]
                self.dataBeaconSamples[element] = (self.dataBeaconSamples[element][0],newBeaconData)

    def run (self):
        interactiveThread = threading.Thread(target=self.terminalInputOutput)
        interactiveThread.daemon = True
        interactiveThread.start()
        self.purgeStartTimer ( )
        return interactiveThread

    def terminalInputOutput (self):
        while not self.threadStopEvent.is_set():
            print ("List of beacon samples:")
            print ("ID - Beacon frame - Name\r\n")
            for dataBeaconIndex in self.dataBeaconSamples:
                print (" ", dataBeaconIndex, "-", self.dataBeaconSamples[dataBeaconIndex][1], "-", self.dataBeaconSamples[dataBeaconIndex][0] )
            try:
                index = int(input("\r\nSelect the beacon sample ID: "))
                if index > 0 and index <= len(self.dataBeaconSamples):
                    beaconDict = self.sensorStore.add(self.dataBeaconSamples[index][1])
                    self.beaconsQueue.put(beaconDict)
                else:
                    print ("\r\n  :Invalid value\r\n")

            except ValueError as err:
                pass

    def purgeStartTimer ( self ):
        # check if there are beacons to purge every x seconds
        if not self.threadStopEvent.is_set():
            threading.Timer(0.1, self.purgeStartTimer).start()
            try:
                beaconDict = self.sensorStore.purge(self.beaconThreshold)
                self.beaconsQueue.put(beaconDict)
            except ValueError as err:
                pass