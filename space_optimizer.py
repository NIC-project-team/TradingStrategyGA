import json
import os
import random


def generate_initial_population(parameters, population_size):
    population = []
    # parameters = [['buy_volumeAVG', 'int'], ['buy_rsi', 'float']]
    for i in range(population_size):
        candidate = {}
        for j in range(len(parameters)):
            candidate[parameters[j][0]] = {}
            if parameters[j][1] == 'int':
                candidate[parameters[j][0]]['type'] = 'int'
                candidate[parameters[j][0]]['low'] = random.randint(0, 10000)
                candidate[parameters[j][0]]['high'] = random.randint(0, 100000)
                candidate[parameters[j][0]]['default'] = random.randint(0, 10000)
            elif parameters[j][1] == 'float':
                candidate[parameters[j][0]]['type'] = 'float'
                candidate[parameters[j][0]]['low'] = random.uniform(0, 10000)
                candidate[parameters[j][0]]['high'] = random.uniform(0, 100000)
                candidate[parameters[j][0]]['default'] = random.uniform(0, 10000)
                candidate[parameters[j][0]]['decimals'] = random.randint(0, round(
                    100000 / candidate[parameters[j][0]]['high']))
        population.append(candidate)
    return population


def evaluate_candidate(candidate_class, loss_function):
    loss = 0
    os.system(f"docker compose run --rm freqtrade hyperopt --strategy {candidate_class} --hyperopt-loss {loss_function} --spaces all -e 10")
    with open("/user_data/hyperopt_results/.last_result.json", "r") as file:
        filename = json.load(file)['latest_hyperopt']
    with open(f"/user_data/hyperopt_results/{filename}", "r") as file:
        result = json.load(file)
        for i in range(len(result) - 1, -1, -1):
            if result[i]['is_best']:
                if 'loss' in result[i].keys():
                    loss = result[i]['loss']
                else:
                    raise Exception("Loss not found in hyperopt result")
                break
    return loss


def mutate_candidate(candidate):
    mutated_candidate = candidate
    for key in mutated_candidate.keys():
        if type(mutated_candidate[key]) == dict:
            if 'low' in mutated_candidate[key].keys():
                mutated_candidate[key]['low'] = random.randint(0, 10000)
            if 'high' in mutated_candidate[key].keys():
                mutated_candidate[key]['high'] = random.randint(0, 100000)
            if 'default' in mutated_candidate[key].keys():
                mutated_candidate[key]['default'] = random.randint(0, 10000)
            if 'decimals' in mutated_candidate[key].keys():
                mutated_candidate[key]['decimals'] = random.randint(0, round(100000 / mutated_candidate[key]['high']))
    return mutated_candidate


def crossover_candidates(candidate1, candidate2):
    crossover_point = random.randint(0, len(candidate1.keys()))
    new_candidate = {}
    for i, key in enumerate(candidate1.keys()):
        if i < crossover_point:
            new_candidate[key] = candidate1[key]
        else:
            new_candidate[key] = candidate2[key]
    return new_candidate


def genetic_algorithm(parameters, population_size, generations, loss_function):
    # TODO: add class
    population = generate_initial_population(parameters, population_size)
    for i in range(generations):
        for j in range(len(population)):
            population[j]['loss'] = evaluate_candidate(get_class(population[j]), loss_function)
        population = sorted(population, key=lambda x: x['loss'])
        new_population = []
        for j in range(population_size // 2):
            new_population.append(population[j])
            new_population.append(mutate_candidate(population[j]))
            new_population.append(crossover_candidates(population[j], population[j + 1]))
        population = new_population
    return population[0]
