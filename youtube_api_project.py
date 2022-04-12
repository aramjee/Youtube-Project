# reference code to run youtube stats not used in main project

from googleapiclient.discovery import build
import pandas as pd
from IPython.display import JSON
import os

api_key = 'AIzaSyDWNS55Gyda-J_lFzXZlJc6WpaX7SDh5mc'

#api_key = os.environ.get('youtube_api_key')
#print(api_key)

channel_ids = ['UC29ju8bIPH5as8OGnQzwJyA',
# more channels here
]

api_service_name = "youtube"
api_version = "v3"

# Get credentials and create an API client
youtube = build(
api_service_name, api_version, developerKey=api_key) # replace credential with our developer key, also not authenticating any users

def get_channel_stats(youtube, channel_ids):

    all_data = [] #create empty list to store Channel data
    
    request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id=','.join(channel_ids) # concatenate channel IDs
    )
    response = request.execute() # server is getting back a response for client browser
    
    #loop through items content within the response 
    for item in response['items']:
        data = {'Channel Name': item['snippet']['title'],
               'Subscribers': item['statistics']['subscriberCount'],
               'Views': item['statistics']['viewCount'],
               'Total Videos': item['statistics']['videoCount'],
               'PlaylistId': item['contentDetails']['relatedPlaylists']['uploads']
               }
        
        all_data.append(data)
        
    return(pd.DataFrame(all_data))

channel_stats = get_channel_stats(youtube, channel_ids)
print(channel_stats)