FROM ros:humble-ros-core-jammy

RUN apt-get update \
    && apt-get install -y --no-install-recommends ros-humble-rmw-cyclonedds-cpp \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --uid 10001 --user-group --create-home participant

ENV RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
    HOME=/home/participant

COPY --chmod=0755 entrypoint.sh /entrypoint.sh

USER 10001:10001
ENTRYPOINT ["/entrypoint.sh"]
CMD ["ping"]
