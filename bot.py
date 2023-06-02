import nonebot
from nonebot.adapters.telegram import Adapter as TelegramAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(TelegramAdapter)

nonebot.load_plugins("plugins")
nonebot.run()
