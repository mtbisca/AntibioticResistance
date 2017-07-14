
from PySteppables import *
import CompuCell
import sys
import random


DAMAGE_FACTOR = 0.6 # if <4 no effect if 4<<5 barrier forms if 6> red cells only
GROWTH_FACTOR = 1

from PySteppablesExamples import MitosisSteppableBase

          

class ConstraintInitializerSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def start(self):
        for cell in self.cellList:
            cell.targetVolume=25
            cell.lambdaVolume=2.0
        

        

class GrowthSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
    def step(self,mcs):
        for cell in self.cellList:
            cell.targetVolume+= 1 * GROWTH_FACTOR      
      
        

class MitosisSteppable(MitosisSteppableBase):
    def __init__(self,_simulator,_frequency=1):
        MitosisSteppableBase.__init__(self,_simulator, _frequency)
    
    def step(self,mcs):
        cells_to_divide=[]
        for cell in self.cellList:
            if cell.volume>50:
                
                cells_to_divide.append(cell)
                
        for cell in cells_to_divide:
            self.divideCellRandomOrientation(cell)

    def updateAttributes(self):
        self.parentCell.targetVolume /= 2.0 # reducing parent target volume                 
        self.cloneParent2Child()            
        parentARF = CompuCell.getPyAttrib(self.parentCell)["ARF"]
        childDict = CompuCell.getPyAttrib(self.childCell)
        childDict["ARF"] = parentARF + ((random.gauss(0.5, 0.17) - 0.5) * 0.1) # child cell slightly mutates ARF 
        
        if childDict["ARF"] >= 0.8:
            self.childCell.type = self.RESISTENTBACTERIA
        else:
            self.childCell.type = self.REGULARBACTERIA
        
        
        
from PlayerPython import *
import CompuCellSetup
from math import *


class DamageCalculatorSteppable(SteppableBasePy):
    def __init__(self,_simulator,_frequency=1):
        SteppableBasePy.__init__(self,_simulator,_frequency)
        
    def start(self):
        for cell in self.cellList:
            if cell.type != self.MEDIUM:
                cellDict=CompuCell.getPyAttrib(cell)
                cellDict["Damage"] = 0
                
                cellDict["ARF"] = random.gauss(0.5,0.17) # normally distributed within roughly within 0 and 1
                if cellDict["ARF"] < 0:
                    cellDict["ARF"] = 0
                elif cellDict["ARF"] > 1:
                    cellDict["ARF"] = 1
                
                if cellDict["ARF"] >= 0.8:
                    cell.type = self.RESISTENTBACTERIA
                else:
                    cell.type = self.REGULARBACTERIA
                
    
    def step(self,mcs):
        antibioticField=CompuCell.getConcentrationField(self.simulator,'Antibiotic')
        for cell in self.cellList:
            if cell.type != self.MEDIUM:
                # get concentration at cells COM
                cellCOM = CompuCell.Point3D()
                cellCOM.x=int(round(cell.xCOM))
                cellCOM.y=int(round(cell.yCOM))
                cellCOM.z=int(round(cell.zCOM))   
                antibioticConcentration = antibioticField.get(cellCOM)
                
                # calculate damage based on concentration and ARF
                cellDict=CompuCell.getPyAttrib(cell)
                cellDict["Damage"] += (1 - cellDict["ARF"]) * antibioticConcentration * DAMAGE_FACTOR
                if cellDict["Damage"] >= 1: # too much damage -> die
                        cell.targetVolume=0
                        cell.lambdaVolume=100
                
    
