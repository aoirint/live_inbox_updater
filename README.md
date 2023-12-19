# live_inbox_updater

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
sudo docker build -t docker.aoirint.com/aoirint/live_inbox_updater .
sudo docker run --rm -v "./cache/niconico_user_icons:/code/live_inbox_updater/cache/niconico_user_icons" --env-file .env docker.aoirint.com/aoirint/live_inbox_updater
```
