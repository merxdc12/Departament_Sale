from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class DiscussionSample:
    text: str
    score: int = 0
    comments: int = 0


@dataclass(frozen=True)
class PainSignal:
    phrase: str
    mentions: int
    weighted_mentions: int


@dataclass(frozen=True)
class PainMiningResult:
    pains: tuple[PainSignal, ...]
    intent_mentions: int
    question_mentions: int
    sample_count: int


DEFAULT_PAIN_PHRASES = (
    "problem",
    "issue",
    "struggling",
    "frustrating",
    "annoying",
    "need help",
    "looking for",
    "recommend",
    "alternative",
    "where can i find",
)

PURCHASE_INTENT_PHRASES = (
    "buy",
    "purchase",
    "recommend",
    "looking for",
    "where can i find",
    "best option",
    "worth it",
)


def mine_pains(
    samples: tuple[DiscussionSample, ...],
    *,
    pain_phrases: tuple[str, ...] = DEFAULT_PAIN_PHRASES,
) -> PainMiningResult:
    """Mine supplied public discussion text without fabricating missing evidence."""
    clean_phrases = tuple(dict.fromkeys(x.strip().lower() for x in pain_phrases if x.strip()))
    if not clean_phrases:
        raise ValueError("pain_phrases must contain at least one non-empty phrase")

    counts = Counter()
    weighted = Counter()
    intent_mentions = 0
    question_mentions = 0

    for sample in samples:
        if sample.score < 0 or sample.comments < 0:
            raise ValueError("discussion score and comments cannot be negative")
        text = sample.text.strip().lower()
        if not text:
            continue

        engagement_weight = 1 + min(sample.score, 100) // 25 + min(sample.comments, 100) // 25
        for phrase in clean_phrases:
            occurrences = text.count(phrase)
            if occurrences:
                counts[phrase] += occurrences
                weighted[phrase] += occurrences * engagement_weight

        intent_mentions += sum(text.count(x) for x in PURCHASE_INTENT_PHRASES)
        question_mentions += text.count("?")

    pains = tuple(
        PainSignal(phrase=phrase, mentions=counts[phrase], weighted_mentions=weighted[phrase])
        for phrase in sorted(counts, key=lambda x: (weighted[x], counts[x], x), reverse=True)
    )
    return PainMiningResult(
        pains=pains,
        intent_mentions=intent_mentions,
        question_mentions=question_mentions,
        sample_count=sum(1 for x in samples if x.text.strip()),
    )
