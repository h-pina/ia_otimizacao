import numpy as np
import random
import math
import time

DEBUG = False
POPSIZE  = 100
GLOBAL_MIN = -106.764537
GLOBAL_MAX = 170
PRECISION_THRESHOLD = 0.05
actualMinimalValue = 50000000


#Remap x to array form



def debug(msg):
    print("[DEBUG] - ", end="")
    print(msg)

#Not sure if I`ll use it`
def matrixForm(x):
    return x.reshape(3,2)

def arrayForm(x):
    return x.ravel()

def f(x):#TODO: Change
    return (130*x[0] + 300*x[1] + 140*x[2] + 120*x[3] + 150*x[4] + 270*x[5])

def applyPenalties(indiv):
    x = matrixForm(indiv['genome'])
    offerRestrictions = [x[0][0] + x[0][1] <= 4330, 
                         x[1][0] + x[1][1] <= 2150, 
                         x[2][0] + x[2][0] <= 7820]
    demandRestrictions = [x[0][0] + x[1][0] + x[2][0] == 4210, 
                          x[0][1] + x[1][1] + x[2][1] ==  6910]
    nonZeroRestriction =  all([el>0 for el in indiv['genome']])
    
    penaltiesCount = 0
    for restriction in offerRestrictions:
        if restriction == False:
            penaltiesCount+=1
    for restriction in demandRestrictions:
        if restriction == False:
            penaltiesCount+=1
    if nonZeroRestriction == False:
        penaltiesCount+=1
    return penaltiesCount
        
def adaptToDemandRestriction(indiv):
    a = [indiv[el] for el in range(len(indiv)) if el%2 == 0]
    if(sum(a) != 4210):
        indexOfMinimalElement = a.index(min(a))
        a[indexOfMinimalElement] += 4210 - sum(a)
    b = [ indiv[el] for el in range(len(indiv)) if el%2 != 0]
    if(sum(b) != 6910):
        indexOfMinimalElement = b.index(min(b))
        b[indexOfMinimalElement] += 6910 - sum(b)
    
    return np.array([a[0],b[0],a[1],b[1],a[2],b[2]])

#Geracao da populacao inicial, partindo de numeros aleatorios dentro do range [-10,10]
def generateInitialPopulation(popSize):
    population = []
    for _ in range(popSize):
        l = [random.random(),random.random(),random.random()]
        l = [l[0]/sum(l),l[1]/sum(l),l[2]/sum(l)]
        genome = np.array([ l[0]*4210, l[0]*6910, l[1]*4210, l[1]*6910, l[2]*4210, l[2]*6910 ])
        individual = {
            'genome': genome,  
            'fitness': -1,
            'rank': -1,
            'penaltiesApplied': -1
        }
        
        population.append(individual)
    population = calculateFitnessValues(population)
    return population


def calculateFitnessValues(population):
    for individual in population:
        individual['fitness'] = f(individual['genome']) 
        individual['penaltiesApplied'] = applyPenalties(individual)
    return population

def selectIndividuals(population):
    sortedPopulation = sorted(population, key=lambda x: (x['penaltiesApplied'],x['fitness']),)
    
    sumOfRanks = ( len(sortedPopulation) * (1 + len(sortedPopulation)) ) / 2
    rankPosition = 1
    pieSection = 0
    for indiv in sortedPopulation:
        pieSection += rankPosition/sumOfRanks
        indiv['rank'] = pieSection
        rankPosition+=1
    
    selectedIndividuals = []
    for _ in range(len(sortedPopulation)//2):
        thresholdForSelection = random.random()
        selectedIndividual = next((x for x in sortedPopulation if x['rank'] > thresholdForSelection))
        selectedIndividuals.append(selectedIndividual)
    
    return selectedIndividuals

def crossover(parents):
    willCrossover = (random.random() < 0.7)
    childrenGenomes = parents.copy()
    #CrossOverLogic
    if willCrossover:
        for _ in range(3):
            elementToSwitch = random.randint(0,len(childrenGenomes[0])-1)
            childrenGenomes[0][elementToSwitch] = childrenGenomes[1][elementToSwitch]
    return childrenGenomes

def mutate(childrenGenomes):
    willMutate = (random.random() < 0.1)
    mutatedChildrenGenome = childrenGenomes
    if not willMutate:
        return childrenGenomes
    elementToMutate = random.randint(0,len(childrenGenomes[0])-1)
    mutatedChildrenGenome[0][elementToMutate] -= childrenGenomes[0][elementToMutate]*0.05
    mutatedChildrenGenome[1][elementToMutate] -= childrenGenomes[0][elementToMutate]*0.05
    return [adaptToDemandRestriction(child) for child in mutatedChildrenGenome]

def mutateAndCrossover(si):
    for index in range(0,len(si),2):
        parentGenomes = [ si[index]['genome'] , si[index + 1]['genome'] ]
        crossedOverChildrenGenomes = crossover(parentGenomes)
        mutatedChildrenGenomes = mutate(crossedOverChildrenGenomes)

        for childGenome in mutatedChildrenGenomes:
            child = {
            'genome': childGenome,
            'fitness': -1,
            'rank': -1,
            'penaltiesApplied': -1
            }
            si.append(child)
    return si

def generateNextPopulation(previousPopulation):
    selectedIndividuals = selectIndividuals(previousPopulation)
    newPopulation = mutateAndCrossover(selectedIndividuals)
    newPopulation = calculateFitnessValues(newPopulation)
    fitnessData = sorted([indiv['penaltiesApplied'] for indiv in newPopulation]) # change
    return (newPopulation, fitnessData)


def checkForResult(data):
    for fd in data:
        if fd == 0:
            return True
    return False

def run():
    maxGenerations = 2000
    converged = False
    population = generateInitialPopulation(100)
    generation = 0
    while not converged:
        population, fitnessData = generateNextPopulation(population)
        converged = checkForResult(fitnessData)
        debug(fitnessData)        
        generation+=1 
        debug(generation)

run()
