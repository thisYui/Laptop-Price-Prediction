from __future__ import annotations

import json

import requests

from app.backend.predictor_service import load_environment, predict_from_text


def main() -> None:
    load_environment()

    print("=== Laptop Price Prediction CLI ===")
    user_input = input("Describe the laptop: ").strip()
    if not user_input:
        print("Error: input is empty.")
        return

    try:
        result = predict_from_text(user_input)
    except requests.exceptions.RequestException as exc:
        print(f"Gemini API request failed: {exc}")
        return
    except Exception as exc:
        print(f"Prediction failed: {exc}")
        return

    print("\n=== Encoder-Ready Raw JSON ===")
    print(json.dumps(result["raw_features"], indent=4, ensure_ascii=False))
    print("\n=== Active Encoded Features ===")
    print(json.dumps(result["active_features"], indent=4, ensure_ascii=False))
    print("\n=== Prediction JSON ===")
    print(json.dumps({"predicted_price": result["predicted_price"]}, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
