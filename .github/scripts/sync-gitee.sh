#!/usr/bin/env bash
set -euo pipefail

: "${GITEE_TOKEN:?Configure the GITEE_SDK_TOKEN repository secret}"
: "${GITEE_USERNAME:?Configure the GITEE_SDK_USERNAME repository variable}"

repo=ChengDu-KunHong/KH-UCANFD_Linux_SDK
api="https://gitee.com/api/v5/repos/$repo"
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT

cat > "$work/askpass" <<'EOF'
#!/usr/bin/env bash
case "$1" in
    *Username*) printf '%s\n' "$GITEE_USERNAME" ;;
    *Password*) printf '%s\n' "$GITEE_TOKEN" ;;
    *) exit 1 ;;
esac
EOF
chmod 700 "$work/askpass"
GIT_ASKPASS="$work/askpass" GIT_TERMINAL_PROMPT=0 git -c credential.helper= push --atomic --tags \
    "https://gitee.com/$repo.git" HEAD:refs/heads/master

gitee() {
    curl --silent --show-error --max-time 120 --header "Authorization: Bearer $GITEE_TOKEN" "$@"
}

# Sync missing assets as well as missing releases so a stalled upload can be retried.
gh api --paginate "repos/$GITHUB_REPOSITORY/releases?per_page=100" \
    --jq '.[] | select(.draft == false and .prerelease == false) | @base64' > "$work/releases"
tac "$work/releases" | while IFS= read -r encoded; do
    release=$(base64 --decode <<< "$encoded")
    tag=$(jq -r '.tag_name' <<< "$release")
    [[ "$tag" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || continue
    status=$(gitee -o "$work/gitee.json" -w '%{http_code}' "$api/releases/tags/$tag")
    # Gitee can return HTTP 200 with JSON null for an unpublished release.
    if [[ "$status" == 200 ]] && jq -e '. == null' "$work/gitee.json" > /dev/null; then
        status=404
    fi
    case "$status" in
        200) ;;
        404)
            jq '{tag_name, name, body, target_commitish: "master", prerelease: false}' <<< "$release" > "$work/new.json"
            gitee --fail --header 'Content-Type: application/json' --data-binary "@$work/new.json" \
                "$api/releases" > "$work/gitee.json"
            ;;
        *) echo "Gitee release lookup returned HTTP $status for $tag" >&2; exit 1 ;;
    esac
    id=$(jq -er '.id' "$work/gitee.json")
    jq -r '.assets[].name' <<< "$release" | while IFS= read -r name; do
        case "$name" in KH-UCANFD_Linux_SDK.zip|KH-UCANFD_Linux_SDK.zip.sha256) ;; *) continue ;; esac
        if jq -e --arg name "$name" '.assets[]? | select(.name == $name)' "$work/gitee.json" > /dev/null; then
            continue
        fi
        gh release download "$tag" --repo "$GITHUB_REPOSITORY" --pattern "$name" --dir "$work" --clobber
        gitee --fail --form "file=@$work/$name" "$api/releases/$id/attach_files" > /dev/null
    done
    printf 'Synced release %s\n' "$tag"
done
