from random import randint
from datetime import datetime

def get_random_value_str() -> str:
   time = int(round(datetime.now().timestamp()))
   return f"{time}_{randint(0,10000)}"


