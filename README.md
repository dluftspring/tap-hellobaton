# tap-hellobaton

`tap-hellobaton` is a Singer tap for [hellobaton](https://www.hellobaton.com/).

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install directly from the repo source using pip

```bash
pip install git+https://github.com/dluftspring/tap-hellobaton.git
```

## Configuration

### Accepted Config Options

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-hellobaton --about
```

You'll need to supply three major configurations in a  `config.json` file

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


### Running ELT with [Meltano](https://www.meltano.com)

TODO

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any _"TODO"_ items listed in
the file.

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-hellobaton
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-hellobaton --version
# OR run a test `elt` pipeline:
meltano elt tap-hellobaton target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to 
develop your own taps and targets.
