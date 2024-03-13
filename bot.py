#-*- coding: utf-8 -*-

#카샤의 의해 뿌려집니다.

import os.path
import asyncio
import discord
import os
import shutil
import random
from random import randint
import time
import datetime
from bs4 import BeautifulSoup
from discord_webhook import DiscordWebhook, DiscordEmbed
import requests
import urllib
import json
import sqlite3
import sys
import schedule
import re
from operator import itemgetter
import ssl, typing
from pytz import timezone, utc
from discord import app_commands, Interaction, Object, ButtonStyle
from discord.ui import Button, View, Modal, TextInput
import uuid
import math
import toss
import settings
from blockcypher import simple_spend

token = settings.token
bot = discord.Client(intents=discord.Intents.all())
tree = app_commands.CommandTree(bot)
botadmin = settings.botadmin
tossid = settings.tossid
api_key = settings.api_key
private_key = settings.private_key
private_keywif = settings.private_keywif
myaddress = settings.myaddress
buylog_webhook = settings.buylog_webhook

async def get_address_details():
    base_url = "https://api.blockcypher.com/v1"
    endpoint = f"{base_url}/ltc/main/addrs/{myaddress}"

    try:
        # Sending a GET request to the BlockCypher API
        response = requests.get(endpoint, params={"token": api_key})
        data = response.json()

        # Extracting relevant details from the response
        balance = data["balance"]
        total_received = data["total_received"]
        total_sent = data["total_sent"]
        balance_formatted = float(balance) / 100000000
        # Returning the address details
        #return balance, total_received, total_sent
        return balance_formatted

    except Exception as e:
        # Error handling if the request fails
        print("Error:", e)
        return None
    
