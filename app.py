from pathlib import Path
import streamlit as st

from evidence_engine.database import seed_database, counts, list_sources
from evidence_engine.freshness import freshness_score
from evidence_engine.pitch_pipeline import analyze_entire_pitch
from evidence_engine.ethical_benchmark import evaluate_against_handbook

ROOT = Path(__file__).resolve().parent
DB = ROOT/"data"/"solar_claim_evidence.db"
ONTOLOGY = ROOT/"data"/"claim_ontology.json"

seed_database(DB, ROOT/"data/source_registry.json", ROOT/"data/seed_evidence.json")

st.set_page_config(page_title="Solar Claim Review", page_icon="☀️", layout="wide")
st.title("Solar Claim Review")
st.write(
    "Paste an entire residential solar sales pitch. The review follows three stages: "
    "persuasion analysis, narrative reconstruction, and claim-by-claim fact checking."
)

analysis_tab, sources_tab = st.tabs(["Full Pitch Review", "Evidence Library"])

with analysis_tab:
    pitch = st.text_area("Entire pitch", height=360, placeholder="Paste the full pitch here...")

    if st.button("Generate Full Review", type="primary", use_container_width=True):
        if not pitch.strip():
            st.error("Paste a pitch first.")
        else:
            result = analyze_entire_pitch(DB, ONTOLOGY, pitch)

            if not result["scope"]["relevant"]:
                st.warning("Outside project scope")
                st.write(result["scope"]["message"])
                st.stop()

            # ---------------- STEP 1 ----------------
            st.markdown("## 1. Wording & Persuasion Analysis")
            p = result["persuasion"]
            c1, c2 = st.columns(2)
            c1.metric("Persuasion Intensity", p["label"])
            c2.metric("Manipulation / Persuasion Techniques", len(p["signals"]))

            st.caption(
                "This section evaluates how the language tries to move the homeowner psychologically or socially. "
                "It is separate from factual truth, which is handled in Section 3."
            )

            if not p["signals"]:
                st.info(
                    "No configured pressure technique was detected in this wording. "
                    "That does not mean the statement is factual or harmless; any factual "
                    "solar/utility claim is still sent to the claim-by-claim fact-check section below."
                )
            else:
                for signal in p["signals"]:
                    level = "High" if signal.severity >= 8 else ("Moderate" if signal.severity >= 5 else "Low")
                    st.markdown(f"### {signal.label} — {level}")
                    st.markdown("**Pitch language**")
                    st.write(f"“{signal.matched_text}”")
                    st.markdown("**How it functions in the pitch**")
                    st.write(signal.explanation)
                    st.markdown("**Persuasion mechanism**")
                    st.write(signal.mechanism)
                    st.markdown("**Likely effect on the homeowner**")
                    st.write(signal.consumer_effect)
                    st.markdown("**Why the combination can escalate**")
                    st.write(signal.escalation)

            from evidence_engine.pitch_story_analyzer import manipulation_synthesis
            st.markdown("### Combined Manipulation Pattern")
            st.write(manipulation_synthesis(p["signals"]))

            # ---------------- STEP 2 ----------------
            st.markdown("## 2. The Story the Pitch Is Telling")

            steps = result["narrative"]["steps"]

            if steps:
                beginning = " ".join(steps[0]["evidence"])
                middle = " ".join(steps[1]["evidence"]) if len(steps) > 1 else beginning
                ending = " ".join(steps[-1]["evidence"])

                st.markdown("### What story is being told?")
                st.write(
                    "Rather than treating the pitch as a list of disconnected sentences, this section "
                    "looks at the overall narrative it asks the homeowner to accept."
                )

                st.markdown("**Opening premise**")
                st.write(beginning)

                st.markdown("**How the pitch develops that premise**")
                st.write(middle)

                st.markdown("**Where the pitch is trying to lead the homeowner**")
                st.write(ending)

                st.markdown("**Narrative interpretation**")
                st.write(
                    "The important question is not only whether each sentence is individually persuasive, "
                    "but how the pitch links them together. The opening creates the frame, the middle supplies "
                    "the explanation, benefit, pressure, or qualification logic, and the ending turns that story "
                    "into an intended conclusion or next action."
                )
            else:
                st.markdown("### What story is being told?")
                st.write(
                    "A distinct narrative sequence could not be reconstructed from the available wording. "
                    "The pitch is still reviewed for persuasion techniques and factual claims."
                )

            st.markdown("### Ethical Assessment Benchmark")
            st.caption(
                "Pitch-specific comparison against the project's handbook. "
                "The handbook is an ethical assessment benchmark only; it is not fact-check evidence."
            )

            benchmark_results = evaluate_against_handbook(pitch)

            for item in benchmark_results:
                st.markdown(f"#### {item['principle']} — {item['status']}")
                st.markdown("**What this pitch is doing**")
                st.write(item["observed"])
                st.markdown("**Handbook benchmark**")
                st.write(item["benchmark"])
                st.markdown("**More responsible approach**")
                st.write(item["improvement"])

            # ---------------- STEP 3 ----------------
            st.markdown("## 3. Claim-by-Claim Fact Check")
            claims = result["claims"]

            if not claims:
                st.warning(
                    "No independently testable claims were matched confidently to the current evidence library."
                )
            else:
                st.write(
                    f"The engine extracted **{len(claims)} independently testable claim(s)**. "
                    "Each claim is classified and researched separately."
                )

                for idx, claim in enumerate(claims, 1):
                    st.markdown(f"### Claim {idx}: {claim['display_name']}")
                    st.markdown("**What the pitch says**")
                    st.write(f"“{claim['claim_text']}”")
                    st.markdown(f"**Fact-check direction:** `{claim['fact_check_direction']}`")

                    if claim.get("fallback"):
                        st.warning(
                            "This is a solar/utility-related factual statement, but it does not yet map "
                            "to a reviewed claim family. The system is deliberately returning a response "
                            "instead of ignoring it."
                        )
                        if claim.get("numeric_terms"):
                            st.write("**Specific terms requiring verification:** " + ", ".join(claim["numeric_terms"]))
                        st.write(
                            "**Next verification step:** identify the exact program, utility tariff, company "
                            "policy, contract rule, or eligibility document that supports this statement."
                        )
                        continue

                    if not claim["evidence"]:
                        st.warning(
                            "The claim was detected, but the reviewed evidence library does not yet contain "
                            "enough evidence to issue a source-backed direction. Current status: "
                            "`NOT_ENOUGH_EVIDENCE`."
                        )
                        continue

                    for j, e in enumerate(claim["evidence"], 1):
                        with st.expander(
                            f"Evidence {j}: {e['publisher']} — {e['title']}",
                            expanded=(j == 1)
                        ):
                            st.write(e["statement"])
                            st.write(f"**Evidence stance:** {e['stance']}")
                            if e["notes"]:
                                st.write(f"**Why it matters:** {e['notes']}")

                            st.code(
                                f"SOURCE AUTHORITY    {e['authority']:.2f}\n"
                                f"SOURCE RELEVANCE    {e['relevance']:.2f}\n"
                                f"SOURCE FRESHNESS    {e['freshness']:.2f}\n"
                                f"CLAIM MATCH         {e['claim_match']:.2f}\n"
                                f"-------------------------\n"
                                f"EVIDENCE CONFIDENCE {e['evidence_confidence']:.2f}"
                            )
                            if e["missing_information"]:
                                st.markdown("**Still needed to fully verify**")
                                for item in e["missing_information"]:
                                    st.write(f"- {item}")
                            if e["needs_review"]:
                                st.warning("The underlying source changed after this evidence was reviewed.")
                            st.markdown(f"Source: {e['url']}")

                    st.divider()

                st.markdown("### Evidence Summary")
                summary = result["summary"]
                st.metric("Claims Identified", summary["claims_identified"])
                for direction, count in sorted(
                    summary["direction_counts"].items(),
                    key=lambda x: (-x[1], x[0])
                ):
                    st.write(f"- **{direction}:** {count}")

with sources_tab:
    c = counts(DB)
    st.metric("Verified Sources", c["sources"])
    st.caption(
        "50-source portfolio: 38 primary Massachusetts / National Grid / Eversource / "
        "MassCEC sources and 12 independent/private industry and market sources. "
        "Primary sources are weighted above private sources in fact checking."
    )
    st.info(
        "The Massachusetts Energy Economics & Solar Assessment Handbook is a separate "
        "reference-only ethical assessment benchmark. It is not counted among the 50 verified "
        "fact-check sources and is never used as evidence to prove or disprove a claim."
    )

    for row in list_sources(DB):
        fresh = freshness_score(row["as_of"], row["volatility"])
        with st.expander(f"{row['publisher']} — {row['title']}"):
            st.write(f"**Authority:** {row['authority_score']:.2f}")
            st.write(f"**Freshness:** {fresh:.2f}")
            st.write(f"**Volatility:** {row['volatility']}")
            st.write(f"**As-of:** {row['as_of']}")
            st.write(f"**Last refresh:** {row['last_refreshed'] or 'Not refreshed'}")
            if row["needs_review"]:
                st.warning("Source content changed and reviewed evidence should be rechecked.")
            st.markdown(row["url"])
