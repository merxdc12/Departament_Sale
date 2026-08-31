"""Rule-aware community marketing intelligence."""

from .content_strategy import ContentStrategy, build_content_strategy
from .discovery import RankedCommunity, SubredditCandidate, rank_subreddits
from .intelligence import RedditIntelligenceInput, build_reddit_opportunity
from .memory import CommunityLearning, CommunityMemory, learn_community_history, remember
from .models import CommunityOpportunity, CommunityPolicy, CommunitySignals
from .pain import DiscussionSample, PainMiningResult, PainSignal, mine_pains
from .performance import CommunityPerformance, evaluate_community_performance, performance_from_strategy
from .reddit import analyze_reddit_opportunity
from .rules import RuleEvidence, analyze_rule_evidence

__all__ = [
    "CommunityLearning",
    "CommunityMemory",
    "CommunityOpportunity",
    "CommunityPerformance",
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
    "evaluate_community_performance",
    "learn_community_history",
    "mine_pains",
    "performance_from_strategy",
    "rank_subreddits",
    "remember",
]
