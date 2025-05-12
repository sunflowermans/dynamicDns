import requests
import miniupnpc
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

scheduledJobSeconds = 6 * 60 * 60 # 6 hours
ddnsbase = 'https://dynamicdns.park-your-domain.com/update?host={0}&domain={1}&password={2}&ip={3}'
atsub = '@'
wwwsub = 'www'
configPath = 'C:\\Users\\direc\\bleh\\dynamicDns\\dnsConfig.txt' #comma-delimited list of DOMAIN,PASSWORD

def get_domain_from_file():
    # Open the file in read mode
    file = open(configPath, 'r')
    # Read the entire content of the file
    content = file.read()
    domain = content.split(',')[0].strip()
    file.close()
    return domain

def get_password_from_file():
    # Open the file in read mode
    file = open(configPath, 'r')
    # Read the entire content of the file
    content = file.read()
    password = content.split(',')[1].strip()
    file.close()
    return password

def log(msg):
    ct = datetime.datetime.now()
    print(f'{ct}: {msg}')

def get_ip_address():
    u = miniupnpc.UPnP()
    u.discoverdelay = 200
    u.discover()
    u.selectigd()
    return u.externalipaddress()

def construct_url(sub, domain, password, ip):
    return ddnsbase.format(sub, domain, password, ip)

def update_dns():
    # Use a breakpoint in the code line below to debug your script.
    ip = get_ip_address()
    try:
        domain = get_domain_from_file()
    except:
        log('Error failed to get domain from config file')
        return

    try:
        password = get_password_from_file()
    except:
        log('Error failed to get password from config file')
        return

    log(f'Retrieved IP address: {ip}')

    atUrl = construct_url(atsub, domain, password, ip)
    wwwUrl = construct_url(wwwsub, domain, password, ip)

    log(f'Updating {domain} dns for sub {atsub}')
    perform_get_request(atUrl)

    log(f'Updating {domain} dns for sub {wwwsub}')
    perform_get_request(wwwUrl)

def perform_get_request(url):
    try:
        response = requests.get(url)
        #split limit of 1. Make sure found that.
        split = response.text.split('<ErrCount>', 1)
        errorCount = '-1'
        if len(split) > 1:
            errorCount = split[1][0]
        else:
            log(f'Error parsing response! RESPONSE: \n{response.text}')

        if errorCount != '0':
            log(f'Error returned in response! RESPONSE: \n{response.text}')
        else:
            log('Successfully updated dns!')
    except:
        log('Error performing GET request!')

#perform first on startup and then once every specified time period
update_dns()
log('Job ended!')
log('Job scheduled. Waiting...')
sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=scheduledJobSeconds)
def timed_job():
    log('Running scheduled job...')
    update_dns()
    log('Job ended!')
    log('Job scheduled. Waiting...')

sched.start()
# Nothing past this point will get run