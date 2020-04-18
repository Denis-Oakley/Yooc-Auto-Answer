# -*- coding: UTF-8 -*-
import atexit
import yaml
import re
import time
from random import random
from threading import Thread

import requests

import answer
import config


def repeatExam(configN):
    examsUrl = configN.examsUrl
    session = requests.Session()
    session.cookies.update(configN.cookies)
    session.headers.update(answer.headers)
    while True:
        if config.questionBanksAmount != 0 and len(questionBanks['collected']) >= config.questionBanksAmount:
            print('题库收集完毕')
            break
        detailUrl = answer.getDetailUrl(examsUrl, session)
        examHtml = session.get(detailUrl).text
        questionIds = re.findall(r'<div class="question-board" id="question-([0-9]+?)">', examHtml)
        time.sleep(5 + random() * 5)  # 睡眠 [5, 10]s
        answers = [{questionId: {'1': '0'}} for questionId in questionIds]
        answer.submitAnswer(session, detailUrl, answers)
        time.sleep(2 + random() * 3)  # 睡眠 [2, 3]s

        examHtml = session.get(detailUrl).text
        examHtml = examHtml.replace('\n', '')
        for question in re.findall(r'question-board" id="question-([0-9]+?)">(.+?)</div>', examHtml):
            questionId = question[0]
            questionContent = question[1]
            try:
                answerN = re.search(r'<p>正确答案：(.+?)</p>', questionContent).group(1)
            except AttributeError:
                print(examHtml)
                return
            if '<span class="ans"' in questionContent:
                # 填空题
                questionBanks['collected'][questionId] = [answerN]
            else:
                answerN = answerN.replace('、', '')
                order = re.findall('data-question-value="([0-9])"', questionContent)
                #                                #  ord('A') = 65
                questionBanks['collected'][questionId] = [order[ord(i) - 65] for i in answerN]
        time.sleep(5 + random() * 5)  # 睡眠 [5, 10]s


def saveConfig():
    with open('Question-Banks.yaml', 'w', encoding='UTF-8') as fileN:
        yaml.safe_dump(questionBanks, fileN, indent=4, allow_unicode=True)


with open('Question-Banks.yaml', 'r', encoding='UTF-8') as file:
    questionBanks = yaml.safe_load(file)

for account in config.accounts:
    Thread(target=repeatExam, args=(account,)).start()

atexit.register(saveConfig)