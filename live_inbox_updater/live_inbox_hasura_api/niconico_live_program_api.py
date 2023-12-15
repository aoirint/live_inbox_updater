from datetime import datetime
from logging import getLogger
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, TypeAdapter, ValidationError

logger = getLogger(__name__)


class NiconicoLiveProgramUpsertObject(BaseModel):
    remote_niconico_content_id: str
    niconico_user_id: str
    title: str
    status: str
    last_fetch_time: datetime
    start_time: datetime | None
    end_time: datetime | None


class NiconicoUser(BaseModel):
    id: str
    remote_niconico_user_id: str


class UpsertNiconicoLiveProgramsResponseInsertNiconicoLivePrograms(BaseModel):
    affected_rows: int


class UpsertNiconicoLiveProgramsResponseData(BaseModel):
    insert_niconico_live_programs: UpsertNiconicoLiveProgramsResponseInsertNiconicoLivePrograms


class UpsertNiconicoLiveProgramsResponseBody(BaseModel):
    data: UpsertNiconicoLiveProgramsResponseData


def upsert_niconico_live_programs(
    objects: list[NiconicoLiveProgramUpsertObject],
    hasura_url: str,
    hasura_token: str,
    useragent: str,
) -> UpsertNiconicoLiveProgramsResponseBody:
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
                objects,
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

    return response_body
