from asyncio.windows_events import NULL
import requests
import uuid
import hmac
import math 

from discord_webhook import DiscordWebhook, DiscordEmbed
from hashlib import sha256
from datetime import datetime
from time import mktime
from time import time, sleep

def checkKey(dict, key):
    if key in dict.keys():
        return True
    else:
        return False
        
def get_epoch_ms_from_now():
        now = datetime.now()
        now_ec_since_epoch = mktime(now.timetuple()) + now.microsecond / 1000000.0
        return int(now_ec_since_epoch * 1000)

#---------------------------------------------------------------------------------------------------------------------#
# Nicehash Api Request
# https://www.nicehash.com/my/settings/keys

key = "key"
secret = "secret"
org_id = "organization id"
webhook_url = "url

is_offline = True
while True:
    sleep(60 - time() % 60)
    
    xtime  = str(get_epoch_ms_from_now())
    xnonce = str(uuid.uuid4())

    message  = bytearray(key, "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray(xtime, "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray(xnonce, "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray(org_id, "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray("GET", "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray("/main/api/v2/mining/rigs2", "utf-8")
    message += bytearray("\x00", "utf-8")
    message += bytearray("", "utf-8")
            
    headers = {
        "X-Time": xtime,
        "X-Nonce": xnonce,
        "X-Auth": key + ":" + hmac.new(bytearray(secret, "utf-8"), message, sha256).hexdigest(),
        "Content-Type": "application/json",
        "X-Organization-Id": org_id
    }

    r = requests.get(url = "https://api2.nicehash.com/main/api/v2/mining/rigs2", headers = headers)

    # Rig Data
    data = r.json()

    rigs_num = data["totalRigs"]
    devices = data["totalDevices"] 
    device_statuses = data["devicesStatuses"]
    active = str(device_statuses["MINING"]) if checkKey(device_statuses, "MINING") else "0"

    if is_offline:
        
        actual = data["totalProfitability"] 
        local  = data["totalProfitabilityLocal"]
        unpaid = data["unpaidAmount"] 

        rigs = data["miningRigs"]

        #---------------------------------------------------------------------------------------------------------------------#
        # Creating Webhook
        webhook = DiscordWebhook(url=webhook_url, 
                                username="Miner Manager")
        #---------------------------------------------------------------------------------------------------------------------#
        # Create First Embed
        main_info = DiscordEmbed(title="All Information", color="ffec00" if active == str(devices) else "ff1000")
        main_info.set_author(
            name="Nicehash Webhook",
            url="https://github.com/bssruhio/nicehash_discord_webhook",
            icon_url=" ",
        )
        main_info.set_thumbnail(url=" ")
        main_info.set_footer(text="made by not.bass#3945")
        main_info.set_timestamp()

        # Row 1
        main_info.add_embed_field(name="Rigs", value=str(rigs_num), inline=True)
        main_info.add_embed_field(name="Devices", value=str(devices), inline=True)
        main_info.add_embed_field(name="Active", value=active, inline=True)

        # Row 2
        main_info.add_embed_field(name="Local Profit", value=str(actual)[0:10] + " BTC", inline=True)
        main_info.add_embed_field(name="Actual Profit", value=str(local)[0:10] + " BTC", inline=True)
        main_info.add_embed_field(name="Unpaid", value=str(unpaid)[0:10] + " BTC", inline=True)

        # Add Main Info
        webhook.add_embed(main_info)

        #---------------------------------------------------------------------------------------------------------------------#
        # Create Embed for each rig
        if len(rigs) == 0:
            rig_info = DiscordEmbed(title="No Rigs were found", color="ffec00")
        else:
            for rig in rigs:
                rig_info = DiscordEmbed(title=rig["name"], color="ff1000" if (rig["minerStatus"] == "OFFLINE" or rig["minerStatus"] == "STOPPED") else "37ff21")
                rig_info.add_embed_field(name="Status", value=rig["minerStatus"], inline=True)
                rig_info.add_embed_field(name="Local",  value=str(rig["localProfitability"])[0:10] + " BTC", inline=True)
                rig_info.add_embed_field(name="Actual", value=str(rig["profitability"])[0:10] + " BTC", inline=True)
                
                rig_devices = rig["devices"]
                for dev in rig_devices:
                    speeds = dev["speeds"]
                    speed_info = ""
                    for speed in speeds:
                        speed_info += speed["title"] + " " + str(math.ceil(float(speed["speed"]))) + " " + speed["displaySuffix"] + "s\n"
                    rig_info.add_embed_field(name=dev["name"], value=dev["status"]["enumName"] + "\n" + speed_info, inline=True)
                    
                webhook.add_embed(rig_info)


        response = webhook.execute()
        print(response)
        
    is_offline = active != str(devices)
