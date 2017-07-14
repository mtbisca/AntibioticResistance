
import sys
from os import environ
from os import getcwd
import string

sys.path.append(environ["PYTHON_MODULE_PATH"])


import CompuCellSetup


sim,simthread = CompuCellSetup.getCoreSimulationObjects()
        
# add extra attributes here
        
CompuCellSetup.initializeSimulationObjects(sim,simthread)
# Definitions of additional Python-managed fields go here
        
#Add Python steppables here
steppableRegistry=CompuCellSetup.getSteppableRegistry()
        

from AntibioticResistenceSteppables import ConstraintInitializerSteppable
ConstraintInitializerSteppableInstance=ConstraintInitializerSteppable(sim,_frequency=1)
steppableRegistry.registerSteppable(ConstraintInitializerSteppableInstance)
        

from AntibioticResistenceSteppables import GrowthSteppable
GrowthSteppableInstance=GrowthSteppable(sim,_frequency=1)
steppableRegistry.registerSteppable(GrowthSteppableInstance)
        

from AntibioticResistenceSteppables import MitosisSteppable
MitosisSteppableInstance=MitosisSteppable(sim,_frequency=1)
steppableRegistry.registerSteppable(MitosisSteppableInstance)
        
        

from AntibioticResistenceSteppables import DamageCalculatorSteppable
instanceOfDamageCalculatorSteppable=DamageCalculatorSteppable(_simulator=sim,_frequency=1)
steppableRegistry.registerSteppable(instanceOfDamageCalculatorSteppable)

CompuCellSetup.mainLoop(sim,simthread,steppableRegistry)
        
        