# Training Roadmap: From Rule-Based Prototype to Data-Trained Application

## Current State

The application is a working prototype with explicit rules, claim ontology, evidence retrieval, and regression tests.

That makes the current system:

- explainable;
- inspectable;
- reproducible;
- useful for generating a training dataset.

It does **not** yet make the system a trained ML/NLP application.

## Goal

Train models that generalize to unfamiliar solar-sales wording while preserving the current evidence and explainability architecture.

## Dataset Design

Each training record should retain the original pitch text plus annotations at several levels.

### Pitch-Level Labels

- in scope / out of scope;
- overall persuasion intensity;
- presence of multi-step narrative;
- jurisdiction.

### Sentence-Level Labels

- persuasion techniques (multi-label);
- factual-claim present / absent;
- claim boundaries;
- implied vs explicit claim;
- requested customer action.

### Claim-Level Labels

- standardized claim family;
- claim normalization;
- causal vs descriptive claim;
- severity/consumer consequence;
- evidence requirement.

### Evidence-Level Labels

- relevant / irrelevant;
- supports / contradicts / contextualizes;
- source authority tier;
- freshness status;
- sufficient / insufficient for verdict.

## Labeling Workflow

A robust process should use at least two independent reviewers for a subset of data.

Measure agreement using metrics appropriate to the label type, for example:

- Cohen's kappa for categorical labels;
- F1 for span/claim extraction;
- Jaccard or multilabel agreement for persuasion techniques.

Disagreements should be adjudicated and used to improve the annotation guide.

## Candidate Modeling Approaches

### Baseline 1 — Existing Rules

Keep the current system as the explainable baseline.

### Baseline 2 — TF-IDF + Linear Models

Useful for interpretable claim-family and persuasion classification benchmarks.

### Model 3 — Sentence Embeddings + Classifier

Use semantic representations to handle paraphrases that do not share the configured phrases.

### Model 4 — Transformer Multi-Label Classifier

Potential target for persuasion/claim-family prediction once sufficient labeled data exists.

### Retrieval Model

Evaluate semantic evidence retrieval separately from claim classification.

Possible metrics:

- Recall@K;
- Precision@K;
- Mean Reciprocal Rank;
- nDCG.

## Train / Validation / Test Strategy

Avoid randomly splitting near-duplicate scripts across train and test.

Prefer grouping by pitch/script source so the test set contains genuinely unseen wording.

A starting structure could be:

```text
70% train
15% validation
15% held-out test
```

with a separate adversarial/paraphrase challenge set.

## Model Evaluation

### Claim Extraction

- precision;
- recall;
- F1;
- exact/partial span match.

### Claim Classification

- macro F1;
- per-class precision/recall;
- confusion matrix.

### Persuasion Multi-Label Classification

- micro/macro F1;
- subset accuracy;
- label-wise recall.

False negatives should receive particular attention because the product requirement is that relevant claims should not silently disappear.

## Confidence Calibration

The current confidence numbers are heuristic ranking values.

Before production, predicted confidence should be calibrated on held-out data using techniques such as:

- reliability curves;
- Brier score;
- expected calibration error;
- Platt scaling or isotonic regression where appropriate.

## Human-in-the-Loop Design

Even after training, the evidence layer should preserve reviewer visibility.

A production workflow could allow an analyst to:

- accept/reject extracted claims;
- correct a claim family;
- approve evidence;
- mark a source stale;
- add a new evidence proposition;
- feed corrections back into the training dataset.

## Production Readiness Criteria

Before public deployment:

- stable held-out performance;
- documented false-negative analysis;
- confidence calibration;
- source-refresh governance;
- jurisdiction-aware evidence filtering;
- privacy review;
- legal/compliance review;
- user-facing disclaimers;
- monitoring/logging;
- rollback/versioning for evidence updates.

## Expansion Path

Once Massachusetts performance is validated, the evidence registry can expand state-by-state while the core text-analysis models remain shared.
