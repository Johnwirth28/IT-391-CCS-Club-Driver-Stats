import mysql.connector
import json


def main():
    db = mysql.connector.connect(
    host="10.111.21.71",          # VM IP over VPN
    user="admin",                 # admin can connect remotely
    password="admin#ab12cd34",
    database="ccsccDB"
    )
    cursor = db.cursor()
    
    user_driver_name = "Dean Plumadore"

    query = """Select DISTINCT P.session_id, P.personal_best, TP.best_time, W.name, W.date, W.high, W.low, W.link
from 
		(Select min(spd.sp_pax_time) as personal_best, spd.event_session_id as session_id
		from Session_PAX_Data spd
			join Car c
				on c.car_id = spd.car_id 
		where c.car_driver_name = (%s)
		group by spd.event_session_id) as P
		JOIN 
			(Select min(spd.sp_pax_time) as best_time, spd.event_session_id as session_id
			from Session_PAX_Data spd
				join Car c
					on c.car_id = spd.car_id
			group by spd.event_session_id) as TP
		on P.session_id = TP.session_id
		JOIN 
		(Select e.event_name as name, es.evt_session_date as date, wd.high_temp as high, wd.low_temp as low, wd.day_icon as link, spd.event_session_id as session_id 
	from Session_PAX_Data spd
		join Car c
			on c.car_id = spd.car_id
		join Weather_Data wd 
			on wd.event_session_id = spd.event_session_id
		join Event_Session es 
			on es.event_session_id = wd.event_session_id 
		join Event e
			on e.event_id = es.event_id 
	where c.car_driver_name = (%s)) as W
	on TP.session_id = W.session_id
	Order by W.date ASC;"""

    cursor.execute(query,(user_driver_name,user_driver_name))

    response = cursor.fetchall()

    dict = {}
    for row in response:
        event_name = row[3]
        if event_name not in dict.keys():
            dict[event_name] = []
        
        dict[event_name].append([row[1],row[2],row[4].strftime(r'%d/%m/%Y'),row[5],row[6],row[7]])
        # [pb, bt, datestr, high, low, icon_link]
    print(json.dumps(dict,indent=4))
            


    
        











if __name__ == "__main__":
    main()