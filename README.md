# iGrafaner
The Grafana application with AI inference for Innodisk's Assembly Line.

# Prepare model
```bash
/path/to/meta/data
├── golden
├── golden_info.json
├── inference_info.json
├── oi_model.onnx
└── panel_info.json
```

# Docker Usage
* Requirements
  * GPU Driver
  * Docker Engine
* Build docker image
    ```bash
    docker/build.sh
    ```
* Setup environment
  ```ini
  [IGRAFANER]
  sample=/path/to/sample_folder
  golden=/path/to/golden_folder
  model=/path/to/onnx_model
  ```
* Run docker container via shell script
  ```bash
  ./docker/run.sh
  ```

# Local Usage
* Requirements
  * GPU Driver
  * python3 ( 3.10 is recommended )
  * Virtualenv, VirtualenvWrapper
* Prepare environment
    ```bash
    mkvirtualenv igra
    ```
* Enter environment
    ```bash
    workon igra
    ```
* Install
    ```bash
    pip install -e .
    ```
* Execute with `igra-cli`
    - golden folder should have `golden`, `inference_info.json`.
    - sample folder shouldn't include `/MAP`
    ```bash
    igra-cli \
    --mysql-host=${HOST} \
    --mysql-port=${PORT} \
    --mysql-username=${USERNAME} \
    --mysql-password=${PASSWORD} \
    --mysql-database=${DATABASE} \
    --start-time="${START_TIME}" \
    --end-time="${END_TIME}" \
    --model-path=${MODEL_PATH} \
    --golden-folder=${GOLDEN_PATH} \
    --mount-folder=${SAMPLE_PATH}
    ```
    See more detail: `igra-cli -h`

