import urllib.request
import json
from datetime import datetime
from ics import Calendar,Event
# Get the dataset metadata by passing package_id to the package_search endpoint
# For example, to retrieve the metadata for this dataset:
def proc_sched(sched):
        cal={}
        for item in sched:
                print(item.keys())
                cal_type = item["Calendar"].replace(" ","")
                if cal_type not in cal:
                        cal[cal_type]={}
                cal[cal_type].update({item["WeekStarting"] :gen_pickup(item)})
        #print(cal)
        return cal
def get_id_list():
        url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/package_show"
        params = { "id": "7b70189a-aede-42f1-b092-8708fa4f5fc3"}
        response = urllib.request.urlopen(url, data=bytes(json.dumps(params), encoding="utf-8"))
        package = json.loads(response.read())
        idlist = []
        for keys in package['result']['resources']:
                if keys["datastore_active"] and keys["last_modified"]:
                        date_obj = datetime.strptime(keys["last_modified"],'%Y-%m-%dT%H:%M:%S.%f')
                        if date_obj >= datetime(2020,1,1):
                                idlist.append(keys["id"])
        return idlist
def get_cal(id):
        url = "https://ckan0.cf.opendata.inter.prod-toronto.ca/api/3/action/datastore_search"
        cal = list()
        total = 1
        offset = 0
        while offset < total:
                # print(total,offset)
                p = { "id": id,"offset": offset }
                r = urllib.request.urlopen(url, data=bytes(json.dumps(p), encoding="utf-8"))
                data = json.loads(r.read())
                if data["success"]:
                        total = data["result"]["total"]
                        for record in data["result"]["records"]:
                                cal.append(record)
                        #cal.append(data["result"]["records"])
                        offset+=100
                else: 
                        break
        return cal
def create_ics(cal):
        for cal_type in cal:
                # print(cal[cal_type])
                c = Calendar()
                for date in cal[cal_type]:
                        e = Event()
                        date_obj = datetime.strptime(date,'%Y-%m-%dT%H:%M:%S')
                        e.begin = date_obj
                        e.name = "Solid Waste Pickup"
                        e.description = cal[cal_type][date]
                        e.transparent = True
                        e.make_all_day()
                        c.events.add(e)
                filename=cal_type+"_"+date_obj.strftime("%Y")+".ics"               
                with open(filename,'w') as f:
                        f.write(str(c))
def gen_pickup(list_val):
        list_pickup = list()
        if list_val["GreenBin"] != '0':
                list_pickup.append("Green Bin")
        if list_val["Garbage"] != '0':
                list_pickup.append("Garbage")        
        if list_val["Recycling"] != '0':
                list_pickup.append("Recycling")
        if list_val["YardWaste"] != '0':
                list_pickup.append("Yard Waste")
        if list_val["ChristmasTree"] != '0':
                list_pickup.append("Christmas Tree")
        str_list = ','.join(list_pickup)
        print(list_val)
        print(str_list)
        return str_list
def main():
        cal = list()
        for id in get_id_list():
                # print(id)
                cal = get_cal(id)
                sorted_cal = proc_sched(cal)
                create_ics(sorted_cal)
                # print(len(get_cal(id)))
                #print(response["records"][0].items())
'''                 for cal in response["records"]["Calendar"]:
                        print(record)
                        cal.append(response['records']) '''
        #print(cal[2][0])
        #cal_dict = proc_sched(response['records'])
        #create_ics(cal_dict)
main()