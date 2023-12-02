import numpy as np
import random
import math
import time




def debug(msg):
    print("[DEBUG] - ", end="")
    print(msg)

class Genetic():

    def __init__(self):
        self.actualMinValue = np.inf
        self.globalCount = 0

    def matrixForm(self,x):
        return x.reshape(3,2)

    def arrayForm(self,x):
        return x.ravel()

    def f(self,x):#TODO: Change
        return (130*x[0] + 300*x[1] + 140*x[2] + 120*x[3] + 150*x[4] + 270*x[5])

    def applyPenalties(self,indiv):
        x = self.matrixForm(indiv['genome'])
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
            
    def adaptToDemandRestriction(self,indiv):
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
    def generateInitialPopulation(self,popSize):
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
        population = self.calculateFitnessValues(population)
        return population


    def calculateFitnessValues(self,population):
        for individual in population:
            individual['fitness'] = self.f(individual['genome']) 
            individual['penaltiesApplied'] = self.applyPenalties(individual)
        return population

    def selectIndividuals(self,population):
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

    def crossover(self,parents):
        willCrossover = (random.random() < 0.7)
        childrenGenomes = parents.copy()
        #CrossOverLogic
        if willCrossover:
            for _ in range(3):
                elementToSwitch = random.randint(0,len(childrenGenomes[0])-1)
                childrenGenomes[0][elementToSwitch] = childrenGenomes[1][elementToSwitch]
        return childrenGenomes

    def mutate(self,childrenGenomes):
        willMutate = (random.random() < 0.1)
        mutatedChildrenGenome = childrenGenomes
        if not willMutate:
            return childrenGenomes
        elementToMutate = random.randint(0,len(childrenGenomes[0])-1)
        mutatedChildrenGenome[0][elementToMutate] -= childrenGenomes[0][elementToMutate]*0.05
        mutatedChildrenGenome[1][elementToMutate] -= childrenGenomes[0][elementToMutate]*0.05
        return [self.adaptToDemandRestriction(child) for child in mutatedChildrenGenome]

    def mutateAndCrossover(self,si):
        for index in range(0,len(si),2):
            parentGenomes = [ si[index]['genome'] , si[index + 1]['genome'] ]
            crossedOverChildrenGenomes = self.crossover(parentGenomes)
            mutatedChildrenGenomes = self.mutate(crossedOverChildrenGenomes)

            for childGenome in mutatedChildrenGenomes:
                child = {
                'genome': childGenome,
                'fitness': -1,
                'rank': -1,
                'penaltiesApplied': -1
                }
                si.append(child)
        return si

    def generateNextPopulation(self,previousPopulation):
        selectedIndividuals = self.selectIndividuals(previousPopulation)
        newPopulation = self.mutateAndCrossover(selectedIndividuals)
        newPopulation = self.calculateFitnessValues(newPopulation)
        fitnessData = sorted([(indiv['penaltiesApplied'], indiv['fitness'] ) for indiv in newPopulation]) # change
        return (newPopulation, fitnessData)


    def checkForResult(self,fitnessData):
        for fd in fitnessData:
            penaltiesApplied,fitnessValue = fd
            if(penaltiesApplied == 0):
                if fitnessValue > (self.actualMinValue*0.99) and fitnessValue < (self.actualMinValue*1.01):
                    self.globalCount+=1
                elif fitnessValue < self.actualMinValue:
                    self.actualMinValue = fitnessValue
                    self.globalCount = 0
                
                if self.globalCount == 3:
                    return (True, self.actualMinValue)
            
        return (False, None)

    def run(self):
        maxGenerations = 2000
        converged = False
        population = self.generateInitialPopulation(100)
        generation = 0
        while not converged and generation < maxGenerations:
            population, fitnessData = self.generateNextPopulation(population)
            converged, answer = self.checkForResult(fitnessData)      
            generation+=1 
        debug(answer)


g = Genetic()
g.run()
