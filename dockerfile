FROM ros:humble

RUN apt-get update && apt-get install -y \
    ros-humble-ros-gz \
    ignition-fortress \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-c"]

RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

WORKDIR /app

COPY scripts/run_simulation.sh /app/run_simulation.sh
COPY worlds /app/worlds

RUN chmod +x /app/run_simulation.sh

CMD ["/bin/bash", "/app/run_simulation.sh"]
