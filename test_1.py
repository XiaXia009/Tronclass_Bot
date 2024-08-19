from datetime import datetime

# 每一天的課表，使用嵌套字典結構
days_of_week = ["一", "二", "三", "四", "五", "六", "日"]
weekly_schedule = {
    "一": [
        {"period": 1, "start": "08:10", "end": "09:00", "status": "課堂", "subject": "電腦網路實習", "location": "BRA0201"},
        {"period": "break1", "start": "09:00", "end": "09:10", "status": "下課", "subject": "", "location": ""},
        {"period": 2, "start": "09:10", "end": "10:00", "status": "課堂", "subject": "電腦網路實習", "location": "BRA0201"},
        {"period": "break2", "start": "10:00", "end": "10:10", "status": "下課", "subject": "", "location": ""},
        {"period": 3, "start": "10:10", "end": "11:00", "status": "課堂", "subject": "電腦網路實習", "location": "BRA0201"},
        {"period": "break3", "start": "11:00", "end": "11:10", "status": "下課", "subject": "", "location": ""},
        {"period": 4, "start": "11:10", "end": "12:00", "status": "課堂", "subject": "數學", "location": "ATB0201"},
        {"period": "lunch", "start": "12:00", "end": "13:20", "status": "午休", "subject": "", "location": ""},
        {"period": 5, "start": "13:20", "end": "14:10", "status": "課堂", "subject": "計算機程式實習", "location": "BCB0305"},
        {"period": "break5", "start": "14:10", "end": "14:20", "status": "下課", "subject": "", "location": ""},
        {"period": 6, "start": "14:20", "end": "15:10", "status": "課堂", "subject": "計算機程式實習", "location": "BCB0305"},
        {"period": "break6", "start": "15:10", "end": "15:20", "status": "下課", "subject": "", "location": ""},
        {"period": 7, "start": "15:20", "end": "16:10", "status": "課堂", "subject": "計算機程式實習", "location": "BCB0305"},
        {"period": "break7", "start": "16:10", "end": "16:20", "status": "下課", "subject": "", "location": ""},
        {"period": 8, "start": "16:20", "end": "17:10", "status": "課堂", "subject": "全民國防教育", "location": "ATB0202"},
    ],
    "二": [
        {"period": 1, "start": "08:10", "end": "09:00", "status": "課堂", "subject": "數學", "location": "ATB0201"},
        {"period": "break1", "start": "09:00", "end": "09:10", "status": "下課", "subject": "", "location": ""},
        {"period": 2, "start": "09:10", "end": "10:00", "status": "課堂", "subject": "數學", "location": "ATB0201"},
        {"period": "break2", "start": "10:00", "end": "10:10", "status": "下課", "subject": "", "location": ""},
        {"period": 3, "start": "10:10", "end": "11:00", "status": "課堂", "subject": "電子學", "location": "ATB0201"},
        {"period": "break3", "start": "11:00", "end": "11:10", "status": "下課", "subject": "", "location": ""},
        {"period": 4, "start": "11:10", "end": "12:00", "status": "課堂", "subject": "電子學", "location": "ATB0201"},
        {"period": "lunch", "start": "12:00", "end": "13:20", "status": "午休", "subject": "", "location": ""},
        {"period": 5, "start": "13:20", "end": "14:10", "status": "課堂", "subject": "英文", "location": "ATB0201/ATD0201"},
        {"period": "break5", "start": "14:10", "end": "14:20", "status": "下課", "subject": "", "location": ""},
        {"period": 6, "start": "14:20", "end": "15:10", "status": "課堂", "subject": "英文", "location": "ATB0201/ATD0201"},
        {"period": "break6", "start": "15:10", "end": "15:20", "status": "下課", "subject": "", "location": ""},
        {"period": 7, "start": "15:20", "end": "16:10", "status": "課堂", "subject": "國文", "location": "ATD0202"},
        {"period": "break7", "start": "16:10", "end": "16:20", "status": "下課", "subject": "", "location": ""},
        {"period": 8, "start": "16:20", "end": "17:10", "status": "課堂", "subject": "國文", "location": "ATD0202"},
    ],
    "三": [
        {"period": 2, "start": "09:10", "end": "10:00", "status": "課堂", "subject": "電腦硬體裝修", "location": "BRA0102"},
        {"period": "break2", "start": "10:00", "end": "10:10", "status": "下課", "subject": "", "location": ""},
        {"period": 3, "start": "10:10", "end": "11:00", "status": "課堂", "subject": "電腦硬體裝修", "location": "BRA0102"},
        {"period": "break3", "start": "11:00", "end": "11:10", "status": "下課", "subject": "", "location": ""},
        {"period": 4, "start": "11:10", "end": "12:00", "status": "課堂", "subject": "電腦硬體裝修", "location": "BRA0102"},
        {"period": "lunch", "start": "12:00", "end": "13:20", "status": "午休", "subject": "", "location": ""},
        {"period": 5, "start": "13:20", "end": "14:10", "status": "課堂", "subject": "電腦網路概論", "location": "OAA0104"},
        {"period": "break5", "start": "14:10", "end": "14:20", "status": "下課", "subject": "", "location": ""},
        {"period": 6, "start": "14:20", "end": "15:10", "status": "課堂", "subject": "電腦網路概論", "location": "OAA0104"},
        {"period": "break6", "start": "15:10", "end": "15:20", "status": "下課", "subject": "", "location": ""},
        {"period": 7, "start": "15:20", "end": "16:10", "status": "課堂", "subject": "電腦網路概論", "location": "OAA0104"},
    ],
    "四": [
        {"period": 1, "start": "08:10", "end": "09:00", "status": "課堂", "subject": "網頁設計", "location": "BCB0305"},
        {"period": "break1", "start": "09:00", "end": "09:10", "status": "下課", "subject": "", "location": ""},
        {"period": 2, "start": "09:10", "end": "10:00", "status": "課堂", "subject": "網頁設計", "location": "BCB0305"},
        {"period": "break2", "start": "10:00", "end": "10:10", "status": "下課", "subject": "", "location": ""},
        {"period": 3, "start": "10:10", "end": "11:00", "status": "課堂", "subject": "網頁設計", "location": "BCB0305"},
        {"period": "break3", "start": "11:00", "end": "11:10", "status": "下課", "subject": "", "location": ""},
        {"period": 4, "start": "11:10", "end": "12:00", "status": "課堂", "subject": "電子學", "location": "BRA0102"},
        {"period": "lunch", "start": "12:00", "end": "13:20", "status": "午休", "subject": "", "location": ""},
        {"period": 5, "start": "13:20", "end": "14:10", "status": "課堂", "subject": "體育", "location": "CPB0101"},
        {"period": "break5", "start": "14:10", "end": "14:20", "status": "下課", "subject": "", "location": ""},
        {"period": 6, "start": "14:20", "end": "15:10", "status": "課堂", "subject": "體育", "location": "CPB0101"},
    ],
    "五": [
        {"period": 3, "start": "10:10", "end": "11:00", "status": "課堂", "subject": "生命教育", "location": "BRA0102"},
        {"period": "break3", "start": "11:00", "end": "11:10", "status": "下課", "subject": "", "location": ""},
        {"period": 4, "start": "11:10", "end": "12:00", "status": "課堂", "subject": "生命教育", "location": "BRA0102"},
        {"period": "lunch+break5", "start": "12:00", "end": "14:20", "status": "午休+下課", "subject": "", "location": ""},
        {"period": 6, "start": "14:20", "end": "15:10", "status": "課堂", "subject": "電子學實習", "location": "BGC0501"},
        {"period": "break6", "start": "15:10", "end": "15:20", "status": "下課", "subject": "", "location": ""},
        {"period": 7, "start": "15:20", "end": "16:10", "status": "課堂", "subject": "電子學實習", "location": "BGC0501"},
        {"period": "break7", "start": "16:10", "end": "16:20", "status": "下課", "subject": "", "location": ""},
        {"period": 8, "start": "16:20", "end": "17:10", "status": "課堂", "subject": "電子學實習", "location": "BGC0501"},
    ],
}

