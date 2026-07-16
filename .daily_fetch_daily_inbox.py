#!/usr/bin/env python3
"""Collect a machine-readable X candidate pack for the AI/Agent strategic radar.

This script is deliberately not an editor. It fetches, normalizes, de-duplicates,
and pre-ranks source material, then leaves final judgment to the 09:10 agent job.
It never writes a user-facing Daily Inbox and never commits or pushes Git.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

REPO = pathlib.Path("/Users/wangyuqiao/repos/clawd-knowledge")
TODAY = subprocess.check_output(["date", "+%F"], text=True).strip()
TRACKED = REPO / "30_People/_tracked.md"
CACHE = REPO / ".daily_fetch" / TODAY
PACK = CACHE / "candidate_pack.json"
FOLLOWING_DIR = REPO / ".daily_following"
AUTHORITY_PATH = pathlib.Path.home() / ".hermes/scripts/ai_authority_accounts.json"
PER_ACCOUNT = 10
MAX_ITEMS = 50
MAX_PER_HANDLE = 4
MAX_WORKERS = 4
FETCH_TIMEOUT = 25
LOOKBACK_HOURS = 48

BATTLEFIELD_TERMS = {
    "claude code": 6, "codex": 6, "hermes": 6, "openclaw": 5,
    "agent": 4, "agents": 4, "agentic": 4, "skill": 4, "skills": 4,
    "mcp": 4, "workflow": 4, "automation": 4, "subagent": 4,
    "gpt-5.6": 6, "deepseek": 4, "model": 2, "benchmark": 3,
    "eval": 3, "quota": 5, "usage limit": 5, "rate limit": 5,
    "reset": 4, "outage": 5, "security": 4, "vulnerability": 4,
    "context": 2, "prompt": 2, "api": 2, "release": 2, "launch": 2,
    "智能体": 4, "自动化": 4, "工作流": 4, "提示词": 2,
    "模型": 2, "额度": 5, "限流": 5, "重置": 4, "安全": 4,
    "发布": 2, "开源": 2, "上下文": 2, "子代理": 4,
}
NOISE_TERMS = {
    "招聘": -5, "hiring": -5, "join us": -4, "周边": -4,
    "keyboard": -4, "键盘": -4, "giveaway": -5, "抽奖": -5,
}


def strip_json(text: str):
    text = text.strip()
    for left, right in (("[", "]"), ("{", "}")):
        start, end = text.find(left), text.rfind(right)
        if start >= 0 and end > start:
            return text[start : end + 1]
    return text


def run(cmd, timeout=FETCH_TIMEOUT):
    return subprocess.run(
        cmd, cwd=str(REPO), text=True, capture_output=True, timeout=timeout
    )


def parse_dt(value: str):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y").astimezone(timezone.utc)
    except ValueError:
        return None


def get_text(tweet: dict):
    parts = []
    for key in ("text", "full_text"):
        if tweet.get(key):
            parts.append(str(tweet[key]))
    for key in ("quotedTweet", "retweetedTweet"):
        nested = tweet.get(key)
        if not isinstance(nested, dict):
            continue
        author = (nested.get("author") or {}).get("username") or ""
        nested_text = nested.get("text") or nested.get("full_text") or ""
        if nested_text:
            parts.append(f"引用 @{author}: {nested_text}")
    return re.sub(r"\s+", " ", " ".join(dict.fromkeys(parts))).strip()


def load_tracked_handles():
    text = TRACKED.read_text(encoding="utf-8")
    out = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            continue
        match = re.match(r"^\s*-\s+@([A-Za-z0-9_]+)", line)
        if match:
            out.append(match.group(1))
    return list(dict.fromkeys(out))


def load_authority_metadata():
    try:
        data = json.loads(AUTHORITY_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {item["handle"].lower(): item for item in data if item.get("handle")}


def load_known_ids():
    ids = set()
    inbox = REPO / "00_Inbox"
    if not inbox.exists():
        return ids
    for path in inbox.glob("*.md"):
        if path.name == f"{TODAY}.md":
            continue
        try:
            ids.update(re.findall(r"/status/(\d+)", path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return ids


def normalize_following(raw):
    if isinstance(raw, dict):
        raw = raw.get("users") or raw.get("data") or []
    result = []
    for item in raw or []:
        if not isinstance(item, dict) or not item.get("username"):
            continue
        result.append({
            "username": item["username"],
            "name": item.get("name") or "",
            "description": item.get("description") or "",
        })
    return result


def capture_following():
    FOLLOWING_DIR.mkdir(parents=True, exist_ok=True)
    snapshot = FOLLOWING_DIR / f"{TODAY}.json"
    proc = run(["bird", "following", "--json"], timeout=90)
    if proc.returncode != 0:
        return [], {"error": (proc.stderr or proc.stdout).strip()[-500:]}
    try:
        following = normalize_following(json.loads(strip_json(proc.stdout)))
    except Exception as exc:
        return [], {"error": f"following JSON parse failed: {exc}"}

    prior_paths = sorted(p for p in FOLLOWING_DIR.glob("*.json") if p.name < snapshot.name)
    prior = []
    if prior_paths:
        try:
            prior = json.loads(prior_paths[-1].read_text(encoding="utf-8"))
        except Exception:
            prior = []
    snapshot.write_text(json.dumps(following, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    current_map = {x["username"].lower(): x for x in following}
    prior_map = {x["username"].lower(): x for x in prior if x.get("username")}
    if not prior_paths:
        delta = {"baseline_created": True, "new": [], "removed": []}
    else:
        delta = {
            "baseline_created": False,
            "new": [current_map[k] for k in current_map.keys() - prior_map.keys()],
            "removed": [prior_map[k] for k in prior_map.keys() - current_map.keys()],
        }
    return following, delta


def score_item(text, likes, retweets, replies, tier):
    lower = text.lower()
    reasons = []
    score = 0.0
    for term, weight in BATTLEFIELD_TERMS.items():
        if term in lower:
            score += weight
            reasons.append(term)
    for term, penalty in NOISE_TERMS.items():
        if term in lower:
            score += penalty
            reasons.append(f"noise:{term}")
    score += math.log1p(max(0, likes))
    score += 0.8 * math.log1p(max(0, retweets))
    score += 0.25 * math.log1p(max(0, replies))
    if tier == "A1-main-battlefield":
        score += 3
    elif tier == "B-provisional-source":
        score -= 1
    return round(score, 2), reasons[:10]


def fetch_handle(handle, cutoff, known_ids, metadata):
    proc = run(["bird", "user-tweets", "@" + handle, "-n", str(PER_ACCOUNT), "--json"], timeout=FETCH_TIMEOUT)
    if proc.returncode != 0:
        error = (proc.stderr or proc.stdout).strip().splitlines()
        return [], error[-1] if error else f"exit {proc.returncode}"
    try:
        data = json.loads(strip_json(proc.stdout))
    except Exception as exc:
        return [], f"JSON parse failed: {exc}"
    if isinstance(data, dict):
        data = data.get("tweets") or data.get("data") or [data]

    account_meta = metadata.get(handle.lower(), {})
    tier = account_meta.get("tier", "B-provisional-source")
    group = account_meta.get("group", "personal-following")
    items = []
    for tweet in data or []:
        if not isinstance(tweet, dict):
            continue
        tweet_id = str(tweet.get("id") or tweet.get("rest_id") or "")
        if not tweet_id or tweet_id in known_ids:
            continue
        created = parse_dt(tweet.get("createdAt") or "")
        if created and created < cutoff:
            continue
        text = get_text(tweet)
        if not text or re.match(r"^RT\s", text, flags=re.I):
            continue
        if tweet.get("inReplyToStatusId") and len(text) < 180:
            continue
        likes = int(tweet.get("likeCount") or tweet.get("favorite_count") or 0)
        retweets = int(tweet.get("retweetCount") or 0)
        replies = int(tweet.get("replyCount") or 0)
        score, reasons = score_item(text, likes, retweets, replies, tier)
        if score < 4 or not any(not r.startswith("noise:") for r in reasons):
            continue
        items.append({
            "id": tweet_id,
            "handle": handle,
            "url": f"https://x.com/{handle}/status/{tweet_id}",
            "created_at": tweet.get("createdAt") or "",
            "text": text[:900],
            "likes": likes,
            "retweets": retweets,
            "replies": replies,
            "prefilter_score": score,
            "prefilter_reasons": reasons,
            "tier": tier,
            "group": group,
        })
    return items, None


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    handles = load_tracked_handles()
    metadata = load_authority_metadata()
    known_ids = load_known_ids()
    following, following_delta = capture_following()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=LOOKBACK_HOURS)

    items = []
    failures = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(fetch_handle, handle, cutoff, known_ids, metadata): handle
            for handle in handles
        }
        for future in as_completed(futures):
            handle = futures[future]
            try:
                fetched, error = future.result()
            except Exception as exc:
                fetched, error = [], f"{type(exc).__name__}: {exc}"
            items.extend(fetched)
            if error:
                failures.append({"handle": handle, "error": error})

    deduped = {}
    for item in items:
        previous = deduped.get(item["id"])
        if previous is None or item["prefilter_score"] > previous["prefilter_score"]:
            deduped[item["id"]] = item
    ranked = sorted(
        deduped.values(),
        key=lambda x: (x["prefilter_score"], x["likes"] + 3 * x["retweets"]),
        reverse=True,
    )
    selected = []
    per_handle = {}
    for item in ranked:
        key = item["handle"].lower()
        if per_handle.get(key, 0) >= MAX_PER_HANDLE:
            continue
        selected.append(item)
        per_handle[key] = per_handle.get(key, 0) + 1
        if len(selected) >= MAX_ITEMS:
            break

    pack = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date": TODAY,
        "purpose": "candidate_material_only_not_user_facing",
        "tracked_handles": handles,
        "following_count": len(following),
        "following_delta": following_delta,
        "failures": sorted(failures, key=lambda x: x["handle"].lower()),
        "raw_candidate_count": len(deduped),
        "candidates": selected,
    }
    PACK.write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    new_following = [
        "@" + str(item.get("username", ""))
        for item in (following_delta.get("new") or [])
        if isinstance(item, dict) and item.get("username")
    ]
    removed_following = [
        "@" + str(item.get("username", ""))
        for item in (following_delta.get("removed") or [])
        if isinstance(item, dict) and item.get("username")
    ]
    print(json.dumps({
        "date": TODAY,
        "pack": str(PACK),
        "tracked_count": len(handles),
        "following_count": len(following),
        "following_new": new_following,
        "following_removed": removed_following,
        "candidate_count": len(selected),
        "failures": failures,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
