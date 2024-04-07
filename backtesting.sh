# to run this properly, you may need to activate the corresponding virtual environment, e.g.:
# source ~/.virtualenvs/TradingStrategyGA/bin/activate

# VolumePairList is not allowed for backtesting. Specify StaticPairList instead in config.json

#TIMERANGE="20170101-20240405"
TIMERANGE="20230101-20240405"

docker compose run --rm freqtrade download-data\
 --timerange $TIMERANGE

# list all the strategy class names manually in --strategy-list
docker compose run --rm freqtrade backtesting\
 --timerange $TIMERANGE\
 --timeframe 5m\
 --strategy-list SampleStrategy Diamond PatternRecognition Strategy005 hlhb\
 --export trades
