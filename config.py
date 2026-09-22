# devgagan
# Note if you are trying to deploy on vps then directly fill values in ("")

from os import getenv

# VPS --- FILL COOKIES 🍪 in """ ... """ 

INST_COOKIES = """
# wtite up here insta cookies
"""

YTUB_COOKIES = """
# write here yt cookies
"""

API_ID = int(getenv("API_ID", "29673529"))
API_HASH = getenv("API_HASH", "36905ab3e8672eb4542b3c46a6eb0c15")
BOT_TOKEN = getenv("BOT_TOKEN", "8646886186:AAFWHAOm7Nkp3pmxZtOGqStfCv0917qtY0k")
OWNER_ID = list(map(int, getenv("OWNER_ID", "8873984055").split()))
MONGO_DB = getenv("MONGO_DB", "mongodb+srv://filestorebot:filestorebot@filestorebot.4y0pzna.mongodb.net/?appName=filestorebot")
LOG_GROUP = getenv("LOG_GROUP", "-1004443016082")
CHANNEL_ID = int(getenv("CHANNEL_ID", "-1004443016082"))
FREEMIUM_LIMIT = int(getenv("FREEMIUM_LIMIT", "0"))
PREMIUM_LIMIT = int(getenv("PREMIUM_LIMIT", "50000"))
WEBSITE_URL = getenv("WEBSITE_URL", "nanolinks.in")
AD_API = getenv("AD_API", "7f3c70d412c1f3e04e6e248c0bc0c94199d3ac33")
STRING = getenv("STRING", None)
YT_COOKIES = getenv("YT_COOKIES", YTUB_COOKIES)
DEFAULT_SESSION = getenv("DEFAUL_SESSION", None)  # added old method of invite link joining
INSTA_COOKIES = getenv("INSTA_COOKIES", INST_COOKIES)
