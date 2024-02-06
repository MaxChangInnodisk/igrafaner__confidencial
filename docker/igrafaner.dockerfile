FROM nvcr.io/nvidia/cuda:12.3.1-runtime-ubuntu22.04

ARG USERNAME=igra
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    #
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && apt-get install -y python3-dev python3-pip libglib2.0-0 libsm6 libgl1-mesa-glx libxrender1 libxext6

# ********************************************************
# * Anything else you want to do like clean up goes here *
# ********************************************************

WORKDIR /opt/inno
COPY [ "setup.py", "requirements.txt", "./" ]
RUN pip install -r requirements.txt

COPY [ "src", "./src" ]
RUN chown ${USER_GID}:${USER_UID} -R /opt/inno/src
RUN pip install --no-deps -e .

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME
