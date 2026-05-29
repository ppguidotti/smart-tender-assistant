import json
import sys
from pathlib import Path

from scoring.adapter import enriched_gap_analysis_to_scoring
from scoring.engine import compute_scoring
from scoring.enrichment import enrich_gap_analysis_with_llm


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scoring.run_scoring <gap_analysis_json>")
        sys.exit(1)

    input_path = sys.argv[1]

    with open(input_path) as f:
        gap_analysis = json.load(f)

    print("\n=== RUNNING LLM ENRICHMENT ===\n")

    enrichment = enrich_gap_analysis_with_llm(gap_analysis)

    print(json.dumps(enrichment, indent=2, ensure_ascii=False))

    requirements = enriched_gap_analysis_to_scoring(
        gap_analysis,
        enrichment,
    )

    print("\n=== NORMALIZED REQUIREMENTS ===\n")

    for req in requirements:
        print(
            json.dumps(
                req.model_dump(mode="json"),
                indent=2,
                ensure_ascii=False,
            )
        )

    result = compute_scoring(requirements)

    print("\n=== SCORING RESULT ===\n")

    print(f"Decision: {result.decision.value}")
    print(f"Score: {result.final_score}")

    print("\nBreakdown:")
    print(json.dumps(result.breakdown.model_dump(), indent=2))

    print("\nRationale:")
    for item in result.rationale:
        print(f"- {item}")

    print("\nRecommended actions:")
    for item in result.recommended_actions:
        print(f"- {item}")


    Path("outputs/scoring").mkdir(parents=True, exist_ok=True)

    with open("outputs/scoring/enrichment.json", "w") as f:
        json.dump(enrichment, f, indent=2, ensure_ascii=False)

    with open("outputs/scoring/normalized_requirements.json", "w") as f:
        json.dump(
            [r.model_dump(mode="json") for r in requirements],
            f,
            indent=2,
            ensure_ascii=False,
        )

    with open("outputs/scoring/scoring_result.json", "w") as f:
        json.dump(
            result.model_dump(mode="json"),
            f,
            indent=2,
            ensure_ascii=False,
        )
    
    print("\nSaved:")
    print("- outputs/scoring/enrichment.json")
    print("- outputs/scoring/normalized_requirements.json")
    print("- outputs/scoring/scoring_result.json")

if __name__ == "__main__":
    main()