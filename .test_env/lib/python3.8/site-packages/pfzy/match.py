"""Module contains the async interface to match needle against haystack in batch."""
import asyncio
import heapq
from typing import Any, Callable, Dict, List, Union, cast

from pfzy.score import SCORE_INDICES, fzy_scorer
from pfzy.types import HAYSTACKS


async def _rank_task(
    scorer: Callable[[str, str], SCORE_INDICES],
    needle: str,
    haystacks: List[Union[str, Dict[str, Any]]],
    key: str,
) -> List[Dict[str, Any]]:
    """Calculate the score for needle against given list of haystacks and rank them.

    Args:
        scorer: Scorer to be used to do the calculation.
        needle: Substring to search.
        haystacks: List of dictionary containing the haystack to be searched.
        key: The key within the `haystacks` dictionary that contains the actual string value.

    Return:
        Sorted list of haystacks based on the needle score with additional keys for the `score`
        and `indices`.
    """
    result = []
    for haystack in haystacks:
        score, indices = scorer(needle, cast(Dict, haystack)[key])
        if indices is None:
            continue
        result.append(
            {
                "score": score,
                "indices": indices,
                "haystack": haystack,
            }
        )
    result.sort(key=lambda x: x["score"], reverse=True)
    return result


async def fuzzy_match(
    needle: str,
    haystacks: HAYSTACKS,
    key: str = "",
    batch_size: int = 4096,
    scorer: Callable[[str, str], SCORE_INDICES] = None,
) -> List[Dict[str, Any]]:
    """Fuzzy find the needle within list of haystacks and get matched results with matching index.

    Note:
        The `key` argument is optional when the provided `haystacks` argument is a list of :class:`str`.
        It will be given a default key `value` if not present.

    Warning:
        The `key` argument is required when provided `haystacks` argument is a list of :class:`dict`.
        If not present, :class:`TypeError` will be raised.

    Args:
        needle: String to search within the `haystacks`.
        haystacks: List of haystack/longer strings to be searched.
        key: If `haystacks` is a list of dictionary, provide the key that
            can obtain the haystack value to search.
        batch_size: Number of entry to be processed together.
        scorer (Callable[[str, str], SCORE_indices]): Desired scorer to use. Currently only :func:`~pfzy.score.fzy_scorer` and :func:`~pfzy.score.substr_scorer` is supported.

    Raises:
        TypeError: When the argument `haystacks` is :class:`list` of :class:`dict` and the `key` argument
            is missing, :class:`TypeError` will be raised.

    Returns:
        List of matching `haystacks` with additional key indices and score.

    Examples:
        >>> import asyncio
        >>> asyncio.run(fuzzy_match("ab", ["acb", "acbabc"]))
        [{'value': 'acbabc', 'indices': [3, 4]}, {'value': 'acb', 'indices': [0, 2]}]
    """
    if scorer is None:
        scorer = fzy_scorer

    for index, haystack in enumerate(haystacks):
        if not isinstance(haystack, dict):
            if not key:
                key = "value"
            haystacks[index] = {key: haystack}

    if not key:
        raise TypeError(
            f"${fuzzy_match.__name__} missing 1 required argument: 'key', 'key' is required when haystacks is an instance of dict"
        )

    batches = await asyncio.gather(
        *(
            _rank_task(
                scorer,
                needle,
                haystacks[offset : offset + batch_size],
                key,
            )
            for offset in range(0, len(haystacks), batch_size)
        )
    )
    results = heapq.merge(*batches, key=lambda x: x["score"], reverse=True)
    choices = []
    for candidate in results:
        candidate["haystack"]["indices"] = candidate["indices"]
        choices.append(candidate["haystack"])
    return choices
