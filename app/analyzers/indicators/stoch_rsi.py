""" Stochastic RSI Indicator
"""

import numpy
import pandas
import talib

from analyzers.utils import IndicatorUtils


class StochasticRSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['stoch_rsi'], hot_thresh=None, cold_thresh=None):
        """Performs a Stochastic RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our Stochastic RSI.
            signal (list, optional): Defaults to stoch_rsi. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        rsi_period_count = period_count * 2
        close_np = dataframe['close'].to_numpy(dtype=float)
        rsi_values = talib.RSI(close_np, rsi_period_count)
        rsi_df = pandas.DataFrame({'rsi': rsi_values})
        rsi_df = rsi_df.dropna().reset_index(drop=True)
        rsi_df = rsi_df.assign(stoch_rsi=numpy.nan)
        for index in range(period_count, rsi_df.shape[0]):
            start_index = index - period_count
            last_index = index + 1
            rsi_min = rsi_df['rsi'].iloc[start_index:last_index].min()
            rsi_max = rsi_df['rsi'].iloc[start_index:last_index].max()
            stoch_rsi = (100 * ((rsi_df['rsi'].iloc[index] - rsi_min) / (rsi_max - rsi_min)))
            rsi_df.loc[rsi_df.index[index], 'stoch_rsi'] = stoch_rsi
        rsi_df['slow_k'] = rsi_df['stoch_rsi'].rolling(window=3).mean()
        rsi_df['slow_d'] = rsi_df['slow_k'].rolling(window=3).mean()
        rsi_df.dropna(how='any', inplace=True)
        if rsi_df[signal[0]].shape[0]:
            rsi_df['is_hot'] = rsi_df[signal[0]] < hot_thresh
            rsi_df['is_cold'] = rsi_df[signal[0]] > cold_thresh

        return rsi_df
