import time
from datetime import datetime, timedelta

def wait_until(target_hour=9, target_minute=35):
    now = datetime.now()
    target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)

    # If the target time has already passed today, schedule for the next day
    if now >= target_time:
        target_time += timedelta(days=1)

    time_to_wait = (target_time - now).total_seconds()
    print(f"Waiting for {int(time_to_wait)} seconds until {target_time.strftime('%I:%M %p')}...")
    time.sleep(time_to_wait)
    print("It's now 9:35 AM. Starting the script...")