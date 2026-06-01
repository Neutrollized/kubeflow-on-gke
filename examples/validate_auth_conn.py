import warnings

# Filter out the specific FutureWarning from the kfp client module
warnings.filterwarnings(
    "ignore", 
    category=FutureWarning, 
    module="kfp.client.client"
)


import kfp

print(" >> istio-ingressgateway:8080 — client initializes (healthz passes via cookie), but list_experiments fails because the cookie auth doesn't propagate the user identity header\n")

YOUR_NAMESPACE = "kubeflow-user-example-com"

client = kfp.Client(
    host="http://localhost:8080",
    namespace=YOUR_NAMESPACE,
)

# See what attributes the client has
print([a for a in dir(client) if not a.startswith('__')])

#--------------------------------------------------------------

print("\n--------------------\n")
print(" >> ml-pipeline:8888 — no cookie needed, but you must inject kubeflow-userid header manually\n")

YOUR_EMAIL = "user@example.com"

client = kfp.Client(
    host="http://localhost:8888",
    namespace=YOUR_NAMESPACE,
)

# Inject the user identity header into the shared api_client
#client._experiment_api.api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)
#client._run_api.api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)
#client._pipelines_api.api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)
#client._upload_api.api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)
#client._recurring_run_api.api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)

# Patch all internal api clients at once
for attr in dir(client):
    if attr.startswith("_") and hasattr(getattr(client, attr), "api_client"):
        getattr(client, attr).api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)

print(client.list_experiments())
