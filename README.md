## TL;DR
You need docker desktop to run this project. 

Then start genetic algorithm optimization with:
```python
python3 genetic_optimizer.py
```

## Important to remember

Disclaimer: This is the repository to demonstrate Genetic Algorithm optimization for Freqtrade bot. 

It is not a financial advice. Use it at your own risk and always be cautious with designing your strategies and testing 
them before using them in real trading.

To fork repo locally use ssh key.

## Usage

To run, use: 
```docker
docker compose up
```
Requirements: docker desktop

To run a separate version with other telegram bot or without bot, change config.json "telegram" part.

Web application can be accessed locally: http://127.0.0.1:8080/

To run backtesting for all strategies with predefined parameters, use:
```
./backtesting.sh
```

To run genetic algorithm, you need to firstly create strategy to optimize, using parameters as described in freqtrade
documentation: https://www.freqtrade.io/en/latest/hyperopt/ (you can access examples in user_data/strategies folder)

Then you need to pass name of the strategy and file name to main function in genetic_optimizer.py. 

## Genetic Algorithm Optimization

Then, you can run genetic algorithm with:
```
python3 genetic_optimizer.py
```

After that, report will be generated in reports folder. If you want to run backtesting for the best strategy, you can create
strategy with best parameters using:
```
python3 strategy_text_generator.py
```

## Backtesting

Then you can run backtesting for this strategy using:
```
docker compose run --rm freqtrade backtesting --strategy <strategy name> --timerange <start-end>
```

## Trade dry-run

Tu run dry run for this strategy, use:
```
docker compose run --rm freqtrade trade --strategy <strategy name> --timerange <start-end>
```

## Telegram API and web UI

Telegram api and ip address for UI can be changed in config.json file.

To run telegram bot, you need to firstly create telegram bot using BotFather and get token. Then you need to create
telegram group and add bot to it. After that, you need to get chat id of the group. You can get it by sending message to
https://t.me/username_to_id_bot. Then you need to add token and chat id to config.json file.


