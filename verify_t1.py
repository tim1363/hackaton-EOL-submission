import argparse
import json
import subprocess
import sys
import time


PING_RESPONSE = {
    "protocol_version": "1.0",
    "supported_tasks": [],
    "self_trained_rl": False,
    "preferred_speed_mps": None,
}

CONTAINER_OPTIONS = ["run", "--rm", "--pull=never", "--network=none"]


def docker(*args, timeout=10):
    return subprocess.run(
        ["docker", *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=timeout,
    ).stdout


def verify_t1(image):
    platform = docker("image", "inspect", "--format", "{{.Os}}/{{.Architecture}}", image)
    if platform.strip() != "linux/amd64":
        raise ValueError(f"Expected linux/amd64, found {platform.strip()!r}")

    start = time.monotonic()
    response = docker(*CONTAINER_OPTIONS, "--entrypoint", "/entrypoint.sh", image, "ping")
    elapsed = time.monotonic() - start
    payload = json.loads(response)
    if payload != PING_RESPONSE or payload["self_trained_rl"] is not False:
        raise ValueError(f"Unexpected T1-only ping metadata: {response.strip()!r}")
    if elapsed > 10:
        raise ValueError(f"ping exceeded 10 seconds: {elapsed:.2f}s")

    docker(
        *CONTAINER_OPTIONS,
        "--entrypoint",
        "/bin/bash",
        image,
        "-ec",
        "test \"$(id -u)\" -ne 0; "
        ". /etc/os-release; test \"$ID:$VERSION_ID\" = 'ubuntu:22.04'; "
        ". /opt/ros/humble/setup.bash; test \"$ROS_DISTRO\" = humble; "
        "python3 -c 'from rclpy.utilities import get_rmw_implementation_identifier as rmw; "
        'assert rmw() == "rmw_cyclonedds_cpp"\'',
        timeout=30,
    )
    print(f"T1 smoke check passed: {platform.strip()}, offline non-root, ping {elapsed:.2f}s.")


def main():
    parser = argparse.ArgumentParser(description="Check the T1-only image in a local Docker Engine.")
    parser.add_argument("image", help="Local image tag or already-pulled image digest")
    args = parser.parse_args()
    try:
        verify_t1(args.image)
    except subprocess.CalledProcessError as error:
        print(f"T1 check failed: Docker exited with {error.returncode}.", file=sys.stderr)
        print((error.stderr or error.stdout or "").strip(), file=sys.stderr)
        return 1
    except FileNotFoundError:
        print("T1 check failed: docker was not found on PATH.", file=sys.stderr)
        return 1
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"T1 check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
