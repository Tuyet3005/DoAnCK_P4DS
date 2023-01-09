from bs4 import BeautifulSoup
import requests
import urllib.parse
import json

def parse_number(number):
    if number == '..':
        return None
    return float(number.replace('.', '').replace(',', '.'))


def get_data_from_url(url):
    # Parse the form to get all the values we need to post
    form_soup = BeautifulSoup(requests.get(url, verify=False).text, 'html.parser')
    iframe = form_soup.select_one('iframe[src*="pxweb"]')
    form_soup = BeautifulSoup(requests.get(iframe.get('src'), verify=False).text, 'html.parser')
    form = form_soup.select_one('form[action*="./?rxid"]')
    values = {}

    for form_input in form.select('input'):
        if form_input.get('value') is not None:
            values[form_input.get('name')] = form_input.get('value')

    for select in form.select('select'):
        if select.get('multiple'):
            values[select.get('name')] = [option.get('value') for option in select.select('option')]
        else:
            values[select.get('name')] = select.select_one('option').get('value')

    form_action = form.get('action')
    # Since form action is relative url, we need to join it with iframe src
    full_action = urllib.parse.urljoin(iframe.get('src'), form_action)

    # Post the form and get the response
    response = requests.post(full_action, data=values, verify=False).text
    print(response)
    soup = BeautifulSoup(response, 'html.parser')

    table = soup.select_one('.table-class')

    # Parse the returned table
    summary = table.get('summary')
    rows_id = form_soup.select_one('#ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_VariableSelectorValueSelectRepeater_ctl01_VariableValueSelect_VariableValueSelect_VariableTitle').text
    cols_id = form_soup.select_one('#ctl00_ContentPlaceHolderMain_VariableSelector1_VariableSelector1_VariableSelectorValueSelectRepeater_ctl02_VariableValueSelect_VariableValueSelect_VariableTitle').text
    col_labels = [col_label.text for col_label in table.select('thead tr:nth-child(2) th')]
    row_labels = [row_label.text for row_label in table.select('tbody tr th')]
    values = sum([
        [parse_number(value.text) for value in row.select('td')]
        for row in table.select('tbody tr')
    ], start=[])

    data = {}

    # Fill default data
    data['status'] = {'130': None}
    data['source'] = None
    data['updated'] = "9999-12-31T16:59:59Z"

    data['label'] = summary
    data['value'] = values
    data['dimension'] = {
        rows_id: {
            'label': rows_id,
            'category': {
                'index': {str(i): i for i in range(len(row_labels))},
                'label': {i: label for i, label in enumerate(row_labels)}
            }
        },
        cols_id: {
            'label': cols_id,
            'category': {
                'index': {str(i): i for i in range(len(col_labels))},
                'label': {i: label for i, label in enumerate(col_labels)}
            }
        },
        'id': [rows_id, cols_id],
        'size': [len(row_labels), len(col_labels)],
        'role': {}
    }

    return {
        'dataset': data
    }


def get_and_write_file(filename, url):
    c = get_data_from_url(url)
    result = json.dumps(c)
    f = open(f'{filename}.json', "a")
    f.write(result)
    f.close()


get_and_write_file('lao_dong_theo_nghe', 'https://www.gso.gov.vn/px-web-2/?pxid=V0241&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng')
get_and_write_file('nang_suat_lao_dong', 'https://www.gso.gov.vn/px-web-2/?pxid=V0249&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng')
get_and_write_file('luc_luong_lao_dong', 'https://www.gso.gov.vn/px-web-2/?pxid=V0234&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng')
get_and_write_file('ti_le_lao_dong', 'https://www.gso.gov.vn/px-web-2/?pxid=V0248&theme=D%C3%A2n%20s%E1%BB%91%20v%C3%A0%20lao%20%C4%91%E1%BB%99ng')

