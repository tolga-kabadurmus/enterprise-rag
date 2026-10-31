import os
import unittest
from unittest.mock import patch

from pydantic import ValidationError

from diagnostic_settings import QdrantDiagnosticSettings, S3DiagnosticSettings


class DiagnosticSettingsTests(unittest.TestCase):
    def test_loads_s3_settings_from_environment(self) -> None:
        environment = {
            "S3_ENDPOINT_URL": "http://localhost:9000",
            "S3_ACCESS_KEY_ID": "test-access-key",
            "S3_SECRET_ACCESS_KEY": "test-secret-key",
        }

        with patch.dict(os.environ, environment, clear=True):
            settings = S3DiagnosticSettings(_env_file=None)

        self.assertEqual(str(settings.endpoint_url), "http://localhost:9000/")
        self.assertEqual(settings.access_key_id, "test-access-key")
        self.assertEqual(
            settings.secret_access_key.get_secret_value(),
            "test-secret-key",
        )
        self.assertEqual(settings.region, "us-east-1")

    def test_rejects_missing_qdrant_secret(self) -> None:
        with patch.dict(
            os.environ,
            {"QDRANT_URL": "http://localhost:6333"},
            clear=True,
        ):
            with self.assertRaises(ValidationError):
                QdrantDiagnosticSettings(_env_file=None)


if __name__ == "__main__":
    unittest.main()
