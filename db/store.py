_runs: list[dict] = []
_next_id: int = 1


def init_db():
    pass  # no-op — runs live in memory for the session


def save_run(record: dict) -> int:
    global _next_id
    entry = {**record, "id": _next_id, "feedback": None, "feedback_comment": None}
    _runs.append(entry)
    _next_id += 1
    return entry["id"]


def update_feedback(run_id: int, value: int):
    for run in _runs:
        if run["id"] == run_id:
            run["feedback"] = value
            return


def update_feedback_comment(run_id: int, comment: str):
    for run in _runs:
        if run["id"] == run_id:
            run["feedback_comment"] = comment
            return


def delete_run(run_id: int):
    global _runs
    _runs = [r for r in _runs if r["id"] != run_id]


def get_run(run_id: int) -> dict | None:
    for run in _runs:
        if run["id"] == run_id:
            return dict(run)
    return None


def get_runs(limit: int = 100) -> list[dict]:
    return [dict(r) for r in reversed(_runs)][:limit]
