from typing import Type, List, Any, Dict
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy
from pattern_recognition_strategy import PatternRecognition


class NewPatternRecognition(PatternRecognition):
        buy_volumeAVG = IntParameter(low=53, high=69790, default=3917, space='buy', optimize=True)
        buy_rsi = DecimalParameter(low=228.97748990142853, high=29301.946588378203, decimals=3, default=1168.7378783161307, space='buy', optimize=True)
