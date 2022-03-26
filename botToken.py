import os

def GetBotToken():
    return os.environ.get("BOT_TOKEN")
    #return '${{ secrets.BOT_TOKEN }}'