"""Keywords: YAKE per page plus corpus TF-IDF, deterministic and offline.

The untyped libraries are wrapped here so nothing else imports them.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

_FENCE_BLOCK = re.compile(r"^(`{3,}|~{3,}).*?^\1[ \t]*$", re.MULTILINE | re.DOTALL)
_INLINE_CODE = re.compile(r"`[^`\n]*`")
_HTML_TAG = re.compile(r"<[^>]+>")
_LINK_TARGET = re.compile(r"\]\([^)]*\)")
_URL = re.compile(r"https?://[^\s\"'<>)]+")
_MD_SYNTAX = re.compile(r"[#*_>|\[\]()!{}]|\{#[^}]*\}")
_TOKEN = re.compile(r"[a-z][a-z0-9.+-]*(?:\s[a-z][a-z0-9.+-]*){0,2}")
MIN_TOKEN = 3
MAX_DOC_FREQ = 0.40
YAKE_TOP = 12
TFIDF_TOP = 5
STOP_WORDS = frozenset(
    (
        "a",
        "about",
        "above",
        "after",
        "again",
        "against",
        "all",
        "also",
        "am",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "because",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "could",
        "did",
        "do",
        "does",
        "doing",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "had",
        "has",
        "have",
        "having",
        "he",
        "her",
        "here",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "itself",
        "just",
        "let",
        "me",
        "more",
        "most",
        "my",
        "myself",
        "no",
        "nor",
        "not",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "our",
        "ours",
        "ourselves",
        "out",
        "over",
        "own",
        "same",
        "she",
        "should",
        "so",
        "some",
        "such",
        "than",
        "that",
        "the",
        "their",
        "theirs",
        "them",
        "themselves",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "use",
        "used",
        "using",
        "very",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "will",
        "with",
        "would",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "see",
        "following",
        "example",
        "examples",
        "returns",
        "return",
        "value",
        "values",
        "request",
        "response",
        "method",
        "type",
        "types",
        "object",
        "objects",
        "property",
        "properties",
        "parameter",
        "parameters",
        "page",
        "pages",
        "note",
        "api",
    )
)


def plain_text(markdown: str) -> str:
    """The Markdown body with code and syntax removed, for keyword extraction."""
    text = _FENCE_BLOCK.sub(" ", markdown)
    text = _INLINE_CODE.sub(" ", text)
    text = _HTML_TAG.sub(" ", text)
    text = _LINK_TARGET.sub("]", text)
    text = _URL.sub(" ", text)
    text = _MD_SYNTAX.sub(" ", text)
    return " ".join(text.split())


def _yake(text: str, top: int = YAKE_TOP) -> list[tuple[str, float]]:
    try:
        import yake  # noqa: PLC0415
    except ImportError:  # pragma: no cover - yake is a dependency
        return []
    extractor: Any = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=top, features=None)
    try:
        pairs: list[tuple[str, float]] = extractor.extract_keywords(text)
    except Exception:  # noqa: BLE001 - yake fails on degenerate input; no keywords then
        return []
    return [(str(k).lower(), float(score)) for k, score in pairs]


def tfidf_terms(corpus: Sequence[str], top: int = TFIDF_TOP) -> list[list[tuple[str, float]]]:
    """Per document, its top distinctive terms by TF-IDF over the corpus."""
    if not corpus:
        return []
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: PLC0415
    except ImportError:  # pragma: no cover - scikit-learn is a dependency
        return [[] for _ in corpus]
    vectorizer: Any = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=1,
        max_df=MAX_DOC_FREQ if len(corpus) > 2 else 1.0,  # noqa: PLR2004 - max_df needs a corpus
        token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9.+-]{1,}\b",  # noqa: S106 - a regex, not a secret
        sublinear_tf=True,
    )
    try:
        matrix = vectorizer.fit_transform(list(corpus))
    except ValueError:
        return [[] for _ in corpus]
    names = vectorizer.get_feature_names_out()
    result: list[list[tuple[str, float]]] = []
    for row in matrix:
        dense = row.toarray().ravel()
        order = dense.argsort()[::-1]
        picked: list[tuple[str, float]] = []
        for index in order:
            if dense[index] <= 0 or len(picked) >= top:
                break
            picked.append((str(names[index]).lower(), float(dense[index])))
        result.append(picked)
    return result


def _acceptable(term: str, common: set[str]) -> bool:
    words = term.split()
    if any(len(w) < MIN_TOKEN for w in words):
        return False
    if all(w in STOP_WORDS for w in words):
        return False
    return term not in common


def merge_keywords(
    yake_terms: list[tuple[str, float]],
    tfidf: list[tuple[str, float]],
    common: set[str],
    *,
    limit: int = 8,
    minimum: int = 5,
) -> list[str]:
    """Combine YAKE (lower is better) and TF-IDF (higher is better) into 5-8 keywords."""
    scored: dict[str, float] = {}
    for rank, (term, _) in enumerate(yake_terms):
        if _acceptable(term, common):
            scored[term] = max(scored.get(term, 0.0), 1.0 - rank / max(len(yake_terms), 1))
    for rank, (term, _) in enumerate(tfidf):
        if _acceptable(term, common):
            scored[term] = max(scored.get(term, 0.0), 0.95 - rank / max(len(tfidf), 1))
    ordered = sorted(scored.items(), key=lambda item: (-item[1], item[0]))
    picked: list[str] = []
    for term, _ in ordered:
        if term in picked or any(term in p or p in term for p in picked):
            continue
        picked.append(term)
        if len(picked) >= limit:
            break
    if len(picked) < minimum:
        for term, _ in ordered:
            if term not in picked:
                picked.append(term)
            if len(picked) >= minimum:
                break
    return picked


def compute_keywords(bodies: dict[str, str], *, limit: int = 8) -> dict[str, list[str]]:
    """Keywords per key over the corpus of Markdown bodies."""
    keys = list(bodies)
    texts = [plain_text(bodies[key]) for key in keys]
    doc_terms: list[set[str]] = []
    yake_all: list[list[tuple[str, float]]] = []
    for text in texts:
        terms = _yake(text)
        yake_all.append(terms)
        doc_terms.append({t for t, _ in terms})
    tfidf_all = tfidf_terms(texts)
    frequency: dict[str, int] = {}
    for term_set in doc_terms:
        for term in term_set:
            frequency[term] = frequency.get(term, 0) + 1
    common = {t for t, n in frequency.items() if len(keys) > 2 and n / len(keys) > MAX_DOC_FREQ}  # noqa: PLR2004 - needs a corpus
    return {
        key: merge_keywords(
            yake_all[i], tfidf_all[i] if i < len(tfidf_all) else [], common, limit=limit
        )
        for i, key in enumerate(keys)
    }
