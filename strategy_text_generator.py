# generator accepts a class and returns a text representation of the classm that extends the class with custom hyperopt search spaces
import random
# for now handle all int as IntParameter and float parameters as SKDecimal
from typing import Type, List, Any, Dict
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal


class Generator:

    def __init__(self):
        self.strategy = None

    def generate_text(self, strategy: str, parameters: Dict[Any, Dict], default_spaces: bool = False) -> str:
        text = f"from typing import Type, List, Any, Dict\n"
        text += f"from freqtrade.strategy import IStrategy\n"
        text += f"from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal\n"
        text += f"from user_data.strategies.{strategy.lower()}_strategy import {strategy}\n\n"

        text += f"class New{strategy}({strategy}):\n"
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
            if parameter[1] == 'int':
                text += (f"        {parameter[0]} = Integer(low={parameter[0]['low']}, high={parameter[0]['high']}, "
                         f"default={parameter[0]['default']}, space='buy', optimize=True)\n")
            elif parameter[1] == 'float':
                text += (f"        {parameter[0]} = SKDecimal(low={parameter[0]['low']}, high={parameter[0]['high']}, "
                         f"default={parameter[0]['default']}, decimals={parameter[0]['decimals']}, space='buy', optimize=True)\n")
        return text


def generate_random_strategy(parameters: List[Any]) -> Dict[Any, Dict]:
    strategy = {}
    for j in range(len(parameters)):
        strategy[parameters[j][0]] = {}
        if parameters[j][1] == 'int':
            strategy[parameters[j][0]]['low'] = random.randint(0, 10000)
            strategy[parameters[j][0]]['high'] = random.randint(0, 100000)
            strategy[parameters[j][0]]['default'] = random.randint(0, 10000)
        elif parameters[j][1] == 'float':
            strategy[parameters[j][0]]['low'] = random.uniform(0, 10000)
            strategy[parameters[j][0]]['high'] = random.uniform(0, 100000)
            strategy[parameters[j][0]]['default'] = random.uniform(0, 10000)
            strategy[parameters[j][0]]['decimals'] = random.randint(0, round(
                100000 / strategy[parameters[j][0]]['high']))

    return strategy


if __name__ == "__main__":
    strategy_class = "Diamond"
    parameters = [['buy_volumeAVG', 'int'], ['buy_rsi', 'float']]
    strategy = generate_random_strategy(parameters)
    generator = Generator()
    text = generator.generate_text(strategy_class, strategy)
    print(text)
    with open(f"new_{strategy_class.lower()}.py", "w") as file:
        file.write(text)
