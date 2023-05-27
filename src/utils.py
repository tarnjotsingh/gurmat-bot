import logging
import discord
import string

logger = logging.getLogger("utils")
logger.setLevel(logging.INFO)

BOT_ID = 745385175856316556
DEFAULT_COLOUR = 0xffa900
ERROR_COLOUR = 0xff0000

# Can extend this so that it's not just the keywords but there are actual stats being recorded against each word
# being used so that we can retrieve statistics on their usages.
vaheguru_key_words = [
    'ਵਾਹਿਗੁਰੂ', 'vaheguru', 'vaheguroo', 'waheguru', 'waheguroo', 'guru', 'jesus', 'christ', 'god',
    'jai sri raam', 'raam', 'ram', 'allah', 'omg', 'rab', 'rabb', 'khuda', 'khudha', 'akaal', 'akal',
    'hari', 'har', 'gopal', 'gobind', 'paramatma', 'pati', 'satgur', 'udharan', 'parmeshwar', 'parmeswar',
    'gorak', 'gopal', 'kaal', 'akaal', 'akal', 'purkh', 'nanak', 'arjan', 'data', 'daataa', 'guru', 'parvadigar',
    'ek', 'oankar', 'hari', 'har', 'narayan'
]


def user_usage_log(ctx: discord.ApplicationContext) -> str:
    # Use discords context object to build the string
    return f"{ctx.author} used the {ctx.command} command in the {ctx.channel} channel"


# TODO: Lets change this so that a single vaheguru command returns a random value from the list instead
def vaheguru_check(message: str) -> bool:
    """Check if one of the key words exist in the provided message string"""
    # I want to linearly scan through the entire sentence and see if any of the words exist in the vaheguru_list
    msg = message.translate(str.maketrans('', '', string.punctuation)).split(" ")
    return any(w in vaheguru_key_words for w in msg)
