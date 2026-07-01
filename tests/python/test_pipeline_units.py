import unittest

from python_pipeline.extract_requirements import extract_job
from python_pipeline.normalize import normalize_text, slugify


class PipelineUnitTests(unittest.TestCase):
    def test_normalize_text_collapses_spaces_and_blank_lines(self):
        self.assertEqual(normalize_text("Hello   world\r\n\r\n\r\nNext"), "Hello world\n\nNext")

    def test_slugify_is_stable_for_file_names(self):
        self.assertEqual(slugify("Contoso Cloud / Senior .NET Engineer"), "contoso-cloud-senior-net-engineer")

    def test_extract_job_detects_core_fields_and_skills(self):
        text = """Company: Example
Role: Senior Full-Stack Engineer
Location: Remote

- Strong React and TypeScript.
- Backend with C#/.NET and SQL.
"""
        job = extract_job(text)
        self.assertEqual(job["company"], "Example")
        self.assertEqual(job["role"], "Senior Full-Stack Engineer")
        self.assertIn("react", job["required_skills"])
        self.assertIn(".net", job["required_skills"])
        self.assertIn("remote", job["work_mode"])
        self.assertIn("senior", job["seniority"])


if __name__ == "__main__":
    unittest.main()
