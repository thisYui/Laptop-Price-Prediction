from pathlib import Path
import sys

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = PROJECT_ROOT / "artifacts" / "preprocessors" / "feature_config.pkl"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.laptop_encoder import load_feature_config, transform_real_input


@pytest.fixture(scope="module")
def config():
    assert CONFIG_PATH.exists(), f"Missing feature config artifact: {CONFIG_PATH}"
    return load_feature_config(CONFIG_PATH)


def make_sample_df():
    return pd.DataFrame(
        [
            {
                "ram_gb": 16,
                "storage_gb": 512,
                "screen_size_inch": 13.6,
                "brand_grouped": "Apple",
                "model_grouped": "MacBook Air",
                "cpu_brand": "Apple",
                "cpu_tier": "High",
                "gpu_tier": "Apple GPU",
                "storage_type_clean": "SSD",
                "condition_clean": "Mới",
                "warranty_status": "Active",
                "no_info_gpu": False,
            },
            {
                "ram_gb": 8,
                "storage_gb": 256,
                "screen_size_inch": 15.6,
                "brand_grouped": "Dell",
                "model_grouped": "Latitude",
                "cpu_brand": "Intel",
                "cpu_tier": "Mid",
                "gpu_tier": "Integrated - Intel",
                "storage_type_clean": "SSD",
                "condition_clean": "Đã sử dụng (chưa sửa chữa)",
                "warranty_status": "not_active",
                "no_info_gpu": False,
            },
            {
                "ram_gb": 32,
                "storage_gb": 1024,
                "screen_size_inch": 16,
                "brand_grouped": "Lenovo",
                "model_grouped": "ThinkPad",
                "cpu_brand": "Intel",
                "cpu_tier": "High-end",
                "gpu_tier": "RTX 4000",
                "storage_type_clean": "SSD",
                "condition_clean": "Mới",
                "warranty_status": "Manufacturer",
                "no_info_gpu": False,
            },
        ]
    )


def test_load_feature_config():
    assert CONFIG_PATH.exists(), f"Missing feature config artifact: {CONFIG_PATH}"
    feature_config = load_feature_config(CONFIG_PATH)
    assert isinstance(feature_config, dict)
    assert "final_feature_cols" in feature_config
    assert isinstance(feature_config["final_feature_cols"], list)
    assert len(feature_config["final_feature_cols"]) > 0


def test_transform_real_input_basic_schema(config):
    sample_df = make_sample_df()
    X = transform_real_input(sample_df, feature_config=config)

    assert list(X.columns) == config["final_feature_cols"]
    assert X.shape[0] == sample_df.shape[0]
    assert X.isna().sum().sum() == 0
    assert len(X.columns) == len(set(X.columns))
    assert X.select_dtypes(include=["object", "category", "string"]).columns.tolist() == []


def test_unknown_brand_model_becomes_rare_if_columns_exist(config):
    sample_df = pd.DataFrame(
        [
            {
                "ram_gb": 16,
                "storage_gb": 512,
                "screen_size_inch": 14,
                "brand_grouped": "UnknownBrandXYZ",
                "model_grouped": "UnknownModelXYZ",
                "cpu_brand": "Intel",
                "cpu_tier": "High",
                "gpu_tier": "Integrated - Intel",
                "storage_type_clean": "SSD",
                "condition_clean": "Mới",
                "warranty_status": "Active",
                "no_info_gpu": False,
            }
        ]
    )
    X = transform_real_input(sample_df, feature_config=config)

    assert list(X.columns) == config["final_feature_cols"]
    if "brand_is_rare" in config["final_feature_cols"]:
        assert X["brand_is_rare"].iloc[0] == 1
    if "model_is_rare" in config["final_feature_cols"]:
        assert X["model_is_rare"].iloc[0] == 1
    if "brand_Other" in config["final_feature_cols"]:
        assert X["brand_Other"].iloc[0] == 1
    if "model_Other" in config["final_feature_cols"]:
        assert X["model_Other"].iloc[0] == 1


def test_missing_optional_columns_does_not_crash(config):
    sample_df = pd.DataFrame(
        [
            {
                "ram_gb": 8,
                "storage_gb": 256,
                "screen_size_inch": 15.6,
                "brand_grouped": "Dell",
                "model_grouped": "Latitude",
                "cpu_brand": "Intel",
                "cpu_tier": "Mid",
                "gpu_tier": "Integrated - Intel",
                "storage_type_clean": "SSD",
            }
        ]
    )
    X = transform_real_input(sample_df, feature_config=config)

    assert list(X.columns) == config["final_feature_cols"]
    assert X.isna().sum().sum() == 0


def test_gpu_edge_cases(config):
    sample_df = pd.DataFrame(
        [
            {"gpu_tier": "Apple GPU", "brand_grouped": "Apple", "model_grouped": "MacBook Air"},
            {"gpu_tier": "Other", "brand_grouped": "Dell", "model_grouped": "Latitude"},
            {"gpu_tier": "RTX 4000", "brand_grouped": "Lenovo", "model_grouped": "ThinkPad"},
            {"gpu_tier": None, "brand_grouped": "HP", "model_grouped": "Elitebook"},
        ]
    )
    X = transform_real_input(sample_df, feature_config=config)

    assert list(X.columns) == config["final_feature_cols"]
    assert X.isna().sum().sum() == 0
    if "gpu_tier_ord_filled" in config["final_feature_cols"]:
        assert X["gpu_tier_ord_filled"].isna().sum() == 0
    if "gpu_missing" in config["final_feature_cols"]:
        assert X["gpu_missing"].iloc[1] == 1
        assert X["gpu_missing"].iloc[3] == 1


def test_transform_does_not_mutate_input(config):
    sample_df = make_sample_df()
    sample_copy = sample_df.copy(deep=True)

    transform_real_input(sample_df, feature_config=config)

    pd.testing.assert_frame_equal(sample_df, sample_copy)


def test_validate_no_raw_columns_in_output(config):
    sample_df = make_sample_df()
    X = transform_real_input(sample_df, feature_config=config)
    raw_columns = {
        "target_price",
        "log_target_price",
        "source",
        "brand_grouped",
        "model_grouped",
        "cpu_brand",
        "cpu_tier",
        "gpu_tier",
        "gpu_raw",
        "gpu_type",
        "gpu_tier_clean",
        "storage_type_clean",
        "condition_clean",
        "warranty_status",
        "no_info_gpu",
    }

    assert raw_columns.isdisjoint(X.columns)
