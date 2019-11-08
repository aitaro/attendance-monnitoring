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

def users_info(user_id):
    client = slack.WebClient(token=os.getenv('SLACK_TOKEN'))

    res = client.users_info(
        user=user_id
    )
    return [res['user']['profile']['display_name'], res['user']['profile']['image_72']]

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

        users_df.loc[user_id] = users_info(user_id) + [total_times]
        print(user_id)
        # import pdb; pdb.set_trace()     

    x = list(range(1, len(users_df.index) + 1))
    y = users_df.hours
    label_x = users_df.name

    # img_c = plt.imread('image/plant_cactus.png')
    # img_b = plt.imread('image/Pteranodon.png')
    imgs = map(lambda x: plt.imread(x), users_df.image)

    fig = plt.figure(figsize=(8, 2*len(users_df.index)))
    plt.barh(x, y, align="center", height=0.5)           # 中央寄せで棒グラフ作成

    for index, row in users_df.iterrows():
        ax = fig.add_axes([0,0,0.1,1])
        ax.axison = False
        ax.imshow(list(imgs)[0])
        ax.text(0,90,'chaya', fontsize=15)

        
    plt.show()

    # plt.title("test")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)


    client.files_upload(
        channels=channel_id,
        file=buf,
        title="Test upload"
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

