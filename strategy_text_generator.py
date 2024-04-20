# generator accepts a class and returns a text representation of the class
# that extends the class with custom hyperopt search spaces + search spaces for custom parameters
import random
# for now handle all int as IntParameter and float parameters as DecimalParameter
from typing import Type, List, Any, Dict, Tuple

file_class_dict = {'Diamond': 'diamond_strategy',
                   'Strategy005': '005_strategy',
                   'PatternRecognition': 'pattern_recognition_strategy'}


def generate_text(strategy_class: str, parameters: Dict[Any, Dict], default_spaces: bool = False) -> Tuple[str, str]:
    text = f"from typing import Type, List, Any, Dict\n"
    text += f"from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy\n"
    text += f"from {file_class_dict[strategy_class]} import {strategy_class}\n\n\n"
    text += f"class New{strategy_class}({strategy_class}):\n"
    # changing default search spaces
    if default_spaces:
        text += f"    class HyperOpt:\n"
        text += f"        # Define a custom stoploss space.\n"
        text += f"        def stoploss_space(self):\n"
        text += f"            return [SKDecimal(-0.05, -0.01, decimals=3, name='stoploss')]\n\n"
        text += f"        # Define custom ROI space\n"
        text += f"        def roi_space(self) -> List[Dimension]:\n"
        text += f"            return [\n"
        text += f"                Integer(10, 120, name='roi_t1'),\n"
        text += f"                Integer(10, 60, name='roi_t2'),\n"
        text += f"                Integer(10, 40, name='roi_t3'),\n"
        text += f"                SKDecimal(0.01, 0.04, decimals=3, name='roi_p1'),\n"
        text += f"                SKDecimal(0.01, 0.07, decimals=3, name='roi_p2'),\n"
        text += f"                SKDecimal(0.01, 0.20, decimals=3, name='roi_p3'),\n"
        text += f"            ]\n\n"
        text += f"        def generate_roi_table(self, params: Dict) -> Dict[int, float]:\n"
        text += f"            roi_table = {{}}\n"
        text += f"            roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']\n"
        text += f"            roi_table[params['roi_t3']] = params['roi_p1'] + params['roi_p2']\n"
        text += f"            roi_table[params['roi_t3'] + params['roi_t2']] = params['roi_p1']\n"
        text += f"            roi_table[params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0\n\n"
        text += f"            return roi_table\n"
    # adding custom parameters to the strategy
    for parameter in parameters:
        values = parameters[parameter]
        if values['type'] == 'int':
            text += (f"        {parameter} = IntParameter(low={values['low']}, high={values['high']}, "
                     f"default={values['default']}, space='buy', optimize=True)\n")
        elif values['type'] == 'float':
            text += (f"        {parameter} = DecimalParameter(low={values['low']}, high={values['high']}, "
                     f"decimals={values['decimals']}, default={values['default']}, space={values['space']}, optimize=True)\n")
    filename = f"user_data/strategies/new_{file_class_dict[strategy_class]}.py"
    with open(filename, "w") as file:
        file.write(text)
    return text, filename


def generate_random_strategy(parameters: List[Any]) -> Dict[Any, Dict]:
    strategy = {}
    for j in range(len(parameters)):
        strategy[parameters[j][0]] = {}
        if parameters[j][1] == 'int':
            strategy[parameters[j][0]]['type'] = 'int'
            strategy[parameters[j][0]]['low'] = random.randint(0, 10000)
            strategy[parameters[j][0]]['high'] = random.randint(0, 100000)
            strategy[parameters[j][0]]['default'] = random.randint(0, 10000)

        elif parameters[j][1] == 'float':
            strategy[parameters[j][0]]['type'] = 'float'
            strategy[parameters[j][0]]['low'] = random.uniform(0, 10000)
            strategy[parameters[j][0]]['high'] = random.uniform(0, 100000)
            strategy[parameters[j][0]]['default'] = random.uniform(0, 10000)
            strategy[parameters[j][0]]['decimals'] = random.randint(0, round(
                100000 / strategy[parameters[j][0]]['high']))

    return strategy


# function for parsing a list of parameters and their types from a file of a strategy
def parse_parameters(strategy_file: str) -> Dict[str, Dict]:
    with open(strategy_file, "r") as file:
        lines = file.readlines()
    parameters = {}
    for line in lines:
        if "Parameter" in line:
            if 'from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy' in line:
                continue
            if "DecimalParameter" in line or "IntParameter" in line:
                parameter_vals = line.split("(")[1].split(")")[0]
                parameter_vals = parameter_vals.split(", ")
                parameter_name = line.split()[0]
                parameter_vals = [val.split("=")[-1].replace("'", "").replace(" ", "") for val in parameter_vals]
                print(parameter_vals)
                type_param = "int" if "IntParameter" in line else "float"
                parameters[parameter_name] = {'type': type_param,
                                              'low': float(parameter_vals[0]),
                                              'high': float(parameter_vals[1]),
                                              'default': float(parameter_vals[2]),
                                              'space': parameter_vals[3]}

                if type_param == "float":
                    parameters[parameter_name]['decimals'] = int(parameter_vals[2])
                    parameters[parameter_name]['space'] = parameter_vals[4]
    return parameters


if __name__ == "__main__":
    # generated strategy is in the user_data/strategies/new_patter_recognition_strategy.py
    # strategy_class = "PatternRecognition"
    # parameter_names = [['buy_volumeAVG', 'int'], ['buy_rsi', 'float']]
    # strategy_params = generate_random_strategy(parameter_names)
    # print(strategy_params)
    # text, filename = generate_text(strategy_class, strategy_params)
    # print(text)
    print(parse_parameters('user_data/strategies/diamond_strategy.py'))
