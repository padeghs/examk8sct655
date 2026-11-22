#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

cluster=k8sfinal
image=localhost/id039-web:4.0
node="$cluster-control-plane"
k=(kubectl --context "kind-$cluster")

case "${1:-}" in
  cluster)
    if ! kind get clusters | grep -Fxq "$cluster"; then
      kind create cluster --name "$cluster" --config kind/cluster.yaml --wait 120s
    fi
    "${k[@]}" get nodes -o wide
    ;;
  build)
    docker build -t "$image" apps
    kind load docker-image "$image" --name "$cluster"
    ;;
  secret)
    "${k[@]}" apply -f k8s/00-namespace.yaml
    umask 077
    secret_file=$(mktemp)
    trap 'rm -f "$secret_file"' EXIT
    read -rp 'Admin username: ' editor_username
    read -rsp 'Admin password: ' editor_password
    printf '\n'
    if [[ -z $editor_username || -z $editor_password ]]; then
      printf 'Enter a username and password.\n' >&2
      exit 2
    fi
    {
      printf 'EDITOR_USERNAME=%s\n' "$editor_username"
      printf 'EDITOR_PASSWORD=%s\n' "$editor_password"
      printf 'EDITOR_SESSION_KEY=%s\n' "$(openssl rand -hex 32)"
      printf 'PUBLIC_ORIGIN=http://www.iam-039.com\n'
    } > "$secret_file"
    "${k[@]}" -n id-039 create secret generic research-editor-secret \
      --from-env-file="$secret_file" --dry-run=client -o yaml |
      "${k[@]}" apply --server-side --field-manager=k8sfinal -f -
    ;;
  deploy)
    nodes=$("${k[@]}" get nodes -o name)
    if [[ $nodes != "node/$node" ]]; then
      printf 'Expected one node named %s.\n' "$node" >&2
      exit 1
    fi
    docker exec "$node" install -d -m 0750 -o 10001 -g 10001 /var/local/k8sfinal/site-content
    "${k[@]}" wait --for=condition=Ready "node/$node" --timeout=120s
    "${k[@]}" -n id-039 get secret research-editor-secret -o name
    "${k[@]}" apply --dry-run=server -f k8s/
    "${k[@]}" apply -f k8s/
    "${k[@]}" -n id-039 rollout restart deployment/portal-039 deployment/app-research \
      deployment/api-039 deployment/admin-039 deployment/gateway-039
    for app in portal-039 app-research api-039 admin-039 gateway-039; do
      "${k[@]}" -n id-039 rollout status "deployment/$app" --timeout=300s
    done
    "${k[@]}" -n id-039 get deploy,pods,svc,pvc -o wide
    ;;
  *)
    printf 'Usage: bash deploy.sh {cluster|build|secret|deploy}\n' >&2
    exit 2
    ;;
esac
