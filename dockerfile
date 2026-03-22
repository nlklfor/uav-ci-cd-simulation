FROM ros:humble

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip \
    git \
    && apt-get clean

WORKDIR /app

COPY . .

CMD ["bash"]