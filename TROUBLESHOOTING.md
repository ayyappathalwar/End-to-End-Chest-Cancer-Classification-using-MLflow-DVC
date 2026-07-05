# Troubleshooting Log

Running record of mistakes/errors hit while working on this project and how they were fixed. Newest entries at the top.

---

## `AttributeError: 'PredictionPipeline' object has no attribute 'predict'`

**Date:** 2026-07-04
**Where:** `app.py` `/predict` route → `src/cnnClassifier/pipeline/prediction.py`

**Mistake / cause:**
Two bugs in `PredictionPipeline`:
1. The method was misspelled `predcit` instead of `predict`, so `app.py`'s call to `clApp.classifier.predict()` failed outright.
2. It loaded the model from `artifacts/model/model.h5`, but the actual trained model (per `config/config.yaml`'s `trained_model_path`) is saved at `artifacts/training/model.h5` — wrong directory.

**Remedy:**
```python
def predict(self):
    model = load_model(os.path.join("artifacts", "training", "model.h5"))
    ...
```

**Note (also fixed separately):** locally, `app.py`'s hardcoded `port=8080` failed with a Windows socket permission error because port 8080 was already bound by the `IP Helper` (`iphlpsvc`) system service. Made the port configurable via `PORT` env var (defaults to 8080, use `PORT=5000 python app.py` locally).

---

## `MlflowException` 404 recurring via `dvc repro` after `main.py` fix

**Date:** 2026-07-03
**Where:** `src/cnnClassifier/components/mode_evaluation_mlflow.py`, `log_into_mlflow()`, invoked via `dvc.yaml`'s `evaluation` stage

**Mistake / cause:**
Earlier we added `load_dotenv(override=True)` to `main.py` to guarantee `.env` always wins over stray shell-exported `MLFLOW_TRACKING_URI` values. But `dvc.yaml`'s `evaluation` stage calls `python src/cnnClassifier/pipeline/stage_04_model_evaluation.py` directly — it never goes through `main.py`, so that fix never took effect for `dvc repro`. Additionally, `log_into_mlflow()` only ever called `mlflow.set_registry_uri(self.config.mlflow_uri)`, never `mlflow.set_tracking_uri(...)` — the tracking URI (used by `start_run`/`create_run`) was left entirely dependent on the `MLFLOW_TRACKING_URI` env var, which still lacked the `.mlflow` suffix in the ambient shell.

**Remedy:**
Fixed at the source (`mode_evaluation_mlflow.py`) instead of the entry-point scripts, so it works no matter what invokes it:
```python
from dotenv import load_dotenv
load_dotenv(override=True)
...
def log_into_mlflow(self):
    mlflow.set_tracking_uri(self.config.mlflow_uri)
    mlflow.set_registry_uri(self.config.mlflow_uri)
    ...
```

**Lesson:** when a pipeline has multiple entry points (`main.py`, `dvc.yaml` per-stage `cmd:`, notebooks), don't put environment-loading logic only in one entry point — put it in the component/module that actually needs it, or every other entry point will silently skip it.

---

## `MlflowException` 404 at `/api/2.0/mlflow/runs/create` when running `python main.py`

**Date:** 2026-07-02
**Where:** `main.py` → `stage_04_model_evaluation` → `Evaluation.log_into_mlflow()` → `mlflow.start_run()`

**Mistake / cause:**
Unlike the notebook, `main.py` never loaded `.env` or set `MLFLOW_TRACKING_URI`/`MLFLOW_TRACKING_USERNAME`/`MLFLOW_TRACKING_PASSWORD` itself — it silently depended on whatever was already present in the shell's environment. The terminal running `main.py` still had a stale `MLFLOW_TRACKING_URI` exported (missing the `.mlflow` suffix, from following the old README instructions before that got fixed), which overrode the correct value in `.env`/`src/cnnClassifier/config/configuration.py`. Without `.mlflow`, DagsHub returns its normal repo HTML page for API calls instead of a JSON response — same class of error as the earlier registry-URI bug, but this time on the tracking API (`create_run`) instead of the registry API.

**Remedy:**
Added `.env` loading directly to `main.py` so the pipeline is self-contained and not dependent on manual shell `export`s:
```python
from dotenv import load_dotenv
load_dotenv(override=True)
```
`override=True` ensures `.env` always wins over any stray/incorrect variables already present in the shell — important since this script will eventually run in CI/CD and on an EC2 instance, not just an interactive terminal.

---

## `MlflowException` (HTML response) at `mlflow.keras.log_model(..., registered_model_name=...)`

**Date:** 2026-07-02
**Where:** `reseacrh/04_model_evaluation_with_mlflow.ipynb`, `Evaluation.log_into_mlflow()`

**Mistake / cause:**
Two compounding issues:
1. `eval_config.mlflow_uri` (set in `ConfigurationManager.get_evaluation_config()`) was missing the `.mlflow` suffix that DagsHub requires for its MLflow API endpoint, unlike `MLFLOW_TRACKING_URI` which had it. `mlflow.set_registry_uri()` was pointed at the plain repo URL, so registry API calls hit the repo's webpage instead of the API.
2. Even with the URI fixed, `mlflow.keras.log_model(self.model, "model", registered_model_name="VGG16Model")` still failed: DagsHub's hosted MLflow tracking server does not support the Model Registry API that `registered_model_name` triggers. The proxy falls through to its SPA and returns an HTML page instead of a JSON API response, which mlflow can't parse — surfaced as an `MlflowException` whose message ends in raw `</html>` (and gets truncated by the notebook UI, making it look empty).

**Remedy:**
- Added `.mlflow` to `eval_config.mlflow_uri` in `ConfigurationManager.get_evaluation_config()`.
- Removed `registered_model_name="VGG16Model"` from the `mlflow.keras.log_model()` call — just log the model without registering it:
```python
mlflow.keras.log_model(self.model, "model")
```

**Note:** after editing a notebook cell via a tool/script, doing Ctrl+S in VSCode can silently overwrite that edit with the editor's own in-memory buffer if the notebook was already open. Re-check the cell after saving if edits seem to have reverted.

---

## `FileNotFoundError: scores.json` in `Evaluation.save_score()`

**Date:** 2026-07-02
**Where:** `reseacrh/04_model_evaluation_with_mlflow.ipynb`, `evaluation.evaluation()` → `save_score()` → `save_json()`

**Mistake / cause:**
`save_json()` in `src/cnnClassifier/utils/common.py` was implemented backwards — despite its name, it opened the target `path` in **read** mode and called `json.load()`, completely ignoring the `data` argument it was supposed to write. So the first time `save_score()` tried to persist `scores.json`, it attempted to read a file that didn't exist yet, and crashed with `FileNotFoundError`.

**Remedy:**
Fixed `save_json()` to actually write:

```python
@ensure_annotations
def save_json(path: Path, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    logger.info(f"json file saved at: {path}")
```

Re-run the evaluation cell after this fix.

---

## `ModuleNotFoundError: No module named 'pkg_resources'` when importing `mlflow`

**Date:** 2026-07-02
**Where:** `reseacrh/04_model_evaluation_with_mlflow.ipynb`, cell importing `mlflow`

**Mistake / cause:**
The `cancerpro` conda env had `setuptools` upgraded to `82.0.1`. Recent `setuptools` releases (80+) drop the legacy `pkg_resources` module by default. `mlflow.utils.requirements_utils` still hard-imports `pkg_resources`, so `import mlflow` failed.

**Remedy:**
Pin `setuptools` below the version that removed `pkg_resources`:

```bash
"c:/ProgramData/miniconda3/envs/cancerpro/python.exe" -m pip install "setuptools<81" --force-reinstall
```

This installed `setuptools 80.10.2`, which still ships `pkg_resources` (with a deprecation warning — fine for now).

**Note:** unrelated pip dependency warning also appeared (`tensorflow-intel 2.13.0 requires typing-extensions<4.6.0`) — pre-existing, does not block mlflow, ignore unless TF breaks.
