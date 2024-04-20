import json
import os
import random

import strategy_text_generator

from user_data.strategies.diamond_strategy import Diamond


def generate_initial_population(parameters, population_size):
    # pass low and high values as parameters, then define default as a number from low to high
    # low and high values are inside parameters
    population = []
    for i in range(population_size):
        candidate = {}
        for j in range(len(parameters)):
            candidate[parameters[j][0]] = {}
            if parameters[j][1] == 'int':
                candidate[parameters[j][0]]['type'] = 'int'
                candidate[parameters[j][0]]['default'] = random.randint(candidate[parameters[j][0]]['low'],
                                                                        candidate[parameters[j][0]]['high'])
            elif parameters[j][1] == 'float':
                candidate[parameters[j][0]]['type'] = 'float'
                candidate[parameters[j][0]]['default'] = random.uniform(candidate[parameters[j][0]]['low'],
                                                                        candidate[parameters[j][0]]['high'])
                candidate[parameters[j][0]]['decimals'] = random.randint(0, round(
                    100000 / candidate[parameters[j][0]]['high']))
        population.append(candidate)
    return population


def evaluate_candidate(candidate_class, loss_function):
    # TODO: multiple backtests on multiple classes per 1 call (for whole population)
    os.system(
        f"docker compose run --rm freqtrade backtesting --strategy NewDiamond --timerange 20230101-20240405")
    # wait until file is created
    while not os.path.exists("user_data/backtest_results/.last_result.json"):
        pass
    with open("user_data/backtest_results/.last_result.json", "r") as file:
        filename = json.load(file)['latest_backtest']
    os.remove("user_data/backtest_results/.last_result.json")

    with open(f"user_data/backtest_results/{filename}", "r") as file:
        profit = None
        for line in file:
            obj = json.loads(line.strip())
            profit = obj.get('profit_total')
    os.remove(f"user_data/backtest_results/{filename}")

    if profit:
        return profit
    else:
        print("No profit found in backtest results!")
        return float('inf')


# def mutate_candidate(candidate):
#     # TODO: pass low and high values as parameters, then define default as a number from low to high
#     mutated_candidate = dict(candidate)
#     for key in mutated_candidate.keys():
#         if type(mutated_candidate[key]) is dict:
#             if 'low' in mutated_candidate[key].keys():
#                 mutated_candidate[key]['low'] = random.randint(0, 10000)
#             if 'high' in mutated_candidate[key].keys():
#                 mutated_candidate[key]['high'] = random.randint(0, 100000)
#             if 'default' in mutated_candidate[key].keys():
#                 mutated_candidate[key]['default'] = random.randint(0, 10000)
#             if 'decimals' in mutated_candidate[key].keys():
#                 mutated_candidate[key]['decimals'] = random.randint(0, round(100000 / mutated_candidate[key]['high']))
#     return mutated_candidate

def mutate_candidate(candidate):
    # pass low and high values as parameters, then define default as a number from low to high
    mutated_candidate = dict(candidate)
    for key in mutated_candidate.keys():
        if type(mutated_candidate[key]) is dict:
            if 'default' in mutated_candidate[key].keys():
                if mutated_candidate[key]['type'] == 'int':
                    mutated_candidate[key]['default'] = random.randint(mutated_candidate[key]['low'],
                                                                       mutated_candidate[key]['high'])
                elif mutated_candidate[key]['type'] == 'float':
                    mutated_candidate[key]['default'] = random.uniform(mutated_candidate[key]['low'],
                                                                       mutated_candidate[key]['high'])
            if 'decimals' in mutated_candidate[key].keys():
                mutated_candidate[key]['decimals'] = random.randint(0, round(
                    100000 / mutated_candidate[key]['high']))

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


def genetic_algorithm(parameters, population_size, generations, loss_function, strategy_class='Diamond'):
    # add class
    population = generate_initial_population(parameters, population_size)
    for i in range(generations):
        for j, candidate in enumerate(population):
            population[j]['loss'] = evaluate_candidate(strategy_text_generator.generate_text(strategy_class, candidate),
                                                       loss_function)
        population = sorted(population, key=lambda x: x['loss'])
        for j in range(len(population)):
            population[j].pop('loss')
        if i == generations - 1:
            return population[0]
        new_population = []
        for j in range(population_size // 2):
            new_population.append(population[j])
            new_population.append(mutate_candidate(population[j]))
            new_population.append(crossover_candidates(population[j], population[j + 1]))
        population = new_population


if __name__ == "__main__":
    # TODO: params as console params
    parameters = [
        ('buy_volumeAVG', 'int'),
        ('buy_rsi', 'float')
    ]
    best_candidate = genetic_algorithm(parameters, 3, 2, 'SharpeHyperOptLoss')
    print('Final result:')
    print(best_candidate)
