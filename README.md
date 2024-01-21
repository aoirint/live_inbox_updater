# live_inbox_updater

## Releases

- [GitHub Releases](https://github.com/aoirint/live_inbox_updater/releases) (source only)
- [GitHub Container Registry](https://github.com/aoirint/live_inbox_updater/pkgs/container/live_inbox_updater)
- [Docker Hub](https://hub.docker.com/r/aoirint/live_inbox_updater)

## Usage

### Native usage

```shell
poetry install

poetry run python -m live_inbox_updater update

poetry run python -m live_inbox_updater add_user --remote_niconico_user_ids 1000

poetry run python -m live_inbox_updater enable_user --remote_niconico_user_ids 1000

poetry run python -m live_inbox_updater disable_user --remote_niconico_user_ids 1000
```

### Docker usage

```shell
mkdir -p ./data
sudo chown "1000:1000" ./data

sudo docker build -t docker.aoirint.com/aoirint/live_inbox_updater .

sudo docker run --rm -v "./data:/code/live_inbox_updater/data" --env-file .env docker.aoirint.com/aoirint/live_inbox_updater

sudo docker run --rm -v "./data:/code/live_inbox_updater/data" --env-file .env docker.aoirint.com/aoirint/live_inbox_updater add_user --remote_niconico_user_ids 1000
```
