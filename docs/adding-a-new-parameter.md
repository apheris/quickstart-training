# Modifying the code: Adding a new parameter

If you want to take more parameters from the command line, you need to add them to the
Secure Runtime and the FLARE components you want to use it.

First, add the parameter to the LogisticRegressionPayload, which you'll find in
[src/ard_demo/secure_runtime/payload.py](../src/ard_demo/secure_runtime/payload.py). This
is a Pydantic model object that deserialises and validates the JSON payload.

We'll work through this with an example, adding a normalisation parameter to the payload:

```python
class LogisticRegressionPayload(BaseModel):
    task_id: TaskID
    dataset_id: str
    file_in_dataset: Optional[str] = None
    derived_dataset_prefix: Optional[str] = "derived"

    # A new parameter for normalisation, defaults to 1
    normalisation_parameter: float = 1.

    # ...
```

Next, add it to the constructor of the component you want to use your parameter. Most
likely, this will be the [TrainingExecutor](../src/ard_demo//model/executor.py).

Continuing the example above...

```python
class TrainingExecutor(ServerLoggingMixin, Executor):
    def __init__(
        self,
        dataset_id: str,
        file_in_dataset: str,
        derived_dataset_prefix: str = "derived",
        normalisation_parameter: float = 1.
    ):
        super().__init__()

        self.dataset_id = dataset_id
        self.file_in_dataset = file_in_dataset
        self.derived_dataset_prefix = derived_dataset_prefix

        self.normalisation_parameter = normalisation_parameter
        
        # ...
```

Now we just need to connect the payload received by the Secure Runtime with the Executor.
We do this by adding the new parameter to the FLARE config files in the Secure Runtime.

These configs can be quite complex, and the finer details are beyond the scope of this
guide, but for now, we'll see how to map the argument through to the config of the
`TrainingExecutor`.

The [`template` function](../src/ard_demo/secure_runtime/secure_runtime_service.py) is
used by the Secure Runtime to build the config files, based on the payload and the
templates stored in [secure_runtime/templates](../src/ard_demo/secure_runtime/templates/).

Inside that directory is [`loaders.py`](../src/ard_demo/secure_runtime/templates/loaders.py),
which contains the files that load and populate the templates.

Here is the template configuration for the Gateway's executor:

```json
{
  "format_version": 2,
  "executors": [
    {
      "tasks": [
        "list_files",
        "download_data",
        "run"
      ],
      "executor": {
        "path": "ard_demo.model.executor.TrainingExecutor",
        "args": {}
      }
    }
  ],
  "task_result_filters": [],
  "task_data_filters": [],
  "components": []
}
```

Note the `args` field - that's where you need to pass in your parameter. In the template,
it's empty, which is because the field is populated in the `_load_client_config` function
in [`loaders.py`](../src/ard_demo/secure_runtime/templates/loaders.py).

Now it's just a case of modifying the loader with the new parameter:

```python
def _load_client_config(payload: LogisticRegressionPayload) -> dict:
    """
    Load the FLARE client config template and populate with data from the job payload
    """
    with open(TEMPLATE_PATH / "conf_fed_client.json.template") as fh:
        config = json.load(fh)

    args = config["executors"][0]["executor"]["args"]

    # We set the arguments to the executor using the values from the payload
    args["dataset_id"] = payload.dataset_id
    args["file_in_dataset"] = payload.file_in_dataset
    args["derived_dataset_prefix"] = payload.derived_dataset_prefix

    # Add your new parameter here
    args["normalisation_parameter"] = payload.normalisation_parameter

    return config
```

That's it! Now you just need to update the model in the
[Apheris Model Registry](custom-model-workflow.md) and start using it!
