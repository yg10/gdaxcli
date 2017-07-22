"""Wrapper around gdax-python.

Gdax-python is the unofficial python library for GDAX.
  https://github.com/danpaquin/gdax-python
  https://pypi.python.org/pypi/gdax
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import gdax

import config

class Client(object):
  """Wrapper of the gdax-python library."""

  def __init__(self):
    """Initializer."""
    self._client = gdax.AuthenticatedClient(
        key=config.KEY, b64secret=config.SECRET, passphrase=config.PASSPHRASE)
    # TODO: configure sandbox keys.

  def products(self):
    """Lists products available for trading."""
    print('Product')
    for product in self._get_product_ids():
      print(product)

  def ticker(self, product_ids=None):
    # TODO: Configure default products or currencies e.g. USD only, ETH only.
    # Add an extra space at the end for padding.
    header = [
      'Product    ',
      'Price      ',
      'Size       ',
      'Bid        ',
      'Ask        ',
      'Gap        ',
      '24h Open   ',
      '24h High   ',
      '24h Low    ',
      '24h Gain (%)   ',
      '24h Volume     ',
    ]
    print(''.join(header))
    if product_ids is None:
      product_ids = self._get_product_ids()
    for product_id in product_ids:
      tick = self._client.get_product_ticker(product_id)
      gap = float(tick['ask']) - float(tick['bid'])
      stats = self._client.get_product_24hr_stats(product_id)
      gain = float(tick['price']) - float(stats['open'])
      gain_perc = gain / float(stats['open']) * 100
      parts = [
        '%-10s ' % product_id,
        '%10s ' % self._truncate(tick['price'], 2),
        '%10s ' % self._truncate(tick['size'], 4),
        '%10s ' % self._truncate(tick['bid'], 2),
        '%10s ' % self._truncate(tick['ask'], 2),
        '%10s ' % self._truncate('%.6f' % gap, 2),
        '%10s ' % self._truncate(stats['open'], 2),
        '%10s ' % self._truncate(stats['high'], 2),
        '%10s ' % self._truncate(stats['low'], 2),
        '%6s (%s)' % (self._truncate(gain, 2), self._truncate(gain_perc, 1)),
        '%14s' % self._truncate(tick['volume'], 4)]
      print(''.join(parts))

  def balance(self):
    print('Currency  Balance')
    accounts = self._client.get_accounts()
    accounts.sort(key=lambda acc: acc['currency'])
    for account in accounts:
      avail = account['available']
      bal = account['balance']
      hold = account['hold']
      currency = account['currency']
      accuracy = 2 if currency == 'USD' else 4
      parts = [
        '%-10s' % account['currency'],
        self._truncate(avail, accuracy),
      ]
      if avail != bal:
        parts.append(' (%s - %s)' % (
            self._truncate(bal, accuracy), self._truncate(hold, accuracy)))
      print(''.join(parts))

  def _get_product_ids(self):
    """Gets sorted list of products."""
    products = self._client.get_products()
    product_ids = [p['id'] for p in products]
    product_ids.sort()
    return product_ids

  def _truncate(self, s, digits):
    """Truncate the value to the number of digits after the dot specified.

    We don't round up because rounding up can cause issues. For example you have
    0.1111115 BTC, but rounding up could show 0.111112, which exceeds the actual
    amount when you try to sell all of it.
    """
    if not isinstance(s, str):
      s = str(s)
    for index, char in enumerate(s):
      if char == '.':
        dot_index = index
        end = dot_index + digits + 1
        break
    else:
      end = len(s)
    return s[:end]