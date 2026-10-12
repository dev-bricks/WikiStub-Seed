import math
import os
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

from translate import (
    estimate_batch_max_cost_usd,
    estimate_max_request_cost_usd,
    main,
    translate_batch,
    translate_text,
)


class TranslationBudgetTests(unittest.TestCase):
    def _fake_sdk(self):
        client = mock.Mock()
        client.messages.create.return_value = SimpleNamespace(
            content=[SimpleNamespace(text=" translated ")]
        )
        sdk = SimpleNamespace(Anthropic=mock.Mock(return_value=client))
        return sdk, client

    def test_direct_request_requires_a_valid_ceiling_before_client_creation(self):
        estimated = estimate_max_request_cost_usd("A definition")
        sdk, _ = self._fake_sdk()
        invalid_ceilings = (None, 0, -1, True, math.nan, math.inf, estimated / 2)

        with (
            mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}, clear=True),
            mock.patch.dict(sys.modules, {"anthropic": sdk}),
        ):
            for ceiling in invalid_ceilings:
                with self.subTest(ceiling=ceiling):
                    with self.assertRaises(ValueError):
                        translate_text("A definition", max_budget_usd=ceiling)
                    sdk.Anthropic.assert_not_called()

    def test_direct_request_uses_explicit_ceiling(self):
        budget = estimate_max_request_cost_usd("A definition")
        sdk, client = self._fake_sdk()

        with (
            mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}, clear=True),
            mock.patch.dict(sys.modules, {"anthropic": sdk}),
        ):
            result = translate_text("A definition", max_budget_usd=budget)

        self.assertEqual(result, "translated")
        sdk.Anthropic.assert_called_once_with(api_key="fake-key", max_retries=0)
        client.messages.create.assert_called_once()

    def test_empty_text_and_missing_key_keep_no_request_fallback(self):
        sdk, _ = self._fake_sdk()
        with (
            mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}, clear=True),
            mock.patch.dict(sys.modules, {"anthropic": sdk}),
        ):
            self.assertEqual(translate_text("  "), "")
            sdk.Anthropic.assert_not_called()

        sdk, _ = self._fake_sdk()
        with (
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.dict(sys.modules, {"anthropic": sdk}),
        ):
            self.assertEqual(translate_text("A definition"), "")
            sdk.Anthropic.assert_not_called()

    def test_missing_sdk_keeps_no_request_fallback(self):
        with (
            mock.patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake-key"}, clear=True),
            mock.patch.dict(sys.modules, {"anthropic": None}),
        ):
            self.assertEqual(translate_text("A definition"), "")

    def test_batch_forwards_the_approved_ceiling_to_each_request(self):
        texts = ["First definition", "Second definition"]
        budget = estimate_batch_max_cost_usd(texts)
        with mock.patch("translate.translate_text", side_effect=["one", "two"]) as call:
            result = translate_batch(texts, delay=0, max_budget_usd=budget)

        self.assertEqual(result, ["one", "two"])
        self.assertEqual(
            call.call_args_list,
            [
                mock.call(text, "en", max_budget_usd=budget)
                for text in texts
            ],
        )

    def test_batch_over_budget_never_starts_a_request(self):
        texts = ["First definition"]
        with mock.patch("translate.translate_text") as call:
            with self.assertRaises(ValueError):
                translate_batch(texts, delay=0, max_budget_usd=0.000001)
        call.assert_not_called()

    def test_standalone_cli_forwards_approved_budget(self):
        with (
            mock.patch("translate.is_available", return_value=True),
            mock.patch("translate.translate_text", return_value="Translation") as call,
            mock.patch("builtins.print"),
        ):
            exit_code = main(
                [
                    "A definition",
                    "--confirm-api-cost",
                    "--max-budget-usd",
                    "1.0",
                ]
            )

        self.assertEqual(exit_code, 0)
        call.assert_called_once_with(
            "A definition", "en", max_budget_usd=1.0
        )

    def test_standalone_cli_rejects_over_budget_before_availability_or_request(self):
        with (
            mock.patch("translate.is_available") as available,
            mock.patch("translate.translate_text") as call,
            mock.patch("builtins.print"),
        ):
            exit_code = main(
                [
                    "A definition",
                    "--confirm-api-cost",
                    "--max-budget-usd",
                    "0.000001",
                ]
            )

        self.assertEqual(exit_code, 1)
        available.assert_not_called()
        call.assert_not_called()


if __name__ == "__main__":
    unittest.main()
