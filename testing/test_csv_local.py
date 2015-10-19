import json,requests,csv,time
#from requests.auth import HTTPBasicAuth

INPUT_ADDRESS_FILE = "input.csv"
RESULT_ADDRESS_FILE = "output.csv"

HEADERS = {'Content-type': 'application/json', 'Accept': 'text/plain'}

RESULTS_URL = 'http://127.0.0.1:5000/get_category'

f = open(INPUT_ADDRESS_FILE)
reader = csv.reader(f)
keys = reader.next()

f2 = open(RESULT_ADDRESS_FILE, 'w')

l = ['wbn','product_name', 'category', 'sub_category', 'dangerous', 'cached']

writer = csv.DictWriter(f2, fieldnames = l)
writer.writeheader()

num_cache = 0

for row in reader:
    max_retry = 0
    payload = []
    record_dict = {}
    
    try:
        for i in range(len(row)):
            record_dict[keys[i]] = row[i]
            payload.append({'wbn' : row[0], "product_name" : row[1]})
        
        while max_retry < 5:
            r2 = requests.post(RESULTS_URL, data = json.dumps(payload),
                            headers = HEADERS)
            
            if r2.status_code == 200:
                res = r2.json()
                x = {}
                x['wbn'] = record_dict['wbn']
                x['product_name'] = record_dict['product_name']
                
                if 'category' in res[0]:
                    x['category']       = res[0]['category']
                    x['sub_category']   = res[0]['sub_category']
                    x['dangerous']      = res[0]['dangerous']
                    x['cached']         = res[0]['cached']

                    if x['cached']:
                        num_cache += 1

                writer.writerow(x)
                break
            else:
                max_retry += 1
                time.sleep(0.3)

    except Exception as err:
        print('Exception {} against request: {}'.format(err, payload))
        continue

f.close()
f2.close()
print 'num_cache = ', num_cache

