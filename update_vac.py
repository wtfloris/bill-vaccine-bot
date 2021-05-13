from requests_html import HTMLSession
from time import sleep
import os, os.path

for pc in os.listdir('data'):
    with open(f'data/{pc}', 'w') as f:
        for loc in HTMLSession().get(f'https://www.prullenbakvaccin.nl/{pc}').html.find('.card-title'):
            if "Heeft geen vaccins" not in loc.text:
                f.write(loc.text + '\n')
    sleep(2)