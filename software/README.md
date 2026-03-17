# DOPFLOW Python Software

## Installation

You can install the dependencies using either Conda or uv. I recommend using uv. Both methods will set up a Python environment with all the necessary packages to run the DOPFLOW GUI.

### Conda

1. Install Anaconda package manager
   <https://docs.conda.io/en/latest/miniconda.html>
2. Find `requirements.yaml` file in
3. Open terminal (Windows: Anaconda Prompt).
4. Execute the following command to create environment:

    ```bash
    conda env create -f requirements.yml
    ```

5. In a new terminal launch

    ```bash
    conda activate phantom_env
    ```

### uv

1. Install uv <https://docs.astral.sh/uv/getting-started/installation/>
2. Navigate to the `software/` folder in the terminal
3. To download and install the dependencies, run the following command:

    ```bash
    uv sync
    ```

## Usage

To launch the GUI run the following command:

```bash
python speed_control.py # With .venv activated
uv run speed_control.py # With uv
```