async def getltcusdt():
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {
        "symbol": "LTCUSDT"
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        last_price = float(data["price"])
        return last_price

    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

async def get_ltc_price_krw():
    ltc_price = await getltcusdt()
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        ltc_krw_price = float(ltc_price)*int(float(data[0]['basePrice']))
        #print(f"LTC Price in KRW: {ltc_krw_price}")
        return ltc_krw_price
    else:
        #print('Failed to fetch LTC/KRW price')
        return "ERR"

async def get_ltc_price_usd():
    ltc_price = await getltcusdt()
    ltc_price = float(ltc_price)
    return ltc_price

async def usdtowon(usd):
    url = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        result = float(usd)*int(float(data[0]['basePrice']))
        #print(f"LTC Price in KRW: {ltc_krw_price}")
        return result
    else:
        #print('Failed to fetch LTC/KRW price')
        return "ERR"


async def litefee_get(percent):
    price = await get_ltc_price_krw() 
    price = int(price)
    inc = 0.003*price
    price = inc+price 
    price = round(price)
    price = price + (price * 0.05)
    price = round(price)
    return price

async def fee_get(won):
   try: 
    won = int(won)
    krkr = await get_ltc_price_krw()
    krkr = int(krkr)
    amount = won/krkr
    amount = amount-0.003
    amount = amount - (amount * 0.05)
    price = amount*krkr
    price = round(price)
    return price
   except Exception as e:
      print(e)
      return None

async def fee_get2(won):
   try: 
    won = int(won)
    krkr = await get_ltc_price_krw()
    krkr = int(krkr)
    amount = won/krkr
    amount = amount-0.003
    amount = amount - (amount * 0.05)
    amount = round(amount,5)   
    return amount
   except Exception as e:
      print(e)
      return None

async def fee_get3(coin):
   try: 
    coin = float(coin)
    amount = coin+0.003
    amount = amount + (amount * 0.05)
    amount = round(amount,5)   
    return amount
   except Exception as e:
      print(e)
      return None

async def fee_get11(usd):
   try: 
    usd = float(usd)
    krkr = await get_ltc_price_usd()
    krkr = int(krkr)
    amount = usd/krkr
    amount = amount+0.003
    amount = round(amount,5)   
    return amount
   except Exception as e:
      print(e)
      return None

async def fee_get12(coin):
   try: 
    amount = float(coin)
    amount = amount + (amount * 0.05)
    amount = round(amount,5)   
    ozzz = await get_ltc_price_krw()
    wonwon = int(ozzz)*amount
    return wonwon
   except Exception as e:
      print(e)
      return None

async def fee_get13(usd):
   try: 
    usd = float(usd)
    krkr = await get_ltc_price_usd()
    krkr = int(krkr)
    amount = usd/krkr
    amount = amount-0.003
    amount = amount - (amount * 0.05)
    amount = round(amount,5)   
    return amount
   except Exception as e:
      print(e)
      return None

async def get_coin_balance():
    price = await get_ltc_price_krw()
    balance = await get_address_details()
    response = float(balance)*float(price)
    response = round(response)
    return response

async def withdraw_ltc(to_address, amount):
    base_url = "https://api.blockcypher.com/v1"
    endpoint = f"{base_url}/ltc/main/txs/push"
    from_address = myaddress
    amount = int(amount*100000000)
    try:
        tx_hash = simple_spend(from_privkey=private_key, to_address=to_address, to_satoshis=amount, coin_symbol='ltc',api_key=api_key)
        return tx_hash

    except Exception as e:
        # Error handling if the request fails
        print("Error:", e)
        return None

def start_db():
    con = sqlite3.connect("db.db")
    cur = con.cursor()
    return con, cur

def user_db():
    con = sqlite3.connect("user.db")
    cur = con.cursor()
    return con, cur

class Modal1(Modal, title="송금"):
    f1 = TextInput(label="지갑주소 (라이트코인)",placeholder="예) ltc1q29hm7wn047c8vgqeth8d97nn7k5xrtgrek9dzg", style=discord.TextStyle.short)
    f2 = TextInput(label="송금 금액 (원화)",placeholder="숫자로만 입력하세요", style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
     try: 
       await interaction.response.defer()
       address = self.children[0].value
       orig = self.children[1].value
       amount = await fee_get2(orig)
       wonwon = orig
       hyun = await get_coin_balance()
       if(amount > hyun):
          await interaction.followup.send("재고가 부족합니다.\n남은 재고:"+str(hyun), ephemeral=True)  
          return
       if(amount < 0.002):
          await interaction.followup.send("최소 주문 금액 0.002", ephemeral=True)  
          return
       con,cur = user_db()
       cur.execute("SELECT * FROM users WHERE id == ? AND guild == ?;",(str(interaction.user.id),str(interaction.guild.id),))
       users = cur.fetchone()
       con.close()
       try:
          guild = users[0]
          uid = users[1]
          money = users[2]
       except:
        await interaction.followup.send("잔액이 부족합니다. 최대 송금 가능 금액: "+str(wonwon), ephemeral=True)  
        return
       if(int(wonwon) > int(money)):
          await interaction.followup.send("잔액이 부족합니다. 최대 송금 가능 금액: "+str(wonwon), ephemeral=True)  
          return
       totl2 = int(money)-int(wonwon)
       con,cur = user_db()
       cur.execute("UPDATE users SET money = ? WHERE id == ? AND guild == ?;", (str(totl2), str(interaction.user.id), str(interaction.guild.id)))
       con.commit()
       con.close()  
       msg = await withdraw_ltc(address, amount)
       if(str(msg) == 'None'):
          await interaction.followup.send('인출중 오류가 발생하였습니다. 관리자에게 문의하세요.', ephemeral=True)  
          return 
       await interaction.user.send("TXID: "+msg)
       try:
        webhook = DiscordWebhook(url=buylog_webhook, username="Coin")
        embed = DiscordEmbed(description="<@"+str(interaction.user.id)+">님 라이트코인 "+str(wonwon)+"원 구매 감사합니다.", color=0xffffff)
        webhook.add_embed(embed)
        reponse = webhook.execute()
       except:
        pass   
       try:
        await interaction.followup.send("전송이 시작되었습니다.", ephemeral=True)  
       except:
          print(msg)
          await interaction.followup.send("오류.", ephemeral=True)  
          webhook = DiscordWebhook(url=buylog_webhook, username="Coin")
          embed = DiscordEmbed(description="<@"+str(interaction.user.id)+">님 라이트코인 구매도중 운지해버림!!", color=0xffffff)
          webhook.add_embed(embed)
          reponse = webhook.execute()
     except Exception as e:
         print(e)    
         await interaction.followup.send("오류 (2).", ephemeral=True)  
         webhook = DiscordWebhook(url=buylog_webhook, username="Coin")
         embed = DiscordEmbed(description="<@"+str(interaction.user.id)+">님 라이트코인 구매도중 운지해버림!!", color=0xffffff)
         webhook.add_embed(embed)
         reponse = webhook.execute()

class Modal12(Modal, title="충전"):
    def __init__(self):
        super().__init__(timeout=None)
    f1 = TextInput(label="입금자명을 입력해 주세요.",placeholder="최대 10자, 특수문자는 쓸 수 없어요.", style=discord.TextStyle.short)
    f2 = TextInput(label="입금액을 입력해 주세요.",placeholder="숫자만 입력해 주세요.", style=discord.TextStyle.short)
    async def on_submit(self, interaction: discord.Interaction):
      await interaction.response.defer()
      입금자명 = self.children[0].value
      충전금액 = self.children[1].value
      button001 = discord.ui.Button(style=discord.ButtonStyle.primary, label="✅ 입금 완료", custom_id="finished")

      view1011 = discord.ui.View()
      view1011.add_item(button001)
      embed = discord.Embed(description=f"**2분 후에 만료됩니다.**", color=discord.Color.orange())
      embed.add_field(name="📝 충전", value=f"**`입금주소   →` https://toss.me/{tossid}\n`입금자명   →` `{입금자명}`\n`입금액   →` `{format(int(충전금액), ',')}원`**", inline=True)
      oldtime = datetime.datetime.now()
      await interaction.followup.send(embed=embed, view=view1011, ephemeral=True) 
      async def button001_callback(interaction: Interaction):
        newtime = datetime.datetime.now()
        df = newtime - oldtime
        dfs = int(df.seconds) #초
        if(dfs > 120):
           await interaction.response.send_message("2분이 초과되었습니다. 다시 충전 신청을 하셔야합니다.", ephemeral=True)
           return
        try:
            await interaction.response.defer()
            response = toss.check(입금자명, int(충전금액))
            print(response)
            msg = response['msg']
            con,cur = user_db()
            cur.execute("SELECT * FROM users WHERE guild == ? AND id == ? ;",(str(interaction.guild.id),str(interaction.user.id),))
            wzz = cur.fetchone()
            con.close()
            if msg == '입금 미확인':
               #await interaction.user.send(embed=discord.Embed(title="충전 실패 ❌", description=f"**다음 사유로 충전이 거부되었습니다.\n사유 : `입금 미확인`**",color=0x2f3136))
               await interaction.followup.send(embed=discord.Embed(title="충전 실패 ❌", description=f"**다음 사유로 충전이 거부되었습니다.\n사유 : `입금 미확인`**",color=0x2f3136), ephemeral=True) 
               return
            if response['result'] == True:
               try:
                  money = wzz[2]
                  total = wzz[3]
                  tl = int(total)+int(충전금액)
                  con,cur = user_db()
                  cur.execute("UPDATE users SET money = ? WHERE id == ? AND guild == ?;", (str(충전금액), str(interaction.user.id), str(interaction.guild.id)))
                  con.commit()
                  con.close()   
                  con,cur = user_db()
                  cur.execute("UPDATE users SET total = ? WHERE id == ? AND guild == ?;", (str(tl), str(interaction.user.id), str(interaction.guild.id)))
                  con.commit()
                  con.close()  
                  await interaction.user.send(embed=discord.Embed(title="Order Accepted", description=f"{money}원 충전 자동 승인 되었습니다.\n주문번호: {response['id']}", color=0x00ff00))
               except:
                  con,cur = user_db()
                  cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", (str(interaction.guild.id), str(interaction.user.id), str(충전금액), "0"))
                  con.commit()
                  con.close()
               return
            elif msg == 'USER_IP_TEMPORARILY_BLOCKED 서비스를 일시적으로 이용할 수 없습니다.':
               #await interaction.user.send(embed=discord.Embed(title="충전 실패 ❌", description=f"**다음 사유로 충전이 거부되었습니다.\n사유 : `일시적인 서비스 장애가 발생하였습니다.`\n\n관리자에게 문의하세요.**",color=0x2f3136))  
               await interaction.followup.send(embed=discord.Embed(title="충전 실패 ❌", description=f"**다음 사유로 충전이 거부되었습니다.\n사유 : `일시적인 서비스 장애가 발생하였습니다.`\n\n관리자에게 문의하세요.**",color=0x2f3136))  
               return
        except:
           #await interaction.user.send(embed=discord.Embed(title="충전 실패 ❌", description=f"**오류! 관리자에게 문의하세요.**",color=0x2f3136))  
           await interaction.followup.send(embed=discord.Embed(title="충전 실패 ❌", description=f"**오류! 관리자에게 문의하세요.**",color=0x2f3136))  
           return       
      button001.callback = button001_callback

@tree.command(name = "최대송금", description = "최대송금액.")
async def cal(interaction: discord.Interaction):
     await interaction.response.defer()
     con,cur = user_db()
     cur.execute("SELECT * FROM users WHERE id == ? AND guild == ?;",(str(interaction.user.id),str(interaction.guild.id),))
     users = cur.fetchone()
     con.close()
     try:
          guild = users[0]
          uid = users[1]
          money = users[2]
     except:
        money = '0'  
     money = int(money)   
     if(money != 0):
      try:
       nomuc = await fee_get(money)
      except Exception as e:
       print(e)
       nomuc = '0' 
     else:
        nomuc = '0'   
     wonwon = format(int(nomuc), ',')   
     embed = discord.Embed(
        title=f":coin: 코인 가격 조회",
        description=f"최대 구매 가능 금액은 약 {str(wonwon)}원입니다.",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name = "코인원", description = "가격계산.")
async def cal(interaction: discord.Interaction, 개수: float):
     await interaction.response.defer()
     price = await litefee_get(5)
     total_value = int(price) * 개수
     wonwon = format(int(total_value), ',')
     embed = discord.Embed(
        title=f":coin: 코인 가격 조회",
        description=f"{str(개수)} 개의 라이트코인은 약 {str(wonwon)}원입니다. (수수료 포함)",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name = "원코인", description = "가격계산.")
async def cal(interaction: discord.Interaction, 원: int):
     await interaction.response.defer()
     amount = await fee_get2(원)
     wonwon = format(int(원), ',')
     embed = discord.Embed(
        title=f":coin: 코인 가격 조회",
        description=f"{str(wonwon)}원으로는 약 {str(amount)}개의 라이트코인을 전송 가능합니다. (수수료 포함)",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name = "달러코인", description = "가격계산.")
async def cal(interaction: discord.Interaction, 달러: float):
     await interaction.response.defer()
     amount = await fee_get13(달러)
     embed = discord.Embed(
        title=f":coin: 코인 가격 조회",
        description=f"{str(달러)}달러로는 약 {str(amount)}개의 라이트코인을 전송 가능합니다. (수수료 포함)",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name = "달러원", description = "가격계산.")
async def cal(interaction: discord.Interaction, 달러: float):
     await interaction.response.defer()
     wonwon = await usdtowon(달러)
     wonwon = int(wonwon)
     inc = int(wonwon)*0.05
     wonwon = wonwon+inc+500
     wonwon = int(wonwon)
     wonwon = round(wonwon)
     wonwon = format(int(wonwon), ',')
     embed = discord.Embed(
        title=f":coin: 코인 가격 조회",
        description=f"{str(달러)}달러는 약 {str(wonwon)}원 입니다. (수수료 포함)",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed, ephemeral=True)

@tree.command(name = "유저충전", description = "관리자")
async def cal12(interaction: discord.Interaction, 충전금액: int, 유저아이디: str):
  if interaction.user.id in botadmin: 
   if interaction.user.guild_permissions.manage_messages:  
     await interaction.response.defer()
     con,cur = user_db()
     cur.execute("SELECT * FROM users WHERE guild == ? AND id == ? ;",(str(interaction.guild.id),str(유저아이디),))
     wzz = cur.fetchone()
     con.close()
     try:
        money = wzz[2]
        total = wzz[3]
        tl = int(total)+int(충전금액)
        con,cur = user_db()
        cur.execute("UPDATE users SET money = ? WHERE id == ? AND guild == ?;", (str(충전금액), str(유저아이디), str(interaction.guild.id)))
        con.commit()
        con.close()   
        con,cur = user_db()
        cur.execute("UPDATE users SET total = ? WHERE id == ? AND guild == ?;", (str(tl), str(유저아이디), str(interaction.guild.id)))
        con.commit()
        con.close()  
     except:
        con,cur = user_db()
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", (str(interaction.guild.id), str(유저아이디), str(충전금액), str(충전금액)))
        con.commit()
        con.close()   
     충전금액 = format(int(충전금액), ',')
     embed = discord.Embed(
        title=f"충전 완료",
        description=f"{str(충전금액)}원을 <@{str(유저아이디)}> 에게 충전하였습니다.",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed)

@tree.command(name = "유저정보", description = "관리자")
async def cal34(interaction: discord.Interaction, 유저아이디: str):
   if interaction.user.guild_permissions.manage_messages:  
     await interaction.response.defer()
     con,cur = user_db()
     cur.execute("SELECT * FROM users WHERE guild == ? AND id == ? ;",(str(interaction.guild.id),str(유저아이디),))
     wzz = cur.fetchone()
     con.close()
     try:
        money = wzz[2]
        total = wzz[3]
     except:
        await interaction.followup.send("존재하지 않는 유저입니다.", ephemeral=True)
        return 
     money = format(int(money), ',')
     total = format(int(total), ',')
     embed = discord.Embed(
        title=f"유저 정보",
        description=f"<@{str(유저아이디)}>님의 정보\n잔액: {money}\n총 충전액: {total}",
        color=discord.Color.blue()
    )
     await interaction.followup.send(embed=embed)


class buttonz(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="재고", custom_id="b1")
    async def press_me1(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer()
      balance = await get_coin_balance()
      balance = format(int(balance), ',')
      embed = discord.Embed(description=f"**코인 재고**", color=discord.Color.orange())
      embed.add_field(name="🪙 코인", value=f"**`라이트코인 (LTC)   →` `{balance}원`**", inline=True)
      await interaction.followup.send(embed=embed, ephemeral=True) 

    @discord.ui.button(label="충전", custom_id="b2")
    async def press_me2(self, interaction: discord.Interaction, button: discord.ui.Button):
         modal = Modal12()
         await interaction.response.send_modal(modal)
         await modal.wait()


    @discord.ui.button(label="내정보", custom_id="b3")
    async def press_me3(self, interaction: discord.Interaction, button: discord.ui.Button):
      await interaction.response.defer()
      con,cur = user_db()
      cur.execute("SELECT * FROM users WHERE guild == ? AND id == ? ;",(str(interaction.guild.id),str(interaction.user.id),))
      wzz = cur.fetchone()
      con.close()
      try:
         money = wzz[2]
         total = int(wzz[3])
         print(total)
         if total == 0:
            nomu = "비구매자"
            susuro = 5
         elif total < 300000:
            nomu = "구매자"
            susuro = 5
         elif total < 500000:
            nomu = "VIP"
            susuro = 5
         else:
            nomu = "VVIP"
            susuro = 5

         
           
      except:
        con,cur = user_db()
        cur.execute("INSERT INTO users VALUES(?, ?, ?, ?);", (str(interaction.guild.id), str(interaction.user.id), "0", "0"))
        con.commit()
        con.close()   
        money = '0'
        total = '0'
        nomu = "비구매자"
        susuro = 5
      money = format(int(money), ',')
      total = format(int(total), ',')
      embed = discord.Embed(description=f"**내 정보**", color=discord.Color.orange())
      user_avatar_url = interaction.user.display_avatar.url
      embed.set_thumbnail(url=user_avatar_url)
      embed.add_field(name="👤 계정", value=f"**`등급   →` `{nomu}`\n`수수료   →` `{susuro}%`**", inline=True)
      embed.add_field(name="💰 금액", value=f"**`잔여금액   →` `{money}원`\n`누적금액   →` `{total}원`**", inline=True)
      await interaction.followup.send(embed=embed, ephemeral=True) 

    @discord.ui.button(label="송금", custom_id="b4")
    async def press_me4(self, interaction: discord.Interaction, button: discord.ui.Button):
      modal = Modal1()
      await interaction.response.send_modal(modal)
      await modal.wait()   
@bot.event
async def on_ready():
    print("Sync 중입니다...")
    await tree.sync() #슬래시 사용시만
    con,cur = start_db()
    cur.execute("SELECT * FROM buk;")
    guilds = cur.fetchall()
    con.close()  
    guilds = list(set(guilds))
    for line in guilds:
        chid = line[0]
        msgid = line[1]
        guildid = line[2]
        ch = bot.get_channel(int(chid))
        if(str(ch) == 'None'):
            #등록됬던 채널이 존재하지 않는 경우
            #채널이 없는 경우 새로 설치하는 방법밖에 없음
            con,cur = start_db()
            cur.execute(f"DELETE FROM buk WHERE guild == ?;",(guildid,))
            con.commit()
            con.close()   
        try:
         msg = await ch.fetch_message(int(msgid))
         await msg.edit(view=buttonz())
        except:
            #등록됬던 메세지가 존재하지 않는 경우
            try:
             embed = discord.Embed(title="자동 대행 자판기", description="사용 방법\n``#1`` ``충전 버튼을 눌러 잔액을 충전합니다.``\n``#2`` ``송금 버튼을 눌러 송금을 진행합니다.``\n``#3`` ``송금조회 명령어로 송금 현황을 확인합니다.``\n\n현재 자동 충전은 토스아이디 송금만 지원합니다.\n계좌이체 충전은 티켓을 통해 문의해주세요.\n문제가 있는 경우 티켓으로 문의해주세요.",color=0xffffff)
             mg = await ch.send(embed=embed, view=buttonz())
             con,cur = start_db()
             cur.execute("UPDATE buk SET msg = ? WHERE guild == ?;", (str(mg.id), guildid))
             con.commit()
             con.close()   
            except:
             pass 
    print("Sync 완료됨.")        
    print(f'Bot is ready. Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
 if message.author == bot.user:
        return
 elif(message.content.startswith(".코인")):
  if message.author.id in botadmin:
   embed = discord.Embed(title="👍자동 대행 자판기", description="사용 방법\n``#1`` ``문의하기를 눌러 잔액을 충전합니다.``\n``#2`` ``송금 버튼을 눌러 송금을 진행합니다.``\n``#3`` ``송금조회 명령어로 송금 현황을 확인합니다.``\n\n현재 충전은 문상충전과 일반 계좌충전을 지원합니다.\n계좌이체 충전은 티켓을 통해 문의해주세요.\n문제가 있는 경우 티켓으로 문의해주세요.",color=0xdd8815)
   mg = await message.channel.send(embed=embed, view=buttonz())
   con,cur = start_db()
   cur.execute(f"DELETE FROM buk WHERE guild == ?;",(str(message.guild.id),))
   con.commit()
   con.close()   
   con,cur = start_db()
   cur.execute("INSERT INTO buk VALUES(?, ?, ?);", (str(message.channel.id), str(mg.id), str(message.guild.id)))
   con.commit()
   con.close()


bot.run(token)
