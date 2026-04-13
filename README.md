# Kubeflow

Made up components which you can install the entire ecosystem or just pick the ones you use. Kubeflow components are:

- Dashboard
- Pipelines
- KServe
- Katib (i.e. AutoML)
- Notebooks
- Trainer
- Spark Operator

## Requirements
- Minimum install requires 1 node with 4vCPUs / 16GB mem + extra for any Notebooks you wish to run
- Full install requires 2 nodes with 4vCPUs / 16GB mem + extra for any Notebooks you wish to run


## Setup via Taskfile
Requires: [Task](https://taskfile.dev/)

> [!NOTE]
> `Taskfile.yaml_STANDALONE` contains tasks to install some of Kubeflow's components as standalone.
> This file is not maintained/updated and was something I created/used initially to test Kubeflow components.

Main tasks:
- `kf:common:setup` installs the prerequisite common components
- `all:min` installs Kubeflow applications: Dashboard, Pipelines, KServe and Notebooks 
- `all` installs all Kubeflow applications
- `kf:port-ward:ui` set up port-forwarding so you can access the UI (unless you have a loadbalancer setup)

 
## Single-command Setup 
Install details, see: [Kubeflow manifests repository](https://github.com/kubeflow/manifests). I have included a `kustomization.yaml` which can be used with the following while-loop:

```sh
while ! kustomize build . | kubectl apply --server-side --force-conflicts -f -; do echo "Retrying to apply resources"; sleep 20; done
```

Use `task clean` to delete the single-command setup (it's difficult to do a one-shot cleanup)


- Port-forward the Kubeflow UI:
```sh
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

## TODO
- Kubeflow examples

