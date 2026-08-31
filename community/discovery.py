from dataclasses import dataclass


@dataclass(frozen=True)
class SubredditCandidate:
    name: str
    title: str = ""
    description: str = ""
    subscribers: int = 0
    active_users: int = 0
    matched_terms: tuple[str, ...] = ()


@dataclass(frozen=True)
class RankedCommunity:
    name: str
    relevance_score: int
    activity_score: int
    audience_score: int
    discovery_score: int
    matched_terms: tuple[str, ...]


def _bounded_ratio(value: int, reference: int) -> int:
    if reference <= 0:
        return 0
    return min(100, round(value / reference * 100))


def rank_subreddits(
    candidates: tuple[SubredditCandidate, ...],
    *,
    target_terms: tuple[str, ...],
) -> tuple[RankedCommunity, ...]:
    """Rank already-discovered public communities without scraping or side effects."""
    normalized_targets = {x.strip().lower() for x in target_terms if x.strip()}
    if not normalized_targets:
        raise ValueError("target_terms must contain at least one non-empty term")

    max_subscribers = max((max(0, x.subscribers) for x in candidates), default=0)
    max_active = max((max(0, x.active_users) for x in candidates), default=0)
    ranked = []

    for item in candidates:
        if item.subscribers < 0 or item.active_users < 0:
            raise ValueError("subscriber and active-user counts cannot be negative")

        corpus = " ".join((item.name, item.title, item.description)).lower()
        direct_matches = tuple(sorted(term for term in normalized_targets if term in corpus))
        supplied_matches = tuple(
            sorted({x.strip().lower() for x in item.matched_terms if x.strip()} & normalized_targets)
        )
        matches = tuple(sorted(set(direct_matches) | set(supplied_matches)))
        relevance = round(len(matches) / len(normalized_targets) * 100)
        activity = _bounded_ratio(item.active_users, max_active)
        audience = _bounded_ratio(item.subscribers, max_subscribers)
        score = round(relevance * 0.55 + activity * 0.25 + audience * 0.20)
        ranked.append(
            RankedCommunity(
                name=item.name,
                relevance_score=relevance,
                activity_score=activity,
                audience_score=audience,
                discovery_score=score,
                matched_terms=matches,
            )
        )

    ranked.sort(key=lambda x: (x.discovery_score, x.relevance_score, x.activity_score), reverse=True)
    return tuple(ranked)
