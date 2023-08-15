# tap-hellobaton

`tap-hellobaton` is a Singer tap for [hellobaton](https://www.hellobaton.com/).

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install directly from the repo source using pip

```bash
pip install git+https://github.com/dluftspring/tap-hellobaton.git
```

### For developers

Install the dev dependencies using [poetry](https://python-poetry.org/)

```bash
~$ poetry install
```

Then make sure the tests are passing locally

```bash
~$ poetry run pytest
```


## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-hellobaton --about
```

You'll need to supply three config parameters

| Parameter | Description | Type | Env Variable Alias |
| :-------- | :---------- | :--- | :----------------- |
| company | Your company instance used in the api url | string (required) | TAP_HELLOBATON_COMPANY |
| api_key | Api key for authentication | string (required) | TAP_HELLOBATON_API_KEY |
| user_agent | User agent to appear in monitoring jobs | string (optional) | TAP_HELLOBATON_USER_AGENT |

You can set these parameters as environment variables or by specifying a json configuration file with the following info

```json

  {
    "company": "<YOUR COMPANY>",
    "api_key": "<YOUR API KEY>",
    "user_agent": "<USER AGENT STRING>"
  }
```

## Usage

You can easily run `tap-hellobaton` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

To see a catalog of the available json schemas you can run the tap in discovery mode

```bash
tap-hellobaton --version
tap-hellobaton --help
tap-hellobaton --config CONFIG_FILE_PATH --discover > ./catalog.json
```

To execute the tap directly from the cli

```bash
tap-hellobaton --config CONFIG_FILE_PATH
```

### Executing with Incremental Replication
Incremental replication means the tap will only query and emit data which was modified since the last import. This is faster than running a full table import. If you are using this tap with Meltano, please read their documentation on [Key-based Incremental Replication](https://docs.meltano.com/guide/integration/#key-based-incremental-replication).

First, generate the `catalog.json` file by running the tap in discovery mode.
```bash
tap-hellobaton --config ./config.json --discover > catalog.json
```

Next, run a full sync and generate the initial state file (`state.json`).
```bash
tap-hellobaton --config ./config.json --catalog catalog.json >> state.json
tail -1 state.json | cut -c 27- | rev | cut -c 2- | rev  > state.json.tmp && mv state.json.tmp state.json
```

From here, all subsequent syncs can be take advantage of incremental replication by reusing the `state.json` file generated in the previous step. The second line here is important as it will update the `state.json` to reflect the most recent run.
```bash
tap-hellobaton --config ./config.json --catalog catalog.json --state state.json >> state.json
tail -1 state.json | cut -c 27- | rev | cut -c 2- | rev  > state.json.tmp && mv state.json.tmp state.json
```

Now you may repeat step 3 to continuously sync only the most recently modified data. If you need to do a full sync, delete the `state.json` file and begin from step 1.

More information on how to use incremental replication while piping output to a Target can be found here under [Running a Singer Tap with a Singer Target](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md#running-a-singer-tap-with-a-singer-target).

### Running ELT with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

First install Meltano (if you haven't already) and any needed plugins. It's recommended that you do this in a virtual environment

```bash
# Install meltano
pip install meltano
# Initialize meltano within this directory
meltano init
```

This will create a new meltano project in your working directory. You can edit the `meltano.yml` file with the following minimal configurations

```yaml
version: 1
send_anonymous_usage_stats: true
project_id: c817018d-de7b-45fb-9fff-260fa84ddaf9
plugins:
  extractors:
  - name: tap-hellobaton
    namespace: tap_hellobaton
    pip_url: git+https://github.com/dluftspring/tap-hellobaton.git
    executable: tap-hellobaton
    capabilities:
    - catalog
    - state
    - discover
    settings:
    - name: company
      kind: string
    - name: api_key
      kind: password
    - name: user_agent
      kind: string
    config:
      company: YOUR_COMPANY
      user_agent: Singer Tap for hellobaton
    load_schema: YOUR_LOAD_SCHEMA
```

You can now install the tap with meltano using

```bash
meltano install
```

Lastly, you should add the api key to your configuration

```bash
meltano config tap-hellobaton set api_key YOUR_API_KEY
#now we can check if all the configs are properly set

meltano config tap-hellobaton list
company [env: TAP_HELLOBATON_COMPANY] current value: 'YOUR COMPANY' (from `meltano.yml`)
api_key [env: TAP_HELLOBATON_API_KEY] current value: 'YOUR API KEY' (from `.env`)
user_agent [env: TAP_HELLOBATON_USER_AGENT] current value: 'YOUR USER AGENT' (from `meltano.yml`)
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-hellobaton --version
# OR run a test `elt` pipeline:
meltano elt tap-hellobaton target-jsonl
# Google bigquery example
meltano elt tap-hellobaton target-bigquery
```

Note that to use the target-jsonl with a new meltano project you'll have to add the configuration to your `meltano.yml` project file and install the plugin. NOTE: make sure your destination path exists in the project directory or the command will throw an error

```yaml
- name: target-jsonl
    variant: andyh1203
    pip_url: target-jsonl
    config:
      destination_path: load/jsonl_target_tests
```

To use the target-bigquery with a new meltano project you'll have to add the configuration to your `meltano.yml` project file and install the plugin. Follow the instructions to configure the [bigquery target](https://github.com/adswerve/target-bigquery#step-1-enable-google-bigquery-api).

```yaml
# For bigquery
loaders:
- name: target-bigquery
  variant: adswerve
  pip_url: git+https://github.com/adswerve/target-bigquery.git@0.12.2
  config:
    project_id: {your gcp project}
    dataset_id: {your gcp dataset id}
    validate_records: true
  settings:
  - name: project_id
    kind: string
  - name: dataset_id
    kind: password
  - name: location
    kind: string
  - name: credentials_path
    kind: string
  - name: add_metadata_columns
    kind: boolean
```

