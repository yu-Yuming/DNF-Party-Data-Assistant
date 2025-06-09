import csv
from random import random
import time
from urllib import parse
from dotenv import load_dotenv
import requests
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 프로그램 정보
version = "1.4.10"

# 캐릭터 데이터 파일
characterDataFileName = "characterData.csv"
serverId = {
    "안톤": "anton",
    "바칼": "bakal",
    "카인": "cain",
    "카시야스": "casillas",
    "디레지에": "diregie",
    "힐더": "hilder",
    "프레이": "prey",
    "시로코": "siroco",
}
buffer = ["眞 크루세이더", "眞 인챈트리스", "眞 뮤즈", "眞 패러메딕"]

# 캐릭터 데이터 추출 배열
characterData = []

with open(characterDataFileName, newline="") as csvfile:
    reader = csv.reader(csvfile)
    for data in reader:
        characterData.append(data)

# 최종 결과 배열
result = []

# 네오플 API 에서 캐릭터 키 정보 취득
load_dotenv()
API_KEY = os.getenv("API_KEY")

driver = webdriver.Chrome()

for data in characterData:
    server = data[0]
    characterName = data[1]

    API_URL = f"https://api.neople.co.kr/df/servers/{serverId[server]}/characters?characterName={parse.quote(characterName)}&apikey={API_KEY}"

    response = requests.get(API_URL)

    try:
        body = response.json()

        characterKey = body["rows"][0]["characterId"]
        jobName = body["rows"][0]["jobGrowName"]
        fame = body["rows"][0]["fame"]

        # Debug Script
        # print(
        #     f"서버: {server}, 캐릭터명: {characterName}, 캐릭터키: {characterKey}, 직업: {jobName}, 명성치: {fame}"
        # )

    except:
        print(
            "캐릭터 키를 받아오는 중 오류가 발생했습니다. 해당 캐릭터의 정보가 정확하지 않거나 서버 연결 상태가 불안정할 수 있습니다."
        )
        exit()

    DUNDAM_URL = (
        f"https://dundam.xyz/character?server={serverId[server]}&key={characterKey}"
    )

    driver.get(DUNDAM_URL)

    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "dval"))
    )
    time.sleep(3 + random())

    if jobName in buffer:
        try:
            buff = driver.find_elements(By.CLASS_NAME, "dval")[
                5 if jobName == "眞 인챈트리스" else 0
            ].text
            print()
            stat = str(int(float(buff.replace(",", "")) / 10e3))
        except:
            # 만약에 버프력 정보가 없으면 배틀크루로 간주
            damage = driver.find_elements(By.CLASS_NAME, "dval")[1].text
            stat = str(round(float(damage.replace(",", "")) / 10e7, 1))
    else:
        damage = driver.find_elements(By.CLASS_NAME, "dval")[1].text
        stat = str(round(float(damage.replace(",", "")) / 10e7, 1))

    driver.get("about:blank")

    result.append([server, characterName, jobName, fame, stat])

driver.quit()

# save result to csv
with open("result.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["서버", "캐릭터 이름", "직업", "명성", "데미지/버프력"])
    for row in result:
        writer.writerow(row)
