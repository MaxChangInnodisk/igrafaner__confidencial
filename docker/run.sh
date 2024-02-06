#!/bin/bash

function is_absolute_path {
  local path="$1"
  if [[ "$path" == /* ]]; then
    return 0  # 是绝对路径
  else
    return 1  # 不是绝对路径
  fi
}

# Move to docker folder
DOCKER_FOLDER=$(dirname "${0}")
ROOT=$(dirname ${DOCKER_FOLDER})
cd ${ROOT}

config_file="${DOCKER_FOLDER}/config.ini"
if [ ! -f "$config_file" ]; then
  echo "Error: Config file '$config_file' does not exist."
  exit 1
fi

# Get data
source <(grep = ${config_file})
DOCKER_IMAGE="${PROJECT}:${VERSION}"
WORKSPACE="/workspace"

SAMPLE_PATH="${WORKSPACE}/sample"
GOLDEN_PATH="${WORKSPACE}/golden"
MODEL_NAME=$(basename ${MODEL})
MODEL_PATH="${WORKSPACE}/model/${MODEL_NAME}"

LOG_NAME=$(basename ${LOG_PATH})
CNTR_LOG_PATH="${WORKSPACE}/${LOG_NAME}"

# Verify
variables=("SAMPLE" "GOLDEN" "MODEL")
for var in "${variables[@]}"; do
  value="${!var}"  # 获取变量的值
  if ! $(is_absolute_path "$value"); then
    echo "$var in config.ini should be an absolute path ( $value )"
    exit 1;
  fi
done

# Execute 
docker run -it \
--rm \
--gpus all \
--name igrafaner \
--net=host \
-w ${WORKSPACE} \
-v ${SAMPLE}:${SAMPLE_PATH} \
-v ${GOLDEN}:${GOLDEN_PATH} \
-v ${MODEL}:${MODEL_PATH} \
-v ${LOG_PATH}:${CNTR_LOG_PATH} \
${DOCKER_IMAGE} \
igra-cli \
--mysql-host=${HOST} \
--mysql-port=${PORT} \
--mysql-username=${USERNAME} \
--mysql-password=${PASSWORD} \
--mysql-database=${DATABASE} \
--start-time="${START_TIME}"  \
--end-time="${END_TIME}"  \
--model-path=${MODEL_PATH} \
--golden-folder=${GOLDEN_PATH} \
--mount-folder=${SAMPLE_PATH}