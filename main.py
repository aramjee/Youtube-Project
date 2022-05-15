from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from googleapiclient.discovery import build
import pandas as pd
from IPython.display import JSON
import os

app = Flask(__name__) # creates an instance of a flask application
app.secret_key = os.environ.get('app.secret_key')


@app.route("/", methods=['GET', 'POST']) # default domain can be /home or /anything
def home(): #inline HTML
    channel_stats_data = {'Channel Name': "",
                        'Subscribers': "",
                        'Views': "",
                        'Total Videos': "",
                        'Playlist ID': "",
                        }
                                                      
    channel_stats = pd.DataFrame(channel_stats_data, index=[0])
    print(channel_stats)
    
    all_video_info = {'channelTitle': "",
                        'title': "",
                        'viewCount': "",
                        'likeCount': "",
                        'commentCount': "",
                        }

    all_video_info = pd.DataFrame(all_video_info, index=[0])


    if request.method == 'POST':
        channel_id = request.form.get("channelID")
        api_key = os.environ.get('youtube_api_key')
        channel_ids = [channel_id,]

        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and creates an API client
        youtube = build(
        api_service_name, api_version, developerKey=api_key) # replace credential with our developer key, also not authenticating any users

        def get_video_ids(youtube, playlist_id):
            video_ids = []
            
            request = youtube.playlistItems().list(
                part="snippet, contentDetails",
                playlistId=playlist_id,
                maxResults = 50 # default call is 5 but we can get maximum of 50, even though we know this person has 911 videos so implement next page token
            )
            response = request.execute()

            for item in response['items']:
                video_ids.append(item['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
            while next_page_token is not None:# keep running the request until we reach the last page
                request = youtube.playlistItems().list(
                    part = "contentDetails",
                    playlistId=playlist_id,
                    maxResults = 50,
                    pageToken =next_page_token)
                response = request.execute()
                
                for item in response['items']:
                    video_ids.append(item['contentDetails']['videoId'])
                
                next_page_token = response.get('nextPageToken')
            
            return video_ids

        def get_channel_stats(youtube, channel_ids):

            all_data = [] #create empty list to store Channel channel_stats_data
            
            request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            id=','.join(channel_ids) # concatenate channel IDs
            )
            response = request.execute() # server is getting back a response for client browser
            
            #loop through items content within the response
            try:

                for item in response['items']:
                    channel_stats_data = {'Channel Name': item['snippet']['title'],
                        'Subscribers': item['statistics']['subscriberCount'],
                        'Views': item['statistics']['viewCount'],
                        'Total Videos': item['statistics']['videoCount'],
                        'Playlist ID': item['contentDetails']['relatedPlaylists']['uploads']
                        }
                    
                    all_data.append(channel_stats_data)
                
                return(pd.DataFrame(all_data))

            except:
                flash("")
                
                #channel_stats="Try re-entering a correct channel ID from youtube."


        channel_stats = get_channel_stats(youtube, channel_ids)
         # Video details in Playlist - ADDED
        def get_video_details(youtube, video_ids):
                       
            all_video_info = []

            for i in range(0, len(video_ids), 50):
                request = youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=','.join(video_ids[i:i+50])
                )
                response = request.execute() 

                for video in response['items']:
                    stats_to_keep = {'snippet': ['channelTitle', 'title'],
                                    'statistics': ['viewCount', 'likeCount', 'commentCount'],
                                    'contentDetails': ['duration', ]
                                    }
                            
                    video_info = {}
                    video_info['video_id'] = video['id']

                    for k in stats_to_keep.keys():
                        for v in stats_to_keep[k]:
                            try:
                                video_info[v] = video[k][v]
                            except:
                                video_info[v] = None

                    all_video_info.append(video_info)
            all_video_info = pd.DataFrame(all_video_info)
            all_video_info['viewCount'] = all_video_info['viewCount'].astype(str).astype(int)
            all_video_info.sort_values(by=['viewCount'], inplace = True, ascending = False)
            all_video_info = all_video_info.head(10).reset_index(drop=True)
            

            return all_video_info

        if channel_stats is None:
            channel_stats_data = [{'Channel Name':"",
                        'Subscribers': "",
                        'Views':"",
                        'Total Videos':"",
                        'Playlist ID':""
                        }]
            channel_stats=pd.DataFrame(channel_stats_data)
            print("Please enter a valid channel ID.")
            
        else:
            video_ids = get_video_ids(youtube, channel_stats['Playlist ID'][0])
            print(video_ids)
            all_video_info = get_video_details(youtube, video_ids)
            print(all_video_info)
            
        print(channel_stats)

    return render_template("index.html", output = channel_stats, output2 = all_video_info)

# Auto-run Application via Saving File
if __name__ == "__main__":
    app.run(debug=True) # setting to true allow us to not have to re-run server, just automatically detects changes


