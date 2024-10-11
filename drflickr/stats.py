# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: Apache-2.0

from drflickr.api import Api
from datetime import date, timedelta, datetime
from drresult import Ok, Err, returns_result
from mrjsonstore import JsonStore
import math
import logging

logger = logging.getLogger(__name__)


class Stats:
    def __init__(self, api, filename):
        self.api = api
        self.stats = JsonStore(filename)
        self.period = 28

    def load(self):
        with self.stats() as stats:
            stats.setdefault('views', {})
            stats['views'].setdefault('total', [])
            today = date.today() - timedelta(days=1)
            values = stats['views']['total']
            if len(values) == 0:
                last_date = today - timedelta(days=(self.period * 2))
            else:
                last_date = datetime.strptime(values[-1]['date'], '%Y-%m-%d').date()
            while last_date < today:
                last_date += timedelta(days=1)
                total_views = self.api.getTotalViews(last_date)
                values.append(
                    {'date': last_date.strftime('%Y-%m-%d'), 'value': total_views}
                )
        return self

    def filterOutliers(self, data):
        if len(data) == 0:
            return []

        mean = sum(data) / len(data)
        variance = sum((x - mean) ** 2 for x in data) / len(data)
        std_dev = math.sqrt(variance)

        # Filter values within 3 standard deviations from the mean
        return [x for x in data if abs(x - mean) <= 3 * std_dev]

    def calcEma(self, values):
        window = min(self.period, int(len(values) / 2))
        if not values or window <= 0:
            return None

        alpha = 2 / (window + 1)
        ema = values[0]

        for value in values[1:]:
            ema = alpha * value + (1 - alpha) * ema

        return ema

    def viewsBelowEma(self):
        logger.info(f'checking views agains EMA')
        views = [x['value'] for x in self.stats.view()['views']['total']]
        views = self.filterOutliers(views)
        ema = self.calcEma(views[:-1])
        ema = ema * 1.4
        today = views[-1]
        logger.info(f'views EMA: {ema}, views today: {today}')
        return today < ema
