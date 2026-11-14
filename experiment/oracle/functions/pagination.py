MAX_PER_PAGE = 50


def page_bounds(total: int, page: int, per_page: int) -> tuple[int, int]:
    if page < 1 or per_page < 1:
        raise ValueError("page and per_page start at 1")
    per_page = min(per_page, MAX_PER_PAGE)
    start = (page - 1) * per_page
    if start >= total:
        return (total, total)
    end = min(start + per_page, total)
    return (start, end)
