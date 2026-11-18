"""Publish Release installation CI badges to both public README files."""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


START = "<!-- sdk-install-results:start -->"
END = "<!-- sdk-install-results:end -->"
RUN_MARKER = re.compile(r"<!-- sdk-install-run: (\d+)\.(\d+) -->")
INSTALL_JOB = re.compile(r"Download and install on (ubuntu-[a-z0-9.-]+)")
READMES = {"en": "README.md", "zh": "README_zh.md"}
RESULTS = {
    "success": ("passing", "通过", "2da44e"),
    "failure": ("failing", "失败", "cf222e"),
    "startup_failure": ("failing", "启动失败", "cf222e"),
    "timed_out": ("timed out", "超时", "cf222e"),
    "cancelled": ("cancelled", "已取消", "6e7781"),
    "skipped": ("skipped", "已跳过", "6e7781"),
}


def api(path):
    request = Request(
        f"{os.environ['GITHUB_API_URL']}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
        },
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def install_jobs(repo_path, run_id):
    # Keep earlier results for jobs omitted from a partial re-run.
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


def badge(label, message, color, logo):
    escaped_alt = re.sub(r"([\\\[\]])", r"\\\1", f"{label} | {message}")
    badge_text = quote(message.replace("-", "--"), safe="")
    options = urlencode({"label": label, "logo": logo, "labelColor": "30363d"})
    return f"![{escaped_alt}](https://img.shields.io/badge/{badge_text}-{color}?{options})"


def render_badges(jobs, platforms, run_url, language):
    versions = set()
    badges = []
    for image, job in sorted(jobs.items()):
        platform = platforms.get((image, job["run_attempt"]), {})
        distro = platform.get("distro", image)
        kernel = platform.get("kernel")
        label = f"{distro} · {kernel}" if kernel else distro
        if platform.get("tag"):
            versions.add(platform["tag"])
        english, chinese, color = RESULTS.get(job["conclusion"], ("unknown", "未知", "6e7781"))
        message = chinese if language == "zh" else english
        image_markdown = badge(label, message, color, logo="github")
        badges.append(f"[{image_markdown}]({run_url}/job/{int(job['id'])})")
    if versions:
        version_line = "SDK " + ", ".join(f"`{tag}`" for tag in sorted(versions))
        badges = [version_line, "", *badges]
    return "\n".join(badges)


def replace_results(readme, results, run):
    if readme.count(START) != 1 or readme.count(END) != 1:
        raise ValueError("README must have exactly one SDK install result section")
    before, _, section = readme.partition(START)
    old, close, after = section.partition(END)
    if not close:
        raise ValueError("SDK install result section markers are in the wrong order")
    if (previous := RUN_MARKER.search(old)) and tuple(map(int, previous.groups())) >= run:
        return readme
    marker = f"<!-- sdk-install-run: {run[0]}.{run[1]} -->"
    return f"{before}{START}\n{marker}\n\n{results}\n\n{END}{after}"


def git(*args, **kwargs):
    return subprocess.run(["git", *args], text=True, check=True, **kwargs)


def update_readmes(branch, results, run):
    ref = f"refs/heads/{branch}"
    for retry in range(3):
        git("fetch", "--no-tags", "origin", ref)
        git("checkout", "--detach", "FETCH_HEAD")
        changed = []
        for language, filename in READMES.items():
            path = Path(filename)
            readme = path.read_text(encoding="utf-8")
            updated = replace_results(readme, results[language], run)
            if updated != readme:
                path.write_text(updated, encoding="utf-8")
                changed.append(filename)
        if not changed:
            print("READMEs already reflect this run or a newer one")
            return
        git("add", "--", *changed)
        git("-c", "user.name=github-actions[bot]",
            "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
            "commit", "-m", "Update SDK release install badges")
        try:
            # One fast-forward updates both languages together.
            git("push", "origin", f"HEAD:{ref}", capture_output=True)
        except subprocess.CalledProcessError as error:
            if retry == 2 or not re.search(r"non-fast-forward|fetch first", error.stderr):
                print(error.stderr, file=sys.stderr)
                raise
        else:
            print("Updated the English and Chinese README badges")
            return


def publish(artifacts):
    repo = os.environ["GITHUB_REPOSITORY"]
    run_id = int(os.environ["GITHUB_RUN_ID"])
    run = (int(os.environ["GITHUB_RUN_NUMBER"]), int(os.environ["GITHUB_RUN_ATTEMPT"]))
    run_url = f"{os.environ['GITHUB_SERVER_URL']}/{repo}/actions/runs/{run_id}"

    platforms = {}
    for path in artifacts.rglob("platform.json"):
        platform = json.loads(path.read_text(encoding="utf-8"))
        platforms[(platform["image"], platform["attempt"])] = platform

    jobs = install_jobs(f"repos/{repo}", run_id)
    if not jobs:
        raise ValueError("No SDK installation jobs found for this run")
    results = {
        language: render_badges(jobs, platforms, run_url, language)
        for language in READMES
    }
    update_readmes(os.environ["GITHUB_REF_NAME"], results, run)


if __name__ == "__main__":
    publish(Path(sys.argv[1]))