def get_current_and_next_class(day, time_str):
    time_now = datetime.strptime(time_str, "%H:%M")
    current_status = "放學"
    next_status = "放學"
    current_subject = ""
    current_location = ""
    next_subject = ""
    next_location = ""
    
    day_schedule = weekly_schedule.get(day, [])
    current_period = None
    next_period = None
    
    for period in day_schedule:
        start_time = datetime.strptime(period["start"], "%H:%M")
        end_time = datetime.strptime(period["end"], "%H:%M")
        
        if start_time <= time_now <= end_time:
            current_status = period["status"]
            current_subject = period["subject"]
            current_location = period["location"]
            current_period = period
            remaining_minutes = (end_time - time_now).seconds // 60
            break
    
    if current_period:
        period_index = day_schedule.index(current_period)
        next_period_index = period_index + 1
        
        while next_period_index < len(day_schedule):
            next_period = day_schedule[next_period_index]
            if next_period["status"] != "下課":
                next_status = next_period["status"]
                next_subject = next_period["subject"]
                next_location = next_period["location"]
                break
            next_period_index += 1
    
    return current_status, current_subject, current_location, remaining_minutes, next_status, next_subject, next_location

current_time = "12:01"
current_day = "五"

current_status, current_subject, current_location, remaining_minutes, next_status, next_subject, next_location = get_current_and_next_class(current_day, current_time)
print(f"這節課: {current_status} - {current_subject} ({current_location})")
print(f"還有多久下課: {remaining_minutes}")
print(f"下節課: {next_status} - {next_subject} ({next_location})")