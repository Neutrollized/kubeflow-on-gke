import warnings

# Filter out the specific FutureWarning from the kfp client module
warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module="kfp.client.client"
)


import kfp
from kfp import dsl
from kfp.dsl import component, pipeline, Dataset, Model, Metrics, Input, Output

# ── Connection setup ───────────────────────────────────────────────────────────
YOUR_EMAIL = "user@example.com"           # kubectl get profile -o yaml | grep name:
YOUR_NAMESPACE = "kubeflow-user-example-com"

def get_client() -> kfp.Client:
    client = kfp.Client(
        host="http://localhost:8888",
        namespace=YOUR_NAMESPACE,
    )
    for attr in dir(client):
        if attr.startswith("_") and hasattr(getattr(client, attr), "api_client"):
            getattr(client, attr).api_client.set_default_header("kubeflow-userid", YOUR_EMAIL)
    return client


# ── Component 1: Data ingestion ────────────────────────────────────────────────
@component(
    base_image="python:3.13-slim",
    packages_to_install=["pandas", "scikit-learn"],
)
def ingest_data(output_dataset: Output[Dataset]):
    from sklearn.datasets import load_iris
    import pandas as pd

    df = pd.DataFrame(
        load_iris().data, columns=["sepal_len", "sepal_wid", "petal_len", "petal_wid"]
    )
    df["target"] = load_iris().target
    df.to_csv(output_dataset.path, index=False)


# ── Component 2: Preprocessing ─────────────────────────────────────────────────
@component(
    base_image="python:3.13-slim",
    packages_to_install=["pandas", "scikit-learn"],
)
def preprocess(
    input_dataset: Input[Dataset],
    train_dataset: Output[Dataset],
    test_dataset: Output[Dataset],
    test_size: float = 0.2,
):
    import pandas as pd
    from sklearn.model_selection import train_test_split

    df = pd.read_csv(input_dataset.path)
    train, test = train_test_split(df, test_size=test_size, random_state=42)
    train.to_csv(train_dataset.path, index=False)
    test.to_csv(test_dataset.path, index=False)


# ── Component 3: Training ──────────────────────────────────────────────────────
@component(
    base_image="python:3.13-slim",
    packages_to_install=["pandas", "scikit-learn", "joblib"],
)
def train_model(
    train_dataset: Input[Dataset],
    model: Output[Model],
    n_estimators: int = 100,
):
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    import joblib

    df = pd.read_csv(train_dataset.path)
    X, y = df.drop("target", axis=1), df["target"]

    clf = RandomForestClassifier(n_estimators=n_estimators, random_state=42)
    clf.fit(X, y)

    joblib.dump(clf, model.path)
    model.metadata["framework"] = "sklearn"


# ── Component 4: Evaluation ────────────────────────────────────────────────────
@component(
    base_image="python:3.13-slim",
    packages_to_install=["pandas", "scikit-learn", "joblib"],
)
def evaluate_model(
    test_dataset: Input[Dataset],
    model: Input[Model],
    metrics: Output[Metrics],
    accuracy_threshold: float = 0.90,
) -> bool:
    import pandas as pd
    from sklearn.metrics import accuracy_score, f1_score
    import joblib

    df = pd.read_csv(test_dataset.path)
    X, y = df.drop("target", axis=1), df["target"]

    clf = joblib.load(model.path)
    preds = clf.predict(X)

    acc = accuracy_score(y, preds)
    f1 = f1_score(y, preds, average="weighted")

    metrics.log_metric("accuracy", round(acc, 4))
    metrics.log_metric("f1_score", round(f1, 4))

    print(f"Accuracy: {acc:.4f} | F1: {f1:.4f}")
    return acc >= accuracy_threshold


# ── Component 5: Deploy ────────────────────────────────────────────────────────
# dummy deploy
@component(base_image="python:3.13-slim")
def deploy_model(model: Input[Model], endpoint: str = "iris-classifier"):
    print(f"Deploying model from {model.path} to endpoint '{endpoint}'")
    print(f"Model framework: {model.metadata.get('framework', 'unknown')}")


# ── Pipeline definition ────────────────────────────────────────────────────────
@pipeline(
    name="iris-training-pipeline",
    description="End-to-end ML pipeline: ingest → preprocess → train → evaluate → deploy",
)
def iris_pipeline(
    test_size: float = 0.2,
    n_estimators: int = 100,
    accuracy_threshold: float = 0.90,
    endpoint: str = "iris-classifier",
):
    ingest_task = ingest_data()

    preprocess_task = preprocess(
        input_dataset=ingest_task.outputs["output_dataset"],
        test_size=test_size,
    )

    train_task = train_model(
        train_dataset=preprocess_task.outputs["train_dataset"],
        n_estimators=n_estimators,
    )

    eval_task = evaluate_model(
        test_dataset=preprocess_task.outputs["test_dataset"],
        model=train_task.outputs["model"],
        accuracy_threshold=accuracy_threshold,
    )

    #with dsl.If(eval_task.output == True, name="accuracy-gate"):
    with dsl.If(eval_task.outputs['Output'] == True, name="accuracy-gate"):
        deploy_model(
            model=train_task.outputs["model"],
            endpoint=endpoint,
        )


# ── Compile & submit ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Compile to YAML
    kfp.compiler.Compiler().compile(
        pipeline_func=iris_pipeline,
        package_path="iris_pipeline.yaml",
    )
    print("Pipeline compiled → iris_pipeline.yaml")

    # Connect and submit
    client = get_client()

    run = client.create_run_from_pipeline_func(
        iris_pipeline,
        arguments={
            "n_estimators": 100,
            "accuracy_threshold": 0.90,
        },
        run_name="iris-run-01",
        experiment_name="iris-experiments",
        namespace=YOUR_NAMESPACE,
    )

    print(f"Run ID:  {run.run_id}")
    print(f"Run URL: http://localhost:8080/pipeline/#/runs/details/{run.run_id}")

    # Optionally block until completion
    result = run.wait_for_run_completion(timeout=600)
    print(f"Status: {result.state}")
