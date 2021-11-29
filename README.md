# Crypto fund

An extensible cloud based Automated Trading System.

Modules
    - Crypto currencies
    - Stocks

Strategies
    - Pairs Trading
    - Real time abitrage

## Architecture
    - Front End
        - Trader's app :: Monitor Order executions, PnL and Positions & Risk
    - Backend
        -Market Data :: Connects to Exchanges to download Market Data; Contains a Data normalizer block to convert different market data formats to JSON
        -Complex Event Processing engine:: Monitor prices and automate trading decisions and makes decisions about execution of orders
        -Maths Calc:: dedicated calculation block in the server for calculating Risk
        -Order Manager :: Intergrated with Risk limits for Operational Risk, contains a order router to place orders to different exchanges
    - Database
        -Mongo dB :: Order definition, Market Data and Event History
        - Event history, to identify future opportunities without recalculating 



# Components
    -