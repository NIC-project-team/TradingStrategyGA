import json
import os
import random
import copy

import strategy_text_generator

from user_data.strategies.diamond_strategy import Diamond


def generate_random_high_low_values(parameters):
    # generate random high and low values for each parameter
    # TODO: change values to needed fix values
    new_parameters = {}
    for i in range(len(parameters)):
        new_parameters[parameters[i][0]] = {}
        new_parameters[parameters[i][0]]['type'] = parameters[i][1]
        new_parameters[parameters[i][0]]['low'] = random.randint(0, 10000)
        new_parameters[parameters[i][0]]['high'] = random.randint(0, 100000)
    return new_parameters


def generate_initial_population(parameters, population_size):
    # for each parameter, generate random value between low and high ('default' value)
    population = []
    for i in range(population_size):
        candidate = {}
        for key in parameters.keys():
            candidate[key] = {}
            if parameters[key]['type'] == 'int':
                candidate[key]['type'] = parameters[key]['type']
                candidate[key]['low'] = parameters[key]['low']
                candidate[key]['high'] = parameters[key]['high']
                candidate[key]['space'] = parameters[key]['space']
                candidate[key]['default'] = random.randint(parameters[key]['low'], parameters[key]['high'])
            elif parameters[key]['type'] == 'float':
                candidate[key]['type'] = parameters[key]['type']
                candidate[key]['low'] = parameters[key]['low']
                candidate[key]['high'] = parameters[key]['high']
                candidate[key]['space'] = parameters[key]['space']
                candidate[key]['default'] = random.uniform(parameters[key]['low'], parameters[key]['high'])
                candidate[key]['decimals'] = parameters[key]['decimals']
        population.append(candidate)
    return population


def generate_strategy_text_population(strategy_class, population):
    # for example, generate NewDiamond1, NewDiamond2, NewDiamond3, ... files from Diamond strategy and population values
    # text file name is new_strategy_name + str(i) + '.py'
    # strategy class is NewStrategyName + i
    for i, candidate in enumerate(population):
        with open(f"user_data/strategies/new_{strategy_class}{i}.py", "w") as file:
            text, filename = strategy_text_generator.generate_text(strategy_class, candidate, i)
            file.write(text)
    return f"user_data/strategies/new_{strategy_class}.py"


def evaluate_population(population, classname):
    # evaluate NewDiamond1, NewDiamond2, NewDiamond3, ... using 1 call
    # docker compose run --rm freqtrade backtesting --strategy NewDiamond0 NewDiamond1 NewDiamond2 --timerange 20230101-20240405
    # filename is like NewDiamond.py, extract NewDiamond from it
    classname = f'New{classname}'
    names_string = ' '.join([f'{classname}{i}' for i in range(len(population))])
    os.system(
        f"docker compose run --rm freqtrade backtesting --strategy-list {names_string} --timerange 20230101-20240405 --timeframe 1h")
    while not os.path.exists("user_data/backtest_results/.last_result.json"):
        pass
    with open("user_data/backtest_results/.last_result.json", "r") as file:
        name = json.load(file)['latest_backtest']
    os.remove("user_data/backtest_results/.last_result.json")
    with open(f"user_data/backtest_results/{name}", "r") as file:
        obj = json.load(file)['strategy_comparison']
        for i in range(len(population)):
            profit = obj[i].get('profit_total')
            # print(profit)
            # calmar ratio can be calculated as profit / max_drawdown
            # max_drawdown = obj[i].get('max_drawdown_abs')
            # if float(max_drawdown) != 0:
            #     population[i]['loss'] = profit / float(max_drawdown)
            # else:
            #     population[i]['loss'] = profit
            population[i]['loss'] = profit
    os.remove(f"user_data/backtest_results/{name}")

    return population


def mutate_candidate(candidate):
    # pass low and high values as parameters, then define default as a number from low to high
    candidate_copy = copy.deepcopy(candidate)
    mutated_candidate = dict(candidate_copy)
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


def genetic_algorithm(parameters, population_size, generations, strategy_class='Diamond'):
    # add class
    # generate initial population
    # TODO: handle local max with generating new initial population if loss is the same for several generations
    # TODO: if too much candidates are the same, change them with mutation
    # TODO: add visualization
    # TODO: check for other strategies

    populations = []
    population = generate_initial_population(parameters, population_size)
    population_without_loss = copy.deepcopy(population)
    # generations
    for i in range(generations):
        generate_strategy_text_population(strategy_class, population_without_loss)
        population = evaluate_population(population, strategy_class)
        new_population = []
        for j in range(population_size):
            new_population.append(population[j])
            new_population.append(mutate_candidate(population[j]))
            new_population.append(crossover_candidates(population[random.randint(0, population_size - 1)],
                                                       population[random.randint(0, population_size - 1)]))
        population = copy.deepcopy(new_population)
        population = sorted(population, key=lambda x: -x['loss'])
        # print losses of the population
        print([candidate['loss'] for candidate in population])
        print(population[0])
        print(population[0]['loss'])
        fixed_population = copy.deepcopy(population)
        populations.append(fixed_population)
        if i == generations - 1:
            print("Losses of the populations")
            for population in populations:
                print([candidate['loss'] for candidate in population])
            print("Best candidates of the population")
            for population in populations:
                print(population[0])
            print("Losses of the best candidates")
            for population in populations:
                print(population[0]['loss'])
            return population[0]
        best_population = population[:int(population_size * 0.6)]
        worst_population = population[-int(population_size * 0.6):]
        worst_sample = random.sample(worst_population, int(population_size * 0.4))
        population = best_population + worst_sample
        if len(population) < population_size:
            population.append(population[0])
        population_without_loss = copy.deepcopy(population)
        for j in range(len(population_without_loss)):
            if 'loss' in population_without_loss[j]:
                population_without_loss[j].pop('loss')


if __name__ == "__main__":
    # TODO: put functions in classes and add visualization with jupiter notebook
    # params as parsed from strategy file
    parameters = strategy_text_generator.parse_parameters("user_data/strategies/sample_strategy.py")
    # default population_size=20, generations=10
    best_candidate = genetic_algorithm(parameters, 100, 10, 'SampleStrategy')
    print('Final result:')
    print(best_candidate)
    # parameters = strategy_text_generator.parse_parameters("user_data/strategies/diamond_strategy.py")
    # initial_population = generate_initial_population(parameters, 3)
    # print(initial_population)
    # filename = generate_strategy_text_population("Diamond", initial_population)
    # print(filename)
