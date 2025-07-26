from thefuzz import fuzz


def check_keywords_with_keywords(keywords, paper_keywords, threshold):
    if not paper_keywords:
        return None, False

    # Ensure paper_keywords is a list
    if not isinstance(paper_keywords, list):
        if isinstance(paper_keywords, str):
            paper_keywords = [paper_keywords]
        else:
            try:
                paper_keywords = list(paper_keywords)
            except:
                paper_keywords = [str(paper_keywords)]

    for keyword in keywords:
        if keyword is None:
            continue

        # Ensure keyword is a string
        keyword = str(keyword)

        if not keyword.strip():
            continue

        for paper_keyword in paper_keywords:
            if paper_keyword is None:
                continue

            # Ensure paper_keyword is a string
            paper_keyword = str(paper_keyword)

            if not paper_keyword.strip():
                continue

            try:
                if fuzz.ratio(keyword, paper_keyword) >= threshold:
                    return keyword, True
            except Exception as e:
                print(f"Error comparing '{keyword}' with '{paper_keyword}': {e}")
                continue

    return None, False


def check_keywords_with_text(keywords, text, threshold):
    if text is None:
        return None, False

    # Ensure text is a string
    text = str(text)

    for keyword in keywords:
        if keyword is None:
            continue

        # Ensure keyword is a string
        keyword = str(keyword)

        # Skip empty strings
        if not keyword.strip() or not text.strip():
            continue

        try:
            if fuzz.partial_ratio(keyword, text) >= threshold:
                return keyword, True
        except Exception as e:
            print(f"Error comparing '{keyword}' with text: {e}")
            continue

    return None, False


def satisfies_any_filters(paper, keywords, filters):
    for filter_, args, kwargs in filters:
        matched_keyword, matched = filter_(paper, keywords=keywords, *args, **kwargs)
        if matched:
            filter_type = filter_.__name__
            return matched_keyword, filter_type, True
    return None, None, False


def satisfies_all_filters(paper, keywords, filters):
    matched_keywords = []
    filter_types = []
    for filter_, args, kwargs in filters:
        matched_keyword, matched = filter_(paper, keywords=keywords, *args, **kwargs)
        if not matched:
            return None, None, False
        filter_types.append(filter_.__name__)
        matched_keywords.append(matched_keyword)
    return matched_keywords, filter_types, True


def satisfies_mixed_filters(paper, keywords, filters):
    """
    keywords: list, e.g. ["a", ["b", "c"]]
    Each element is either a string (must match) or a list (any in the list must match).
    The outer list is AND, inner lists are OR.
    """
    matched_keywords = []
    filter_types = []
    for idx, keyword_group in enumerate(keywords):
        if isinstance(keyword_group, list):
            # OR logic for this group
            group_matched = False
            for kw in keyword_group:
                for filter_, args, kwargs in filters:
                    matched_keyword, matched = filter_(
                        paper, keywords=[kw], *args, **kwargs
                    )
                    if matched:
                        matched_keywords.append(matched_keyword)
                        filter_types.append(filter_.__name__)
                        group_matched = True
                        break
                if group_matched:
                    break
            if not group_matched:
                return None, None, False
        else:
            # Single keyword, must match
            group_matched = False
            for filter_, args, kwargs in filters:
                matched_keyword, matched = filter_(
                    paper, keywords=[keyword_group], *args, **kwargs
                )
                if matched:
                    matched_keywords.append(matched_keyword)
                    filter_types.append(filter_.__name__)
                    group_matched = True
                    break
            if not group_matched:
                return None, None, False
    return matched_keywords, filter_types, True


def keywords_filter(paper, keywords, threshold=85):
    paper_keywords = paper.content.get("keywords")
    if paper_keywords is not None:
        return check_keywords_with_keywords(keywords, paper_keywords, threshold)
    return None, False


def title_filter(paper, keywords, threshold=85):
    paper_title = paper.content.get("title")
    if paper_title is not None:
        return check_keywords_with_text(keywords, paper_title, threshold)
    return None, False


def abstract_filter(paper, keywords, threshold=85):
    paper_abstract = paper.content.get("abstract")
    if paper_abstract is not None:
        return check_keywords_with_text(keywords, paper_abstract, threshold)
    return None, False
