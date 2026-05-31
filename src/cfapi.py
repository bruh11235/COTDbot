import requests
import random

CF_SET_API = "https://codeforces.com/api/problemset.problems"
CF_SUBMISSION_API = "https://codeforces.com/api/user.status?handle={username}"


def get_random_problem(min_rating: int = 800,
                       max_rating: int = 3500) -> dict | None:
    response = requests.get(CF_SET_API, timeout=10)
    data = response.json()

    if data["status"] != "OK":
        raise RuntimeError("Codeforces API error")

    problems = data["result"]["problems"]
    problems = [p for p in problems if "rating" in p and
                min_rating <= p["rating"] <= max_rating]

    if not problems:
        return None
    return random.choice(problems)


def problem_url(problem: dict) -> str:
    contest_id = problem["contestId"]
    index = problem["index"]
    return f"https://codeforces.com/problemset/problem/{contest_id}/{index}"


def get_user_submission(username: str) -> dict | None:
    response = requests.get(CF_SUBMISSION_API.format(username=username),
                            timeout=10)
    data = response.json()

    if data["status"] != "OK":
        raise RuntimeError("Codeforces API error")

    return data

