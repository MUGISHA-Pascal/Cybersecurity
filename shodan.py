import shodan
SHODAN_API_KEY='XImCRKmMc2p9IMpfIFeaJJS3aDVv9ww7'
api = shodan.Shodan(SHODAN_API_KEY)

results=api.search('apache')
print('result found : {}'.format (results['total']))
for result in results['matches']:
    print('IP: {}'.format(result['ip_str']))
    print(result['data'])
    print('')
