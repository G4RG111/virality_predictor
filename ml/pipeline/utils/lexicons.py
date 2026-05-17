"""
Virality signal lexicons.
All phrase matching across dimension extractors uses these centralized lists.
"""
from __future__ import annotations

# ── Hackability (25% weight) ────────────────────────────────────────────────
# Community-discovered alternative uses — SharkNinja's primary viral vector
HACKABILITY_PHRASES: list[str] = [
    "hack", "life hack", "hacked", "hacking",
    "trick", "tip", "tips and tricks",
    "you can also use this for", "you can also use it",
    "i use it for", "i use this for", "i use it as",
    "tried putting", "tried using it", "tried it with",
    "i tried", "decided to try", "wanted to try",
    "i was curious if", "wondered if you could",
    "experiment", "experimenting", "experimented",
    "discovered", "realized you could", "figured out",
    "alternative use", "unexpected use", "didn't expect to use",
    "works great for", "works well for", "works as a",
    "not just for", "more than just", "not only",
    "recipe", "recipes", "diy", "custom",
    "modified", "upgrade", "attached",
    "creative use", "other use", "second use", "multiple uses",
    "also works", "also great for", "also perfect for",
    "use it to make", "use it as a", "doubles as",
    "people don't realize", "secret use", "hidden use",
    "found a way to", "came up with", "brilliant idea",
    "game changer hack", "tiktok hack",
]

# ── Emotional Intensity (17%) ───────────────────────────────────────────────
OBSESSION_PHRASES: list[str] = [
    "obsessed", "obsession", "absolutely obsessed",
    "addicted", "hooked", "can't stop using",
    "living for this", "this changed my life", "life-changing",
    "life changing", "game changer", "game-changer",
    "mind blown", "mindblown", "blew my mind",
    "where has this been all my life", "why didn't i find this sooner",
    "never going back", "can't imagine life without",
    "i'm in love with", "fallen in love with",
    "absolutely love", "i love this so much",
    "can't believe", "unbelievable", "unreal",
    "jaw dropped", "jaw-dropping", "jaw dropping",
    "holy", "omg", "oh my god", "oh my gosh",
    "amazing", "incredible", "phenomenal", "extraordinary",
    "i'm shook", "shook", "floored", "blown away",
    "this is everything", "literally everything",
    "10/10", "100/10", "11/10",
]

EXCITEMENT_INTENSIFIERS: list[str] = [
    "absolutely", "literally", "seriously", "genuinely",
    "honestly", "truly", "completely", "totally",
    "insanely", "ridiculously", "incredibly", "unbelievably",
    "so so so", "sooo", "loveeee", "amazinggg",
]

# ── Shareability (17%) ──────────────────────────────────────────────────────
SOCIAL_PLATFORM_MENTIONS: list[str] = [
    "tiktok", "tik tok", "instagram", "reels", "reel",
    "youtube", "youtube shorts", "shorts",
    "twitter", "x (twitter)", "facebook", "pinterest",
    "snapchat", "reddit", "r/", "subreddit",
    "social media", "went viral", "viral video",
    "trending", "on trend", "trend",
    "hashtag", "#", "influencer", "creator",
]

TIKTOK_MADE_ME_BUY_PHRASES: list[str] = [
    "tiktok made me buy", "tiktok made me get",
    "saw it on tiktok", "found it on tiktok",
    "saw on tiktok", "tiktok recommendation",
    "tiktok brought me here", "came from tiktok",
    "saw this on instagram", "instagram made me buy",
    "saw on reels", "reels recommendation",
]

SHOW_OTHERS_PHRASES: list[str] = [
    "showed my friends", "showed everyone", "show my",
    "showed my mom", "showed my husband", "showed my wife",
    "showed my partner", "showed my sister", "showed my brother",
    "people always ask", "people keep asking", "everyone asks me",
    "everyone wants one", "everyone needs this",
    "brought it to", "took it to", "used it in front of",
    "demonstrated to", "showed off my",
    "look at this", "you have to see", "watch me use",
    "before and after", "before/after", "transformation",
    "the results speak", "visible difference", "visible results",
]

