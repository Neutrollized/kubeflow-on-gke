# Examples

## Requirements
**istio-ingressgateway:8080** — client initializes (healthz passes via cookie), but list_experiments fails because the cookie auth doesn't propagate the user identity header
**ml-pipeline:8888** — no cookie needed, but you must inject kubeflow-userid header manually
