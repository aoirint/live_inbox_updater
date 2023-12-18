from logging import getLogger
from typing import Iterable
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

from .base import NiconicoLiveProgramManager, NiconicoLiveProgramUpsertObject

logger = getLogger(__name__)


class UpsertNiconicoLiveProgramsResponseInsertNiconicoLivePrograms(BaseModel):
    affected_rows: int


class UpsertNiconicoLiveProgramsResponseData(BaseModel):
    insert_niconico_live_programs: UpsertNiconicoLiveProgramsResponseInsertNiconicoLivePrograms


class UpsertNiconicoLiveProgramsResponseBody(BaseModel):
    data: UpsertNiconicoLiveProgramsResponseData


class NiconicoLiveProgramHasuraManager(NiconicoLiveProgramManager):
    def __init__(
        self,
        hasura_url: str,
        hasura_token: str,
        useragent: str,
    ):
        self.hasura_url = hasura_url
        self.hasura_token = hasura_token
        self.useragent = useragent

    def upsert_all(
        self,
        upsert_objects: Iterable[NiconicoLiveProgramUpsertObject],
    ) -> None:
        hasura_url = self.hasura_url
        hasura_token = self.hasura_token
        useragent = self.useragent

        hasura_api_url = urljoin(hasura_url, "v1/graphql")

        payload = {
            "query": """
mutation UpsertNiconicoLivePrograms(
    $niconico_live_program_upsert_objects: [niconico_live_programs_insert_input!]!
) {
    insert_niconico_live_programs(
        objects: $niconico_live_program_upsert_objects,
        on_conflict: {
            constraint: niconico_live_programs_remote_niconico_content_id_key,
            update_columns: [
                niconico_user_id
                title
                status
                last_fetch_time
                start_time
                end_time
            ]
        }
    ) {
        affected_rows
    }
}
""",
            "variables": {
                "niconico_live_program_upsert_objects": TypeAdapter(
                    list[NiconicoLiveProgramUpsertObject]
                ).dump_python(
                    list(upsert_objects),
                    mode="json",
                ),
            },
        }

        res = httpx.post(
            url=hasura_api_url,
            headers={
                "Authorization": f"Bearer {hasura_token}",
                "User-Agent": useragent,
            },
            json=payload,
        )
        res.raise_for_status()

        response_body_json = res.json()
        try:
            response_body = UpsertNiconicoLiveProgramsResponseBody.model_validate(
                response_body_json
            )
        except ValidationError:
            logger.error(response_body_json)
            raise

        affected_rows = response_body.data.insert_niconico_live_programs.affected_rows
        logger.info(f"Upserted {affected_rows} niconico live programs")
