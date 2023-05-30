import asyncio
import os

from twitchAPI.twitch import Twitch
from ics import Calendar, Event


async def generate_calendar():
    c = Calendar()
    c.creator = "Twitch Followed Streams"

    twitch_client_id = os.environ["TWITCH_CLIENT_ID"]
    twitch_client_secret = os.environ["TWITCH_CLIENT_SECRET"]

    twitch = await Twitch(twitch_client_id, twitch_client_secret)

    # Extract usernames from 'FollowedStreams.config' file
    usernames = []
    with open("FollowedStreams.config", "r") as f:
        for line in f:
            if line[0] != "#":
                usernames.append(line.strip())

    users = twitch.get_users(logins=usernames)

    async for user in users:
        print(user.display_name)
        schedule = await twitch.get_channel_stream_schedule(user.id)
        segment_count = 0
        async for segment in schedule:
            e = Event()
            e.name = f"{user.display_name}: {segment.title}"
            e.begin = segment.start_time
            e.end = segment.end_time
            e.description = user.description
            e.url = f"https://twitch.tv/{user.display_name}"
            c.events.add(e)

            segment_count += 1
            if segment_count >= 100:
                break

    with open("calendar.ics", "w") as f:
        f.writelines(c.serialize_iter())


if __name__ == "__main__":
    asyncio.run(generate_calendar())
