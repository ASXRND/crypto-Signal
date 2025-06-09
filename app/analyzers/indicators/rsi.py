""" RSI Indicator
"""

import math

import pandas
from talib import abstract

from analyzers.utils import IndicatorUtils


class RSI(IndicatorUtils):
    def analyze(self, historical_data, period_count=14,
                signal=['rsi'], hot_thresh=None, cold_thresh=None, forecast_lookahead=1, forecast_history=20):
        """Performs an RSI analysis on the historical data

        Args:
            historical_data (list): A matrix of historical OHCLV data.
            period_count (int, optional): Defaults to 14. The number of data points to consider for
                our RSI.
            signal (list, optional): Defaults to rsi. The indicator line to check hot/cold
                against.
            hot_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to purchase.
            cold_thresh (float, optional): Defaults to None. The threshold at which this might be
                good to sell.
            forecast_lookahead (int, optional): На сколько свечей вперёд считать движение.
            forecast_history (int, optional): Сколько последних сигналов анализировать для прогноза.

        Returns:
            pandas.DataFrame: A dataframe containing the indicators and hot/cold values.
        """

        dataframe = self.convert_to_dataframe(historical_data)
        rsi_values = abstract.RSI(dataframe, period_count).to_frame()
        rsi_values.dropna(how='all', inplace=True)
        rsi_values.rename(columns={rsi_values.columns[0]: 'rsi'}, inplace=True)

        if rsi_values[signal[0]].shape[0]:
            rsi_values['is_hot'] = rsi_values[signal[0]] < hot_thresh
            rsi_values['is_cold'] = rsi_values[signal[0]] > cold_thresh

            # --- Новый блок: расчет среднего движения после сигнала ---
            closes = dataframe['close'].reindex(rsi_values.index)
            forecast_pct = []
            for idx in rsi_values.index[-forecast_history:]:
                if rsi_values.at[idx, 'is_hot'] or rsi_values.at[idx, 'is_cold']:
                    # Индекс будущей свечи
                    future_idx = closes.index.get_loc(idx) + forecast_lookahead
                    if future_idx < len(closes):
                        price_now = closes.loc[idx]
                        price_future = closes.iloc[future_idx]
                        pct_move = (price_future - price_now) / price_now * 100
                        forecast_pct.append(pct_move)
            rsi_values['forecast_pct'] = 0.0
            if forecast_pct:
                rsi_values.at[rsi_values.index[-1], 'forecast_pct'] = round(sum(forecast_pct) / len(forecast_pct), 2)
            else:
                rsi_values.at[rsi_values.index[-1], 'forecast_pct'] = 0.0
            # --- Конец нового блока ---

        return rsi_values
