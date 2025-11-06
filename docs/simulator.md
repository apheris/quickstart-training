# Running locally with the FLARE simulator

Included with this repository is a harness for the FLARE simulator that allows you to
run the model against a local dataset to debug it on your machine before pushing to
Apheris.

The simulator harness wraps functionality that is used within the Apheris system, such
as the Secure Runtime's templating functions, and hooks into the DAL to use local files
instead of trying to pull via the remote endpoint.

To use it, you run the `run_simulator.py` script in `src/logistic_regression_quickstart`.
At a minimum, you must provide a dataset ID. You also need to be logged into Apheris, as
the Dummy Data, which is assigned to the Apheris dataset, needs to be downloaded from
an Apheris server.

The following shows an example run using a single dataset:

```console
python3 src/logistic_regression_quickstart/run_simulator.py --dataset-ids whas1_gateway-1_org-1
```

## Output

The output of the simulator is stored in the simulator's workspace directory. By default
this is called `simulator_output` and lies in the current working directory. You can
override this path using the `--simulator-output-path` parameter. If the path doesn't
exist, it will be created.

You'll see FLARE is quite noisy. It's possible to [configure FLARE to provide less
logging](https://nvflare.readthedocs.io/en/main/user_guide/configurations/logging_configuration.html),
but for this demo we have left all logging enabled.

At the end of the run, you should see either a success message or a summary of which tasks
have failed. You can use this to help find where to look in the logs from FLARE.

If all is well, you will see something that looks like this:

```console
...
INFO:SimulatorRunner:return_code from process.exitcode: 0
Simulator run completed successfully. Workspace output stored in /path/to/repo/simulator_output/workspace
```

### The workspace

After running the demo, you'll see a number of files inside the `simulator_output`
directory - this encapsulates the entire FLARE workspace, including the configuration and
output of both FLARE server and client(s).

The trained model weights are written to `simulator_output/workspace/server/simulate_job/models/server.npy`.

You can see the downloaded Dummy Data in `simulator_output/workspace/site-1/simulate_job/app_site-1/datasets/whas1_gateway-1_org-1/whas1_gateway-1_org-1`.

> [!NOTE]
> In a real Apheris run, you would never gain access to the data as it's sensitive, but for the simulator, we use non-sensitive Dummy Data.

You can also view the text logs from both server and client in their respective sub-directories.

The full directory output of this example is shown below:

```console
tree simulator_output 
simulator_output
├── jobs
│   ├── app
│   │   └── config
│   │       ├── config_fed_client.json
│   │       └── config_fed_server.json
│   └── meta.json
├── persisted
└── workspace
    ├── local
    ├── server
    │   ├── local
    │   │   └── log_config.json
    │   ├── log.json
    │   ├── log.txt
    │   ├── log_error.txt
    │   ├── log_fl.txt
    │   ├── pool_stats
    │   │   └── simulator_cell_stats.json
    │   ├── simulate_job
    │   │   ├── app_server
    │   │   │   └── config
    │   │   │       ├── config_fed_client.json
    │   │   │       └── config_fed_server.json
    │   │   ├── meta.json
    │   │   └── models
    │   │       └── server.npy
    │   └── startup
    ├── site-1
    │   ├── local
    │   │   └── log_config.json
    │   ├── log.json
    │   ├── log.txt
    │   ├── log_error.txt
    │   ├── simulate_job
    │   │   ├── app_site-1
    │   │   │   ├── config
    │   │   │   │   ├── config_fed_client.json
    │   │   │   │   └── config_fed_server.json
    │   │   │   └── datasets
    │   │   │       └── whas1_gateway-1_org-1
    │   │   │           └── whas1_gateway-1_org-1
    │   │   └── meta.json
    │   └── startup
    └── startup
24 directories, 21 files
```

#### The `jobs` directory

The `jobs` directory contains the FLARE configs created by the secure_runtime. This is
useful for debugging issues when your components don't seem to be configured properly -
you can check the configs and ensure parameters are passed through to FLARE correctly by
the secure runtime's `template` function.

#### The `workspace` directory

This contains the entire FLARE workspace, including the server and client's logs, configs,
etc. The `workspace/simulated_job/app_server` directory is essentially what you would
download using the `apheris job download-results` with the CLI if you ran a remote job.
