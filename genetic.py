import numpy as np
import random
import math
import time

DEBUG = False
POPSIZE  = 100
GLOBAL_MIN = -106.764537
GLOBAL_MAX = 170
PRECISION_THRESHOLD = 0.05

def debug(msg):
    print("[DEBUG] - ", end="")
    print(msg)

def f(x11,x12,x21,x22,x31,x32):#TODO: Change
    return (130*x11 + 300*x12 + 140*x21 + 120*x22 + 150*x31 + 270*x32)

def isWithinRestrictions(x11,x12,x21,x22,x31,x32):
    offerRestrictions = all([x11 + x12 <= 4330, x21 + x22 <= 2150, x31 + x32 <= 7820])
    demandRestrictions = all([x11 + x21 + x31 == 4210, x12 + x22 + x32 ==  6910])
    nonZeroRestriction = all(x>0 for x in (x11,x12,x21,x22,x31,x32))
    return offerRestrictions and demandRestrictions and nonZeroRestriction

#Geracao da populacao inicial, partindo de numeros aleatorios dentro do range [-10,10]
def generateInitialPopulation(popSize, upperLimit, lowerLimit):
    x = []
    done = False
    while not done:
        localX = []
        localX.append(random.uniform(lowerLimit,upperLimit))
        localX.append(random.uniform(lowerLimit,upperLimit))
        localX.append(random.uniform(lowerLimit,upperLimit))
        localX.append(random.uniform(lowerLimit,upperLimit))
        localX.append(random.uniform(lowerLimit,upperLimit))
        localX.append(random.uniform(lowerLimit,upperLimit))
        if(isWithinRestrictions(*localX)):
            return localX
    return x

#Aplica o ranking linear
def linearRanking(population,maxRank,minRank):
    population.sort(key= lambda x : x[2]) # ordenacao da populacao
    ranks = [] 

    #inicializacao das variaveis para o rankeamento
    N = len(population)
    min = minRank
    max = maxRank
    totalSum = 0

    #calculo dos ranks (nesse caso, de 0 a 100)
    for index in range(len(population)): 
        value = min + (max - min)/(N-1) * (N-index)
        totalSum  += value
        ranks.append(value)
    accSum = 0

    #normalizacao
    for j in range(len(ranks)): 
        normalizedRank = ranks[j]/totalSum
        accSum+=normalizedRank
        population[j][3] = accSum    
    return population 

#Com o preenchimento dos ranks na funcao linearRank, rodar a roleta e selecionar
#o numero de membros definido por membersToSelect
def roullete(population,membersToSelect):
    selected = []
    for i in range(membersToSelect):
        num = random.random()
        selected.append(next(e for e in population if e[3]>num))
    return [ [s[0],s[1],s[2],-1] for s in selected]

#realizar crossover
def crossover(parent1, parent2):
    factor = random.random()
    if factor > 0.7:
        return [parent1[0],parent1[1],-1], [parent2[0],parent2[1]]
    return [parent1[0], parent2[1],-1], [ parent2[0], parent1[1]]

#mutacao dos filhos (filhos podem ser os proprios pais, quando nao houver crossover)
def mutate(child1, child2):
    multiplier = random.choice([1,-1])
    child1 = [child1[0] + multiplier*random.uniform(0,2),child1[1] + multiplier*random.uniform(0,2)]
    child2 = [child2[0] + multiplier*random.uniform(0,2),child2[1] + multiplier*random.uniform(0,2)]
    child1.extend([f(child1[0],child1[1]),-1])
    child2.extend([f(child2[0],child2[1]),-1])
    return child1, child2

#Obtencao das novas populacoes, aplicando crossover e mutacoes apos a roleta
def getNewPopulation(population):
    newPop = []
    for i in range(0,len(population), 2):
        parent1 = population[i]
        parent2 = population[i+1]        
        child1, child2 = crossover(parent1,parent2)
        child1, child2 = mutate(child1, child2)
        newPop.extend([parent1,parent2,child1,child2])
        #restricoes
        #gerar novos
    return newPop

#Validacao da nova populacao
def checkForResult(group, expectedValue, threshold):
    acceptedValueMargins = [expectedValue-threshold, expectedValue+threshold]
    for g in group:
        if g[2] > acceptedValueMargins[0] and g[2]<acceptedValueMargins[1]:
            return True, g
    return False, []

if __name__ == "__main__":
    # #inicializacao das variaveis
    # poplation = generateInitialPopulation(POPSIZE, 10,-10)
    # done = False
    # result = []
    # generationCount = 0

    # #loop principal
    # while done is False:
    #     generationCount+=1
    #     population = linearRanking(population,100,0)
    #     selectedMembers = roullete(population,50)
    #     population = getNewPopulation(selectedMembers)
    #     done, result = checkForResult(population, GLOBAL_MIN, PRECISION_THRESHOLD)

    # #Resultados
    # print(f'Coordenadas Encontradas - x: {result[0]} | y: {result[1]}')
    # print(f'Numero de geracoes {generationCount}')
    st = time.time()
    debug(generateInitialPopulation(100,0,10000))
    debug(time.time() - st)

