# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement

# --- Do not remove these libs ---
from functools import reduce
from typing import Any, Callable, Dict, List

import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from skopt.space import Categorical, Dimension, Integer, Real  # noqa

from freqtrade.optimize.hyperopt_interface import IHyperOpt

# --------------------------------
# Add your lib to import here
import talib.abstract as ta  # noqa
import freqtrade.vendor.qtpylib.indicators as qtpylib


class DrissaHyperopt(IHyperOpt):
        """
        This is a Hyperopt template to get you started.

        More information in the documentation: https://www.freqtrade.io/en/latest/hyperopt/

        You should:
        - Add any lib you need to build your hyperopt.

        You must keep:
        - The prototypes for the methods: populate_indicators, indicator_space, buy_strategy_generator.

        The methods roi_space, generate_roi_table and stoploss_space are not required
        and are provided by default.
        However, you may override them if you need 'roi' and 'stoploss' spaces that
        differ from the defaults offered by Freqtrade.
        Sample implementation of these methods will be copied to `user_data/hyperopts` when
        creating the user-data directory using `freqtrade create-userdir --userdir user_data`,
        or is available online under the following URL:
        https://github.com/freqtrade/freqtrade/blob/develop/freqtrade/templates/sample_hyperopt_advanced.py.
        """
        @staticmethod
        def populate_indicators(dataframe: DataFrame, metadata: dict) -> DataFrame:
                
                dataframe['rsi'] = ta.RSI(dataframe)
                dataframe['sell-rsi'] = ta.RSI(dataframe)

                #Boillinger bands
                bollinger1 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=1)
                dataframe['bb_lowerband1'] = bollinger1['lower']
                dataframe['bb_middleband1'] = bollinger1['mid']
                dataframe['bb_upperband1'] = bollinger1['upper']

                bollinger2 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=2)
                dataframe['bb_lowerband2'] = bollinger2['lower']
                dataframe['bb_middleband2'] = bollinger2['mid']
                dataframe['bb_upperband2'] = bollinger2['upper']

                bollinger3 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=3)
                dataframe['bb_lowerband3'] = bollinger3['lower']
                dataframe['bb_middleband3'] = bollinger3['mid']
                dataframe['bb_upperband3'] = bollinger3['upper']

                bollinger4 = qtpylib.bollinger_bands(qtpylib.typical_price(dataframe), window=20, stds=4)
                dataframe['bb_lowerband4'] = bollinger4['lower']
                dataframe['bb_middleband4'] = bollinger4['mid']
                dataframe['bb_upperband4'] = bollinger4['upper']

                return dataframe


        @staticmethod
        def populate_buy_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
                        """
                        Based on TA indicators, populates the buy signal for the given dataframe
                        :param dataframe: DataFrame populated with indicators
                        :param metadata: Additional information, like the currently traded pair
                        :return: DataFrame with buy column
                        """
                
                dataframe.loc[
                (
                        (dataframe['rsi'] > 30) & 
                        (dataframe["close"] < dataframe['bb_lowerband'])
                ),
                'buy'] = 1

        return dataframe

                        # GUARDS AND TRENDS
           if params.get('rsi-enabled'):
                                conditions.append(dataframe['rsi'] > params['rsi-value'])

                        # TRIGGERS
           if 'trigger' in params:
                                if params['trigger'] == 'bb_lower1':
                                        conditions.append(dataframe['close'] < dataframe['bb_lowerband1'])
                                if params['trigger'] == 'bb_lower2':
                                        conditions.append(dataframe['close'] < dataframe['bb_lowerband2'])
                                if params['trigger'] == 'bb_lower3':
                                        conditions.append(dataframe['close'] < dataframe['bb_lowerband3'])
                                if params['trigger'] == 'bb_lower4':
                                        conditions.append(dataframe['close'] < dataframe['bb_lowerband4'])
                                

                        # Check that the candle had volume
                conditions.append(dataframe['volume'] > 0)

                if conditions:
                                dataframe.loc[
                                        reduce(lambda x, y: x & y, conditions),
                                        'buy'] = 1

                return dataframe

                return populate_buy_trend

        @staticmethod
        def indicator_space() -> List[Dimension]:
                """
                Define your Hyperopt space for searching buy strategy parameters.
                """
                return [
                        Integer(5, 50, name='rsi-value'),
                        Categorical([True, False], name='rsi-enabled'),
                        Categorical(['bb_lower1','bb_lower2','bb_lower3','bb_lower4'], name='trigger')
                ]

        @staticmethod
        def sell_strategy_generator(params: Dict[str, Any]) -> Callable:
                """
                Define the sell strategy parameters to be used by Hyperopt.
                """
                def populate_sell_trend(dataframe: DataFrame, metadata: dict) -> DataFrame:
                        """
                        Based on TA indicators, populates the sell signal for the given dataframe
                        :param dataframe: DataFrame populated with indicators
                        :param metadata: Additional information, like the currently traded pair
                        :return: DataFrame with buy column
                        """
                        dataframe.loc[
                        (
                                (dataframe["close"] > dataframe['bb_middleband'])
                        ),
                        'sell'] = 1

                return dataframe

                conditions = []

                        # GUARDS AND TRENDS
                if params.get('sell-rsi-enabled'):
                                conditions.append(dataframe['rsi'] > params['sell-rsi-value'])

                        # TRIGGERS
                if 'sell-trigger' in params:
                                if params['sell-trigger'] == 'sell-bb_lower1':
                                        conditions.append(dataframe['close'] > dataframe['bb_lower1'])
                                if params['sell-trigger'] == 'sell-bb_mid1':
                                        conditions.append(dataframe['close'] > dataframe['bb_mid1'])
                                if params['sell-trigger'] == 'sell-bb_upper1':
                                        conditions.append(dataframe['close'] > dataframe['bb_upper1'])
 

                        # Check that the candle had volume
                conditions.append(dataframe['volume'] > 0)

                if conditions:
                                dataframe.loc[
                                        reduce(lambda x, y: x & y, conditions),
                                        'sell'] = 1

                return dataframe

                return populate_sell_trend

        @staticmethod
        def sell_indicator_space() -> List[Dimension]:
                """
                Define your Hyperopt space for searching sell strategy parameters.
                """
                return [
                        Integer(30, 100, name='sell-rsi-value'),
                        Categorical([True, False], name='sell-rsi-enabled'),
                        Categorical(['sell-bb_upper',
                                                 'sell-bb_mid1',
                                                 'sell-bb_upper1'], name='sell-trigger')
                ]
