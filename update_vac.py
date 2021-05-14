from requests_html import HTMLSession
from time import sleep
import os, os.path

for pc in os.listdir('/var/lib/bill-vaccine-bot/data'):
    with open(f'/var/lib/bill-vaccine-bot/data/{pc}', 'w') as f:
        for loc in HTMLSession().get(f'https://www.prullenbakvaccin.nl/{pc}').html.find('.card-body'):
            if "Heeft geen vaccins" not in loc.text:
                f.write(loc.text + '\n')
    sleep(2)
