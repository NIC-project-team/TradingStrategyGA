# generator accepts a class, list of parameters and returns a new strategy with rewritten hyperopt search spaces

# pre-defined space (roi_space, generate_roi_table, stoploss_space, trailing_space, max_open_trades_space)
from typing import Type, List, Any, Dict
from freqtrade.strategy import IStrategy
from freqtrade.optimize.space import Categorical, Dimension, Integer, SKDecimal
# integer, boolean, skdecimal, categorical, dimension
from user_data.strategies.diamond_strategy import Diamond
class Generator:

    def __init__(self):
        self.strategy = None

    def generate(self, strategy: Type[IStrategy], parameters: List[Any]) -> Type[IStrategy]:
        class NewStrategy(strategy):
            class HyperOpt:
                # Define a custom stoploss space.
                def stoploss_space():
                    return [SKDecimal(-0.05, -0.01, decimals=3, name='stoploss')]

                # Define custom ROI space
                def roi_space() -> List[Dimension]:
                    return [
                        Integer(10, 120, name='roi_t1'),
                        Integer(10, 60, name='roi_t2'),
                        Integer(10, 40, name='roi_t3'),
                        SKDecimal(0.01, 0.04, decimals=3, name='roi_p1'),
                        SKDecimal(0.01, 0.07, decimals=3, name='roi_p2'),
                        SKDecimal(0.01, 0.20, decimals=3, name='roi_p3'),
                    ]

                def generate_roi_table(params: Dict) -> Dict[int, float]:
                    roi_table = {}
                    roi_table[0] = params['roi_p1'] + params['roi_p2'] + params['roi_p3']
                    roi_table[params['roi_t3']] = params['roi_p1'] + params['roi_p2']
                    roi_table[params['roi_t3'] + params['roi_t2']] = params['roi_p1']
                    roi_table[params['roi_t3'] + params['roi_t2'] + params['roi_t1']] = 0

                    return roi_table

        self.strategy = NewStrategy
        return NewStrategy

    def save_to_file(self, path: str):
        with open(path, 'w') as f:
            f.write(self.strategy)


# Usage
if __name__ == '__main__':
    generator = Generator()
    new_strategy = generator.generate(Diamond, [])
    # save to file
    generator.save_to_file('test_file.py')


