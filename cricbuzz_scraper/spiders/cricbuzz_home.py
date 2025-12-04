import scrapy

def parse_match_text(text: str) -> dict:
    original_text = text
    core = text.replace("Points Table", "").replace("Schedule", "").strip()

    match_format = None
    title_part = None
    rest = None

    for token in [" T20 ", " ODI ", " Test "]:
        if token in core:
            title_part, rest = core.rsplit(token, 1)
            match_format = token.strip()
            break

    if not match_format:
        return {"raw_text": original_text}

    match_title = title_part.strip()
    rest = rest.strip()
    words = rest.split()
    if len(words) < 3:
        return {"raw_text": original_text, "match_title": match_title, "format": match_format}

    team1 = words[0]
    i = 1
    if i < len(words) and words[i] == team1:
        i += 1

    second_team_idx = None
    j = i
    while j < len(words):
        w = words[j]
        if w.isalpha() and w.isupper() and len(w) <= 3 and w != team1:
            second_team_idx = j
            break
        j += 1

    if second_team_idx is None:
        return {"raw_text": original_text, "match_title": match_title, "format": match_format, "team1": team1}

    team1_score = " ".join(words[i:second_team_idx]).strip() or None

    team2 = words[second_team_idx]
    k = second_team_idx + 1
    if k < len(words) and words[k] == team2:
        k += 1

    status_start = len(words)
    s = k
    while s < len(words):
        ww = words[s]
        if ww[0].isalpha() and ww[0].isupper() and len(ww) >= 3:
            status_start = s
            break
        s += 1

    team2_score = " ".join(words[k:status_start]).strip() or None
    status = " ".join(words[status_start:]).strip() or None

    return {
        "raw_text": original_text,
        "match_title": match_title,
        "format": match_format,
        "team1": team1,
        "team1_score": team1_score,
        "team2": team2,
        "team2_score": team2_score,
        "status": status,
    }


class CricbuzzHomeSpider(scrapy.Spider):
    name = "cricbuzz_home"
    allowed_domains = ["cricbuzz.com"]
    start_urls = ["https://www.cricbuzz.com"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
        "DOWNLOAD_DELAY": 1,
    }

    def parse(self, response):
        carousel = response.css("div.carousal-list")
        if not carousel:
            return

        cards = carousel.css("div > div")
        seen_texts = set()

        for idx, card in enumerate(cards, start=1):
            raw_text = card.css("::text").getall()
            cleaned = " ".join(t.strip() for t in raw_text if t.strip())

            if not cleaned:
                continue
            if cleaned in seen_texts:
                continue
            seen_texts.add(cleaned)

            has_format = any(fmt in cleaned for fmt in ("T20", "ODI", "Test"))
            if cleaned.count("Schedule") == 1 and has_format:
                parsed = parse_match_text(cleaned)
                parsed["card_index"] = idx
                yield parsed
