import os

import pandas as pd
import pytest

from lac_validator.config import column_names
from lac_validator.datastore import create_datastore
from lac_validator.ingress import read_from_text


@pytest.fixture(scope="session")
def dummy_input_files():
    return {
        "header.csv": "Header",
        "episodes.csv": "Episodes",
        "reviews.csv": "Reviews",
        "uasc.csv": "UASC",
        "oc2.csv": "OC2",
        "oc3.csv": "OC3",
        "ad1.csv": "AD1",
        "placed_for_adoption.csv": "PlacedAdoption",
        "previous_permanence.csv": "PrevPerm",
        "missing.csv": "Missing",
        "sw_episodes.csv": "SWEpisodes",
    }


@pytest.fixture(scope="session")
def dummy_metadata():
    return {
        "collectionYear": "2019/20",
        "localAuthority": "test_LA",
    }


@pytest.fixture(scope="session")
def dummy_input_data(dummy_input_files, dummy_metadata):
    fake_data_dir = os.path.join(os.path.dirname(__file__), "fake_data")

    dummy_uploads = []
    for filename in dummy_input_files.keys():
        path = os.path.join(fake_data_dir, filename)

        with open(path, "rb") as live_file:
            bytez = live_file.read()

        dummy_uploads.append(
            {"name": filename, "file_content": bytez, "description": "This year"}
        )
        dummy_uploads.append(
            {"name": filename, "file_content": bytez, "description": "Prev year"}
        )

    dummy_dfs, extra_metadata = read_from_text(dummy_uploads)
    dummy_metadata.update(extra_metadata)
    return create_datastore(dummy_dfs, dummy_metadata)


@pytest.fixture(scope="session")
def dummy_empty_input(dummy_metadata):
    out = {
        table_name: pd.DataFrame(columns=c) for table_name, c in column_names.items()
    }
    out_last = {
        table_name + "_last": pd.DataFrame(columns=c)
        for table_name, c in column_names.items()
    }
    return create_datastore({**out, **out_last}, dummy_metadata)


@pytest.fixture(scope="session")
def dummy_chscp():
    def read_file(path):
        with open(path, mode="rb") as f:
            return f.read()

    fake_ch_dir = os.path.join(os.path.dirname(__file__), "fake_data", "ch_fake.xlsx")
    fake_scp_dir = os.path.join(os.path.dirname(__file__), "fake_data", "scp_fake.xlsx")
    combined_fake_dir = os.path.join(
        os.path.dirname(__file__), "fake_data", "combined_scp_ch_fake.xlsx"
    )
    scpch_assisted_dir = os.path.join(
        os.path.dirname(__file__), "fake_data", "scpch_assisted.xlsx"
    )
    combined_2025_fake_dir = os.path.join(
        os.path.dirname(__file__), "fake_data", "scp_ch_2025_fake.xlsx"
    )
    dummy_ch = read_file(fake_ch_dir)
    dummy_scp = read_file(fake_scp_dir)
    dummy_combined = read_file(combined_fake_dir)
    dummy_combined_assisted = read_file(scpch_assisted_dir)
    dummy_combined_2025 = read_file(combined_2025_fake_dir)
    return (
        dummy_ch,
        dummy_scp,
        fake_ch_dir,
        fake_scp_dir,
        combined_fake_dir,
        combined_2025_fake_dir,
        dummy_combined,
        dummy_combined_assisted,
        dummy_combined_2025,
    )
