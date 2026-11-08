import json

import pytest

from backend.config import DATA_DIR
from backend.utils.data_loader import (
    DATASET_NAMES, DatasetError, load_dataset, load_dataset_safe, search_records,
    validate_all, validate_dataset, validate_relationships,
)


@pytest.mark.parametrize("name", DATASET_NAMES)
def test_dataset_is_valid(name):
    assert validate_dataset(name) == []


def test_relationships_are_consistent():
    assert validate_relationships() == []


def test_validate_all_report_is_clean():
    assert all(not problems for problems in validate_all().values())


def test_jobs_are_clearly_labelled_samples():
    content = json.loads((DATA_DIR / "jobs.json").read_text(encoding="utf-8"))
    assert "not live vacancies" in content["disclaimer"]
    for job in content["jobs"]:
        assert job["is_demo"] is True
        assert "Sample" in job["company"]
        assert "not a live vacancy" in job["listing_label"]


def test_resource_urls_are_https():
    assert all(r["url"].startswith("https://") for r in load_dataset("learning_resources"))


def test_missing_file_is_handled(tmp_path):
    with pytest.raises(DatasetError):
        load_dataset("careers", data_dir=tmp_path)
    assert validate_dataset("careers", data_dir=tmp_path)


def test_invalid_json_is_reported(tmp_path):
    (tmp_path / "careers.json").write_text("{not json", encoding="utf-8")
    assert "not valid JSON" in validate_dataset("careers", data_dir=tmp_path)[0]


def test_unknown_dataset_name():
    with pytest.raises(DatasetError):
        load_dataset("unknown")
    assert load_dataset_safe("unknown") == []


def test_search_records_ranks_by_matches():
    records = [{"t": "python basics"}, {"t": "python data science"}, {"t": "cooking"}]
    result = search_records(records, "python data", ("t",))
    assert result[0]["t"] == "python data science" and len(result) == 2
