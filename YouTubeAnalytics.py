import requests
from constants import YT_API_KEY
from pprint import pprint
from kafka import KafkaProducer
import json

if __name__ == "__main__":
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    response = requests.get("https://www.googleapis.com/youtube/v3/videos", 
                            {
                                'key': YT_API_KEY,
                                'id': "8FZZivIfJVo",
                                'part': 'snippet,statistics,status'
                            })

    response = json.loads(response.text)['items']
    for video in response:
        video_res = {
            'title': video['snippet']['title'],
            'likes': int(video['statistics'].get('likeCount', 0)),
            'comments': int(video['statistics'].get('commentCount', 0)),
            'views': int(video['statistics'].get('viewCount', 0)),
            'favorites': int(video['statistics'].get('favoriteCount', 0)),
            'thumbnail': video['snippet']['thumbnails']['default']['url']
        }


        print(pprint(video_res))

        producer.send('youtube_videos', json.dumps(video_res).encode('utf-8'))
        producer.flush()
        