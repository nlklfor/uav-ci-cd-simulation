FROM ros:humble

RUN apt-get update && apt-get install -y \
    ros-humble-ros-gz \
    ros-humble-cv-bridge \
    ignition-fortress \
    python3-pip \
    python3-opencv \
    xvfb \
    libgl1-mesa-dri \
    libgles2 \
    libegl1 \
    && rm -rf /var/lib/apt/lists/*

SHELL ["/bin/bash", "-c"]

WORKDIR /app

COPY ros2_ws/src /app/ros2_ws/src

RUN source /opt/ros/humble/setup.bash && \
    rosdep update && \
    rosdep install --from-paths /app/ros2_ws/src --ignore-src -r -y

RUN source /opt/ros/humble/setup.bash && \
    cd /app/ros2_ws && \
    colcon build

COPY scripts/run_simulation.sh /app/run_simulation.sh
COPY scripts/test.py /app/test.py
COPY worlds /app/worlds

# Pre-cache Fuel models during image build so they don't download at runtime
RUN Xvfb :99 -screen 0 1280x1024x24 -ac -noreset & \
    export DISPLAY=:99 && \
    export LIBGL_ALWAYS_SOFTWARE=1 && \
    ign gazebo /app/worlds/simple_world.sdf -r -s & \
    IGN_PID=$! && sleep 60 && kill $IGN_PID 2>/dev/null; true

RUN chmod +x /app/run_simulation.sh

CMD ["/bin/bash", "-c", \
     "source /opt/ros/humble/setup.bash && \
      source /app/ros2_ws/install/setup.bash && \
      /app/run_simulation.sh"]
