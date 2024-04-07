# generator accepts a class and returns a text representation of the classm that extends the class with custom hyperopt search spaces

from typing import Type, List, Any, Dict

class Generator:

    def __init__(self):
        self.strategy = None

    def generate_text(self, strategy, parameters: List[Any]):
        text = f"from typing import Type, List, Any, Dict\n"
        text += f"from freqtrade.strategy import IStrategy\n"
        text += f"from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal\n"
        text += f"from user_data.strategies.{strategy.lower()}_strategy import {strategy}\n\n"

        text += f"class NewStrategy({strategy}):\n"
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
        return text


if __name__ == "__main__":
    generator = Generator()
    print(generator.generate_text("Diamond", []))
    with open("strategy_text.py", "w") as file:
        file.write(generator.generate_text("Diamond", []))