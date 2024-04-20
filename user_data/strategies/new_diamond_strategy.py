from typing import Type, List, Any, Dict
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy
from diamond_strategy import Diamond


class NewDiamond(Diamond):
        buy_vertical_push = DecimalParameter(low=0.5, high=1.5, decimals=3, default=3.0, space='buy', optimize=True)
        buy_horizontal_push = IntParameter(low=0.0, high=10.0, default=0.0, space='buy', optimize=True)
        sell_vertical_push = DecimalParameter(low=0.5, high=1.5, decimals=3, default=3.0, space='sell', optimize=True)
        sell_horizontal_push = IntParameter(low=0.0, high=10.0, default=0.0, space='sell', optimize=True)
