""" Handles outputting results to the terminal.
"""

import json
import sys

import structlog


class Output():
    """ Handles outputting results to the terminal.
    """

    def __init__(self):
        """Initializes Output class.
        """

        # Установка кодировки stdout в UTF-8 для поддержки русского языка при запуске в Docker.
        try:
            sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
        except Exception:
            pass  # В докере или IDE может не поддерживаться fileno, игнорируем ошибку

        self.logger = structlog.get_logger()
        self.dispatcher = {
            'cli': self.to_cli,
            'csv': self.to_csv,
            'json': self.to_json
        }


    def to_cli(self, results, market_pair):
        """Создаёт структурированный и русифицированный вывод для CLI"""
        normal_colour = '\u001b[0m'
        hot_colour = '\u001b[31m'
        cold_colour = '\u001b[36m'

        indicator_type_map = {
            'indicators': 'Индикаторы',
            'informants': 'Информанты',
            'crossovers': 'Пересечения'
        }
        indicator_desc = {
            'stoch_rsi': 'Stochastic RSI — осциллятор, показывает перекупленность (>0.8) или перепроданность (<0.2).',
            'rsi': 'RSI — индекс относительной силы, классический индикатор перекупленности/перепроданности.',
            'macd': 'MACD — индикатор схождения/расхождения скользящих средних.',
            'mfi': 'MFI — индекс денежного потока.',
            'obv': 'OBV — объём на балансе.',
            'momentum': 'Momentum — индикатор импульса.',
            'ichimoku': 'Ichimoku — комплексный индикатор тренда.',
            'sma': 'SMA — простая скользящая средняя.',
            'ema': 'EMA — экспоненциальная скользящая средняя.',
            'vwap': 'VWAP — средневзвешенная цена по объёму.',
            'bollinger_bands': 'Bollinger Bands — полосы Боллинджера.'
        }

        output = f'\nПара: {market_pair}\n' + '-'*40 + '\n'
        for indicator_type in results:
            rus_type = indicator_type_map.get(indicator_type, indicator_type)
            output += f'{rus_type}:\n'
            for indicator in results[indicator_type]:
                for i, analysis in enumerate(results[indicator_type][indicator]):
                    if not hasattr(analysis['result'], 'shape') or analysis['result'].shape[0] == 0:
                        self.logger.info('Нет результатов для %s #%s', indicator, i)
                        continue

                    colour_code = normal_colour
                    status = ''
                    status_explain = ''
                    if 'is_hot' in analysis['result'].iloc[-1]:
                        if analysis['result'].iloc[-1]['is_hot']:
                            colour_code = hot_colour
                            status = '🔥 Горячо'
                            status_explain = 'Сигнал: индикатор в зоне перекупленности/активности.'
                    if 'is_cold' in analysis['result'].iloc[-1]:
                        if analysis['result'].iloc[-1]['is_cold']:
                            colour_code = cold_colour
                            status = '❄️ Холодно'
                            status_explain = 'Сигнал: индикатор в зоне перепроданности/пассивности.'

                    # Описание индикатора
                    desc = indicator_desc.get(indicator, '')

                    if indicator_type == 'crossovers':
                        key_signal = '{}_{}'.format(
                            analysis['config']['key_signal'],
                            analysis['config']['key_indicator_index']
                        )
                        key_value = analysis['result'].iloc[-1][key_signal]
                        crossed_signal = '{}_{}'.format(
                            analysis['config']['crossed_signal'],
                            analysis['config']['crossed_indicator_index']
                        )
                        crossed_value = analysis['result'].iloc[-1][crossed_signal]
                        if isinstance(key_value, float):
                            key_value = format(key_value, '.8f')
                        if isinstance(crossed_value, float):
                            crossed_value = format(crossed_value, '.8f')
                        formatted_string = f'{key_value} / {crossed_value}'
                        output += f"  {colour_code}{indicator} #{i}: {formatted_string} {status}{normal_colour}\n"
                        if desc:
                            output += f"    → {desc}\n"
                        if status_explain:
                            output += f"    → {status_explain}\n"
                    else:
                        formatted_values = []
                        for signal in analysis['config']['signal']:
                            value = analysis['result'].iloc[-1][signal]
                            if isinstance(value, float):
                                formatted_values.append(format(value, '.8f'))
                            else:
                                formatted_values.append(str(value))
                        formatted_string = ' / '.join(formatted_values)
                        output += f"  {colour_code}{indicator} #{i}: {formatted_string} {status}{normal_colour}\n"
                        if desc:
                            output += f"    → {desc}\n"
                        if status_explain:
                            output += f"    → {status_explain}\n"
        output += '-'*40 + '\n'
        return output


    def to_csv(self, results, market_pair):
        """Creates the csv to output to the CLI

        Args:
            market_pair (str): Market pair that this message relates to.
            results (dict): The result of the completed analysis to output.

        Returns:
            str: Completed CSV message
        """

        self.logger.warning('WARNING: CSV output is deprecated and will be removed in a future version')

        output = str()
        for indicator_type in results:
            for indicator in results[indicator_type]:
                for i, analysis in enumerate(results[indicator_type][indicator]):
                    value = str()

                    if indicator_type == 'crossovers':
                        key_signal = '{}_{}'.format(
                            analysis['config']['key_signal'],
                            analysis['config']['key_indicator_index']
                        )

                        key_value = analysis['result'].iloc[-1][key_signal]

                        crossed_signal = '{}_{}'.format(
                            analysis['config']['crossed_signal'],
                            analysis['config']['crossed_indicator_index']
                        )

                        crossed_value = analysis['result'].iloc[-1][crossed_signal]

                        if isinstance(key_value, float):
                            key_value = format(key_value, '.8f')

                        if isinstance(crossed_value, float):
                            crossed_value = format(crossed_value, '.8f')

                        value = '/'.join([key_value, crossed_value])
                    else:
                        for signal in analysis['config']['signal']:
                            value = analysis['result'].iloc[-1][signal]
                            if isinstance(value, float):
                                value = format(value, '.8f')

                    is_hot = str()
                    if 'is_hot' in analysis['result'].iloc[-1]:
                        is_hot = str(analysis['result'].iloc[-1]['is_hot'])

                    is_cold = str()
                    if 'is_cold' in analysis['result'].iloc[-1]:
                        is_cold = str(analysis['result'].iloc[-1]['is_cold'])

                    new_output = ','.join([
                        market_pair,
                        indicator_type,
                        indicator,
                        str(i),
                        value,
                        is_hot,
                        is_cold
                    ])

                    output += '\n{}'.format(new_output)

        return output


    def to_json(self, results, market_pair):
        """Creates the JSON to output to the CLI

        Args:
            market_pair (str): Market pair that this message relates to.
            results (dict): The result of the completed analysis to output.

        Returns:
            str: Completed JSON message
        """

        self.logger.warning('WARNING: JSON output is deprecated and will be removed in a future version')

        for indicator_type in results:
            for indicator in results[indicator_type]:
                for index, analysis in enumerate(results[indicator_type][indicator]):
                    results[indicator_type][indicator][index]['result'] = analysis['result'].to_dict(
                        orient='records'
                    )[-1]

        formatted_results = { 'pair': market_pair, 'results': results }
        output = json.dumps(formatted_results)
        output += '\n'
        return output
