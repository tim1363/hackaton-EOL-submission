# EOL / RoboHack 2.0 / T1

Контейнер участника для T1. Ubuntu 22.04, ROS 2 Humble, CycloneDDS, `linux/amd64`.

## Сборка и проверка

Нужны Docker Engine с Buildx и Python 3 на машине сборки.

```bash
docker buildx build --platform linux/amd64 --load -t eol-t1:local .
python3 verify_t1.py eol-t1:local
```

Проверка запускает `/entrypoint.sh ping` без сети и GPU, проверяет непривилегированный UID и ждёт один JSON за 10 секунд. При сборке нужен интернет.

## Поддержка заданий

Эта версия предназначена только для T1. Контейнер не заявляет незавершённые T2–T5.

```json
{"protocol_version":"1.0","supported_tasks":[],"self_trained_rl":false,"preferred_speed_mps":null}
```
