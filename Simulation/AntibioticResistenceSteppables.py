
from PySteppables import *
import CompuCell
import sys
import random

DAMAGE_FACTOR = 0.1 #.4535
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
        # print "INSIDE MITOSIS STEPPABLE"
        cells_to_divide=[]
        for cell in self.cellList:
            if cell.volume>50:
                
                cells_to_divide.append(cell)
                
        for cell in cells_to_divide:
            # to change mitosis mode leave one of the below lines uncommented
            self.divideCellRandomOrientation(cell)
            # self.divideCellOrientationVectorBased(cell,1,0,0)                 # this is a valid option
            # self.divideCellAlongMajorAxis(cell)                               # this is a valid option
            # self.divideCellAlongMinorAxis(cell)                               # this is a valid option

    def updateAttributes(self):
        self.parentCell.targetVolume /= 2.0 # reducing parent target volume                 
        self.cloneParent2Child()            
        parentARF = CompuCell.getPyAttrib(self.parentCell)["ARF"]
        childDict = CompuCell.getPyAttrib(self.childCell)
        childDict["ARF"] = parentARF + ((random.gauss(0.5, 0.17) - 0.5) * 0.1) # child cell slightly mutates ARF 
        # for more control of what gets copied from parent to child use cloneAttributes function
        # self.cloneAttributes(sourceCell=self.parentCell, targetCell=self.childCell, no_clone_key_dict_list = [attrib1, attrib2] )
        
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
                    #cellDict["ARF"] = 0.5
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
                

        
    def finish(self):
        # this function may be called at the end of simulation - used very infrequently though
        return
    
