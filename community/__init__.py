"""Rule-aware community marketing intelligence."""

from .content_strategy import ContentStrategy, build_content_strategy
from .discovery import RankedCommunity, SubredditCandidate, rank_subreddits
from .intelligence import RedditIntelligenceInput, build_reddit_opportunity
from .models import CommunityOpportunity, CommunityPolicy, CommunitySignals
from .pain import DiscussionSample, PainMiningResult, PainSignal, mine_pains
from .reddit import analyze_reddit_opportunity
from .rules import RuleEvidence, analyze_rule_evidence

__all__ = [
    "CommunityOpportunity",
    "CommunityPolicy",
    "CommunitySignals",
    "ContentStrategy",
    "DiscussionSample",
    "PainMiningResult",
    "PainSignal",
    "RankedCommunity",
    "RedditIntelligenceInput",
    "RuleEvidence",
    "SubredditCandidate",
    "analyze_reddit_opportunity",
    "analyze_rule_evidence",
    "build_content_strategy",
    "build_reddit_opportunity",
    "mine_pains",
    "rank_subreddits",
]
