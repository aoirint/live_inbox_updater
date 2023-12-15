import time

import jwt


def main() -> None:
    secret_key = input("HS256 secret key: ")

    iat = int(time.time())
    exp = 2524608000  # 2050-01-01T00:00:00+00:00

    payload = {
        "sub": "bb22706e-0ad4-4dae-8ac8-ac8b75b63048",
        "iat": iat,
        "exp": exp,
        "x-hasura-default-role": "live_inbox_updater",
        "x-hasura-allowed-roles": ["live_inbox_updater"],
        "x-hasura-user-id": "bb22706e-0ad4-4dae-8ac8-ac8b75b63048",
    }

    print(
        jwt.encode(
            payload=payload,
            key=secret_key,
            algorithm="HS256",
        ),
    )


if __name__ == "__main__":
    main()
