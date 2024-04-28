import json
import os
import random
import copy
import time

import strategy_text_generator


def generate_initial_population(parameters, population_size):
    population = []
    for i in range(population_size):
        candidate = {}
        for key in parameters.keys():
            candidate[key] = {}
            candidate[key]['type'] = parameters[key]['type']
            candidate[key]['space'] = parameters[key]['space']

            if parameters[key]['type'] == 'int':
                candidate[key]['low'] = parameters[key]['low']
                candidate[key]['high'] = parameters[key]['high']
                candidate[key]['default'] = random.randint(parameters[key]['low'], parameters[key]['high'])
            elif parameters[key]['type'] == 'float':
                candidate[key]['low'] = parameters[key]['low']
                candidate[key]['high'] = parameters[key]['high']
                candidate[key]['default'] = random.uniform(parameters[key]['low'], parameters[key]['high'])
                candidate[key]['decimals'] = parameters[key]['decimals']
                candidate[key]['default'] = round(candidate[key]['default'], candidate[key]['decimals'])
            elif parameters[key]['type'] == 'categorical':
                candidate[key]['options'] = parameters[key]['options']
                candidate[key]['default'] = random.choice(parameters[key]['options'])
            elif parameters[key]['type'] == 'boolean':
                candidate[key]['default'] = random.choice([True, False])
        population.append(candidate)
    return population


def generate_strategy_text_population(strategy_class, population):
    for i, candidate in enumerate(population):
        with open(f"user_data/strategies/new_{strategy_class}{i}.py", "w") as file:
            text, filename = strategy_text_generator.generate_text(strategy_class, candidate, i)
            file.write(text)
    return f"user_data/strategies/new_{strategy_class}.py"


def evaluate_population(population, classname, timeframe='1h'):
    classname = f'New{classname}'
    names_string = ' '.join([f'{classname}{i}' for i in range(len(population))])
    os.system(
        f"docker compose run --rm freqtrade backtesting --strategy-list {names_string} --timerange 20240101-20240405 --timeframe {timeframe}")
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
                    mutated_candidate[key]['default'] = round(mutated_candidate[key]['default'],
                                                              mutated_candidate[key]['decimals'])
                elif mutated_candidate[key]['type'] == 'categorical':
                    mutated_candidate[key]['default'] = random.choice(mutated_candidate[key]['options'])

                elif mutated_candidate[key]['type'] == 'boolean':
                    mutated_candidate[key]['default'] = random.choice([True, False])

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


def genetic_algorithm(parameters, population_size, generations, strategy_class='Diamond', timeframe='1h'):
    t = time.time()

    populations = []
    best_losses = []
    avg_losses = []
    best_candidates = []
    population = generate_initial_population(parameters, population_size)
    population_without_loss = copy.deepcopy(population)
    # generations
    for i in range(generations):
        print("Generation", i, time.time() - t)
        generate_strategy_text_population(strategy_class, population_without_loss)
        population = evaluate_population(population, strategy_class, timeframe)
        population = sorted(population, key=lambda x: -x['loss'])
        new_population = []
        for j in range(population_size // 3):
            new_population.append(population[j])
            new_population.append(mutate_candidate(population[random.randint(0, population_size - 1)]))
            new_population.append(crossover_candidates(population[random.randint(0, population_size - 1)],
                                                       population[random.randint(0, population_size - 1)]))
        population = copy.deepcopy(new_population)
        population = sorted(population, key=lambda x: -x['loss'])
        # print losses of the population
        print([candidate['loss'] for candidate in population])
        print(population[0])
        avg_loss = sum([population[i]['loss'] for i in range(len(population))]) / len(population)
        print(population[0]['loss'], avg_loss)
        best_losses.append(population[0]['loss'])
        avg_losses.append(avg_loss)
        best_candidates.append(population[0])
        fixed_population = copy.deepcopy(population)
        populations.append(fixed_population)
        if i == generations - 1:
            final_time = time.time() - t

            print("Losses of the populations")
            for pop in populations:
                print([candidate['loss'] for candidate in pop])
            print("Best candidates of the population")
            for pop in populations:
                print(pop[0])
            print("Losses of the best candidates")
            for pop in populations:
                print(pop[0]['loss'])
            print("Average losses")
            for j in range(len(populations)):
                print(avg_losses[j])

            with open(f"reports/{strategy_class}.json", "w") as file:
                json.dump({'losses': best_losses, 'avg_losses': avg_losses, 'best_candidates': best_candidates, 'final_time': final_time}, file)
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


def delete_new_strategy_files():
    for file in os.listdir('user_data/strategies'):
        # remove files starting with new_
        if file.startswith(f'new_'):
            os.remove(f'user_data/strategies/{file}')
    for file in os.listdir('user_data/backtest_results'):
        # remove files starting with new_
        if file.startswith(f'new_'):
            os.remove(f'user_data/backtest_results/{file}')


if __name__ == "__main__":
    # params as parsed from strategy file
    # strategy_class = 'Diamond'
    # strategy_file = f"user_data/strategies/diamond_strategy.py"
    # strategy_class = 'Strategy005'
    # strategy_file = f"user_data/strategies/strategy_005.py"
    strategy_class = 'SampleStrategy'
    strategy_file = f"user_data/strategies/sample_strategy.py"
    parameters, timeframe = strategy_text_generator.parse_parameters(strategy_file)
    print(parameters)
    print(timeframe)
    best_candidate = genetic_algorithm(parameters, 30, 20, strategy_class, timeframe)
    print('Final result:')
    print(best_candidate)
    delete_new_strategy_files()
