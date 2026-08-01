import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('client_frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

ids_to_check = [
    'profileFullName', 'profilePhone', 'profileEmail', 'profileShipping',
    'userNameDisplay', 'userPhoneDisplay', 'userAvatar', 'userShippingDisplay',
    'garageContainer', 'garageCountBadge', 'addGarageCarForm',
    'clientVinInput', 'clientVinCounter', 'requestCarSelect', 
    'requestForm', 'claimPinForm', 'requestsHistoryContainer',
    'myOrdersContainer', 'serviceTimelineContainer', 'toastContainer',
    'authScreen', 'mainScreen', 'registerForm', 'loginForm',
    'bottomNav', 'viewGarage', 'viewRequests', 'viewOrders', 'viewProfile'
]

for id_name in ids_to_check:
    found = f'id="{id_name}"' in html
    status = '✅' if found else '❌ MISSING'
    print(f'{status}: {id_name}')
