# Kubeflow

Made up components which you can install the entire ecosystem or just pick the ones you use. Kubeflow components are:

- Dashboard
- Pipelines
- KServe
- Katib (i.e. AutoML)
- Notebooks
- Trainer
- Spark Operator


## Setup via Taskfile
Requires: [Task](https://taskfile.dev/)

> [!NOTE]
> `Taskfile.yaml_STANDALONE` contains tasks to install some of Kubeflow's components as standalone.
> This file is not maintained/updated and was something I created/used initially to test Kubeflow components.

Main tasks:
- `kf:common:setup` installs the prerequisite common components
- `all:min` installs Kubeflow applications: Dashboard, Pipelines, KServe and Notebooks 
- `all` installs all Kubeflow applications

 
## TODO
- Kubeflow examples
- Single-command full install (see [Kubeflow manifests repository](https://github.com/kubeflow/manifests) for details).  I have included a `kustomization.yaml` file with some notes, but this isn't currently being used

