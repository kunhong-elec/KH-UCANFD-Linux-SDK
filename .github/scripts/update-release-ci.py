"""Publish the latest Release install matrix results in the public README."""

import base64
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


START = "<!-- sdk-install-results:start -->"
END = "<!-- sdk-install-results:end -->"
RUN_MARKER = re.compile(r"<!-- sdk-install-run: (\d+)\.(\d+) -->")
INSTALL_JOB = re.compile(r"Download and install on (ubuntu-[a-z0-9.-]+)")
RESULTS = {
    "success": "✅ 通过",
    "failure": "❌ 失败",
    "timed_out": "❌ 超时",
    "cancelled": "已取消",
    "skipped": "已跳过",
}


def api(path, body=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
    }
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        f"{os.environ['GITHUB_API_URL']}/{path}",
        data=data,
        headers=headers,
        method="PUT" if data is not None else "GET",
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def install_jobs(repo_path, run_id):
    # A partial re-run retains earlier results for jobs that did not run again.
    jobs = {}
    page = 1
    while True:
        batch = api(
            f"{repo_path}/actions/runs/{run_id}/jobs?filter=all&per_page=100&page={page}"
        )["jobs"]
        for job in batch:
            if match := INSTALL_JOB.fullmatch(job["name"]):
                image = match[1]
                if image not in jobs or job["run_attempt"] > jobs[image]["run_attempt"]:
                    jobs[image] = job
        if len(batch) < 100:
            return jobs
        page += 1


def cell(value):
    return html.escape(value).replace("|", "&#124;").replace("\r", " ").replace("\n", " ")


def render_table(jobs, platforms, run_url):
    lines = [
        "| 发行版 | 实测内核 | SDK 版本 | 下载安装结果 |",
        "| --- | --- | --- | --- |",
    ]
    for image, job in sorted(jobs.items()):
        platform = platforms.get((image, job["run_attempt"]), {})
        distro = cell(platform.get("distro", image))
        kernel = cell(platform.get("kernel", "—"))
        tag = cell(platform.get("tag", "—"))
        status = RESULTS.get(job["conclusion"], "未完成")
        log_url = f"{run_url}/job/{int(job['id'])}"
        lines.append(f"| {distro} | <code>{kernel}</code> | <code>{tag}</code> | [{status}]({log_url}) |")
    return "\n".join(lines)


def replace_results(readme, table, run):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must have exactly one SDK install result section")
    before, _, section = readme.partition(START)
    old, close, after = section.partition(END)
    if not close:
        raise ValueError("SDK install result section markers are in the wrong order")
    if (previous := RUN_MARKER.search(old)) and tuple(map(int, previous.groups())) >= run:
        return readme
    marker = f"<!-- sdk-install-run: {run[0]}.{run[1]} -->"
    return f"{before}{START}\n{marker}\n\n{table}\n\n{END}{after}"


def publish(artifacts):
    repo = os.environ["GITHUB_REPOSITORY"]
    repo_path = f"repos/{repo}"
    run_id = int(os.environ["GITHUB_RUN_ID"])
    run = (int(os.environ["GITHUB_RUN_NUMBER"]), int(os.environ["GITHUB_RUN_ATTEMPT"]))
    run_url = f"{os.environ['GITHUB_SERVER_URL']}/{repo}/actions/runs/{run_id}"
    branch = os.environ["GITHUB_REF_NAME"]

    platforms = {}
    for path in artifacts.rglob("platform.json"):
        platform = json.loads(path.read_text(encoding="utf-8"))
        platforms[(platform["image"], platform["attempt"])] = platform

    jobs = install_jobs(repo_path, run_id)
    if not jobs:
        raise ValueError("No SDK installation jobs found for this run")
    table = render_table(jobs, platforms, run_url)

    readme_path = f"{repo_path}/contents/README.md"
    for retry in range(3):
        current = api(f"{readme_path}?{urlencode({'ref': branch})}")
        readme = base64.b64decode(current["content"]).decode()
        updated = replace_results(readme, table, run)
        if updated == readme:
            print("README already reflects this run or a newer one")
            return
        try:
            result = api(readme_path, {
                "message": "Update SDK release install results",
                "branch": branch,
                "sha": current["sha"],
                "content": base64.b64encode(updated.encode()).decode(),
            })
            print(f"README updated in {result['commit']['sha']}")
            return
        except HTTPError as error:
            if error.code != 409 or retry == 2:
                raise


if __name__ == "__main__":
    publish(Path(sys.argv[1]))
