from typing import Type, List, Any, Dict
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter, IStrategy
from pattern_recognition_strategy import PatternRecognition


class NewPatternRecognition(PatternRecognition):
        buy_volumeAVG = IntParameter(low=158, high=43995, default=5138, space='buy', optimize=True)
        buy_rsi = DecimalParameter(low=2929.078414111064, high=69638.49677359418, decimals=1, default=7223.343738201048, space='buy', optimize=True)
