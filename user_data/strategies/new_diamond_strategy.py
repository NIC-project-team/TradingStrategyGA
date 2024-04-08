from typing import Type, List, Any, Dict
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy
from diamond_strategy import Diamond


class NewDiamond(Diamond):
        buy_volumeAVG = IntParameter(low=735, high=22004, default=5204, space='buy', optimize=True)
        buy_rsi = DecimalParameter(low=2910.714140620263, high=87550.64916643348, decimals=0, default=7136.8687611503365, space='buy', optimize=True)
