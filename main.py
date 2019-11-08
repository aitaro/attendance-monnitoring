from flask import jsonify
import requests
from datetime import timedelta
from datetime import datetime
import pandas as pd
import pandas as pd
import matplotlib as mpl
import re
mpl.use("agg")
import matplotlib.pyplot as plt
import io
import matplotlib.pyplot as plt
import slack
import numpy as np
from threading import Thread
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os
import urllib


def users_info(user_id):
    client = slack.WebClient(token=os.getenv('SLACK_TOKEN'))

    res = client.users_info(
        user=user_id
    )
    # print(res)
    name = res['user']['profile']['display_name'] or res['user']['profile']['real_name']
    return [name, res['user']['profile']['image_72']]

def backgroundworker(channel_id):

    client = slack.WebClient(token=os.getenv('SLACK_TOKEN'))

    res = client.channels_history(
        channel=channel_id
    )
    messages = res['messages']

    resent_messages = [s for s in messages if datetime.fromtimestamp(float(s['ts'])) > datetime.now() - timedelta(weeks=1)]
    df = pd.DataFrame(resent_messages)
    users = df['user'].dropna().unique()

    cols = ['name', 'image', 'hours']
    users_df = pd.DataFrame(index=[], columns=cols)

    for user_id in users:
        texts = df[df.user == user_id].text
        texts_str = ','.join(texts)
        times = re.findall('\d+\.?\d*\s?[hH]', texts_str)
        total_times = 0
        for time in times:
            total_times += float(time[:-1])
        if total_times == 0: continue

        users_df.loc[user_id] = users_info(user_id) + [total_times]
        print(user_id)
        print(users_info(user_id)[0])
        print(users_info(user_id)[1])
        # import pdb; pdb.set_trace()     

    # users_df.loc['123456'] = ['aitaro.chaya', 'https://avatars.slack-edge.com/2018-07-02/390580434608_8bde4a6e0c9a2c554f29_72.png', 2]
    users_df = users_df.sort_values('hours')
    x = list(range(1, len(users_df.index) + 1))
    y = users_df.hours

    fig = plt.figure(figsize=(8, 2*len(users_df.index)))
    plt.barh(x, y, align="center", height=0.5)           # 中央寄せで棒グラフ作成
    plt.yticks([]) 

    print(users_df)

    counter = 0
    for index, row in users_df.iterrows():
        print(index)
        ax = fig.add_axes([0 , 0.8 / len(users_df.index) * counter + 0.1, 0.1, 0.8 / len(users_df.index)])
        ax.axison = False
        # create a file-like object from the url
        f = urllib.request.urlopen(row.image)

        ax.imshow(plt.imread(f, 0))
        ax.text(0,90,row['name'], fontsize=15)
        counter += 1

    plt.show()

    # plt.title("test")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)


    client = slack.WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    client.files_upload(
        channels=channel_id,
        file=buf,
        initial_comment="直近一週間の勤怠",
        title="Attendance summary"
    )

def main(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    thr = Thread(target=backgroundworker, args=[request.form['channel_id']])
    thr.start()

    return ""

