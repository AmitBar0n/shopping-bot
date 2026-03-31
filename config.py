import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
AMIT_ID: int = int(os.environ["AMIT_ID"])
PARTNER_ID: int = int(os.environ["PARTNER_ID"])
AMIT_NAME: str = os.environ.get("AMIT_NAME", "עמית")
PARTNER_NAME: str = os.environ.get("PARTNER_NAME", "ירדן")

AUTHORIZED_IDS: set[int] = {AMIT_ID, PARTNER_ID}

NAMES: dict[int, str] = {
    AMIT_ID: AMIT_NAME,
    PARTNER_ID: PARTNER_NAME,
}
