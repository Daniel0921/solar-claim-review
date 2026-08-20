# Project Evolution: From Loose Idea to Analytical Pipeline

This project did not begin with a finalized architecture. It began with a much less structured question: **could a computer help explain why a solar sales pitch felt misleading or overly aggressive?**

Documenting that evolution is useful because many of the current design decisions came directly from prototype failures.

## Stage 1 — Manual Pitch Review

The first version of the idea was effectively manual analysis. A pitch could be read and flagged for statements such as:

- "no cost";
- "fixed bill";
- "you have to qualify";
- "the utility sent us";
- "your bill disappears";
- "it has to be cheaper."

This proved the basic concept but did not create a reusable system.

### Lesson

The project needed to convert subjective observations into explicit analytical categories.

## Stage 2 — Rule-Based Phrase Detection

The first software prototype used regular expressions and predefined phrase families.

This made the system repeatable, but it had two major weaknesses:

1. it could miss softer paraphrases;
2. it treated a full pitch too much like a keyword list.

### Lesson

Language risk is contextual. Several moderate phrases can combine into a much stronger consumer impression.

## Stage 3 — Persuasion + Fact Checking Become Separate Problems

The architecture split into two concepts:

```text
HOW THE PITCH IS PRESENTED
```

and:

```text
WHETHER THE FACTUAL CLAIM IS SUPPORTED
```

This was a major conceptual shift. A persuasive tactic and a factual error are different analytical objects.

## Stage 4 — Evidence Dictionary

Hard-coded fact-check responses were not scalable. The project therefore introduced:

- source registry;
- evidence records;
- authority scoring;
- freshness;
- claim relevance;
- source tiers.

This turned fact checking from a set of canned answers into an evidence-retrieval problem.

### Lesson

A trustworthy system should know not only *what it thinks*, but *which reviewed evidence it relied on*.

## Stage 5 — Character-Window Failure

The persuasion engine initially displayed text by taking a fixed number of characters around a regex match.

That produced unusable fragments such as partial words and sentences.

### Fix

The parser was rebuilt to resolve complete semantic sentences before rendering quotes.

### Lesson

A correct classifier can still produce a poor product if the explanation layer destroys context.

## Stage 6 — One Winning Claim Was Not Enough

A full sales pitch can claim simultaneously that:

- renewable-energy requirements exist;
- those requirements cause delivery charges;
- delivery charges fund solar;
- solar costs nothing;
- the utility bill disappears;
- the solar payment is fixed;
- savings are guaranteed;
- the homeowner must qualify.

Mapping the whole pitch to one label caused the evidence engine to fact-check whichever claim happened to win the classifier.

### Fix

The project moved to multi-claim decomposition:

```text
Pitch
  ↓
Extract Claims
  ↓
Classify Each Claim
  ↓
Retrieve Evidence for Each Claim
```

### Lesson

Document-level classification was the wrong abstraction. The atomic unit for evidence review is the claim.

## Stage 7 — Narrative Reconstruction

Even claim-by-claim fact checking did not fully explain *why a pitch felt convincing*.

The project introduced narrative analysis to examine how a script builds a story:

```text
premise → explanation → solution → action
```

This allows the report to say that individual facts may be real while the causal chain connecting them is unsupported.

## Stage 8 — False-Negative Fallback Rules

Another failure appeared when a solar-related sentence did not match a configured claim family. The app could return no analysis.

That behavior was unacceptable for a review system.

### Fix

Mandatory routing rules were introduced:

- every in-scope input receives a response;
- known claims use the normal evidence path;
- unknown relevant claims return `REQUIRES_ADDITIONAL_EVIDENCE`;
- off-topic text returns `OUTSIDE_PROJECT_SCOPE`.

### Lesson

A system should expose uncertainty rather than hide it behind an empty result.

## Stage 9 — Evidence Portfolio Expansion

The source portfolio expanded to 50 reviewed sources with a primary-source-first hierarchy.

The current split is:

- 38 Massachusetts/public/utility primary-tier sources;
- 12 independent/private sources.

This makes it possible to compare regulatory evidence with industry/market perspectives without treating them as equally authoritative.

## Stage 10 — Current Prototype

The current Streamlit prototype now supports:

- full-pitch input;
- scope routing;
- multi-claim extraction;
- manipulation/persuasion analysis;
- narrative reconstruction;
- ethical assessment benchmarking;
- evidence retrieval;
- freshness-aware source ranking;
- claim-by-claim verdict direction;
- explicit unknown-evidence behavior;
- automated regression tests.

## The Next Evolution — Training on Data

The prototype is still rule-based. That is useful because it makes the logic inspectable, but it limits linguistic flexibility and prevents the current scores from being statistically calibrated.

The next stage is a labeled corpus.

The target evolution is:

```text
Transparent Rules Prototype
        ↓
Human-Labeled Pitch Dataset
        ↓
Train / Validation / Test Split
        ↓
Semantic Claim Extraction Model
        ↓
Persuasion Multi-Label Classifier
        ↓
Evidence Retrieval Evaluation
        ↓
Confidence Calibration
        ↓
Production Validation
```

At that point the rule system can remain as:

- a baseline;
- a fallback;
- an explainability layer;
- a regression-testing framework.

The important outcome of this evolution is not simply a Streamlit app. It is a reusable pipeline for turning messy qualitative language into structured, evidence-backed analysis.
