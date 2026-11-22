import datetime as dt
import pathlib
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"scripts"))
from collect_market_ticker import parse_daily

class MarketTickerTests(unittest.TestCase):
    def test_valid(self):
        with patch("collect_market_ticker.dt") as clock:
            clock.date.fromisoformat=dt.date.fromisoformat
            clock.datetime.now.return_value=dt.datetime(2026,11,21,tzinfo=dt.timezone.utc)
            clock.timezone.utc=dt.timezone.utc
            q=parse_daily({"meta":{"currency":"USD"},"values":[{"datetime":"2026-11-20","close":"100"},{"datetime":"2026-11-19","close":"90"}]},"dow","DJI")
        self.assertEqual(q["price"],100)
        self.assertEqual(q["previous_close"],90)
        self.assertEqual(q["market_status"],"STATUS NÃO CONFIRMADO")
    def test_missing_previous(self):
        with self.assertRaises(ValueError):
            parse_daily({"meta":{"currency":"USD"},"values":[{"datetime":"2026-11-20","close":"100"}]},"dow","DJI")
    def test_provider_error(self):
        with self.assertRaises(ValueError):
            parse_daily({"status":"error","message":"not entitled"},"dow","DJI")
    def test_invalid_price(self):
        with self.assertRaises(ValueError):
            parse_daily({"meta":{"currency":"USD"},"values":[{"datetime":"2026-11-20","close":"0"},{"datetime":"2026-11-19","close":"90"}]},"dow","DJI")
if __name__=="__main__":unittest.main()