# ── Novelty (12%) ───────────────────────────────────────────────────────────
NOVELTY_PHRASES: list[str] = [
    "never seen anything like", "nothing like it",
    "nothing compares", "nothing else like this",
    "first time", "first time ever", "never before",
    "unique", "one of a kind", "one-of-a-kind",
    "revolutionary", "revolutionary product",
    "innovative", "innovation",
    "i didn't expect", "didn't expect this",
    "surprised me", "blew me away",
    "completely different", "totally different",
    "unlike anything", "unlike any other",
    "first of its kind", "brand new concept",
    "ahead of its time", "future is here",
]

# ── Creator Friendliness (12%) ──────────────────────────────────────────────
CREATOR_PHRASES: list[str] = [
    "content creator", "content creation", "i create content",
    "for my channel", "on my channel", "my youtube channel",
    "my followers", "my audience", "my subscribers",
    "i review products", "product reviewer",
    "unboxing", "unbox", "first impressions",
    "filmed", "film", "recorded a video", "made a video",
    "i posted about", "posted a video", "making a video",
    "screenshot", "took pictures", "photogenic",
    "looks great on camera", "great for photos",
    "aesthetic", "aesthetically pleasing",
    "video potential", "great for content",
]

# ── Recommendation Intent / Word-of-Mouth (5%) ──────────────────────────────
WOM_PHRASES: list[str] = [
    "told everyone", "told my friends", "told my family",
    "told my mom", "told my sister", "told my coworkers",
    "recommended to everyone", "recommended it to",
    "sent this link to", "sent the link to my",
    "buying one for my", "bought one for my",
    "getting one for my", "ordering one for",
    "my mom needs this", "my friend needs this",
    "everyone needs this", "everyone should have",
    "buy this now", "go buy this",
    "would recommend", "highly recommend", "100% recommend",
    "5 stars recommend", "would buy again",
    "perfect gift", "gift idea", "gifting this",
    "christmas gift", "birthday gift", "great gift",
    "buying as gifts", "bought as a gift for",
]

# ── Price-to-Wow (2%) ────────────────────────────────────────────────────────
PRICE_WOW_PHRASES: list[str] = [
    "worth every penny", "worth the money", "worth it",
    "money well spent", "best money i've spent",
    "expensive but worth", "pricey but worth",
    "can't believe the price", "can't believe how cheap",
    "steal at this price", "great deal", "amazing deal",
    "surprisingly affordable", "budget friendly",
    "premium quality for the price", "luxurious for the price",
    "would pay more", "would pay double",
    "cheaper than i expected", "less than i thought",
    "great value", "excellent value", "best value",
    "bang for the buck", "bang for buck",
]

# ── Functional / Non-Viral Language (for contrast) ─────────────────────────
# Used to identify satisfaction-only language that should NOT inflate VIBE score
FUNCTIONAL_ONLY_PHRASES: list[str] = [
    "does what it says", "does the job", "works as expected",
    "cleans well", "works fine", "gets the job done",
    "easy to use", "simple to operate", "straightforward",
    "functional", "practical", "useful",
    "as advertised", "as described", "as expected",
]

# ── Experiment Intent (sub-signal for Hackability) ──────────────────────────
EXPERIMENT_INTENT_PHRASES: list[str] = [
    "i decided to try", "i was curious if", "i discovered that",
    "i found out that", "i realized i could", "i figured out",
    "turns out you can", "you can actually", "apparently you can",
    "someone told me you can", "saw a hack where",
    "read that you can", "heard you can",
]


# ── Lookup helpers ───────────────────────────────────────────────────────────

ALL_VIRALITY_PHRASES: list[str] = (
    HACKABILITY_PHRASES
    + OBSESSION_PHRASES
    + SOCIAL_PLATFORM_MENTIONS
    + TIKTOK_MADE_ME_BUY_PHRASES
    + SHOW_OTHERS_PHRASES
    + NOVELTY_PHRASES
    + CREATOR_PHRASES
    + WOM_PHRASES
    + PRICE_WOW_PHRASES
    + EXPERIMENT_INTENT_PHRASES
)


def contains_any(text: str, phrases: list[str]) -> bool:
    """Case-insensitive check — returns True if any phrase appears in text."""
    lowered = text.lower()
    return any(phrase in lowered for phrase in phrases)


def count_matches(text: str, phrases: list[str]) -> int:
    """Count distinct phrase matches in text."""
    lowered = text.lower()
    return sum(1 for phrase in phrases if phrase in lowered)


def get_matched_phrases(text: str, phrases: list[str]) -> list[str]:
    """Return all matching phrases found in text."""
    lowered = text.lower()
    return [phrase for phrase in phrases if phrase in lowered]
