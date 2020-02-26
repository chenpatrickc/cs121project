import requests
import urllib
from bs4 import BeautifulSoup

def make_url(base_url, comp):

    url = base_url

    # add each component to the base url
    for r in comp:
        url = '{}/{}'.format(url, r)

    return url

# base url for the daily index files
base_url = r"https://www.sec.gov/Archives/edgar/daily-index"

year = 2019
# create the daily index url for 2019
year_url = make_url(base_url, [year, 'index.json'])
# print(year_url)

# request the 2019 url
content = requests.get(year_url)
decoded_content = content.json()
# print(decoded_content)

filelist = []
#loop through the dictionary
for item in decoded_content['directory']['item']:

    #get the name of the folder
    # print('-'*100)
    # print('Pulling url for quarter {}'.format(item['name']))

    #create the qtr url
    qtr_url = make_url(base_url, ['2019', item['name'], 'index.json'])

    # print(qtr_url)
    #request the url and decode it
    file_content = requests.get(qtr_url)
    decoded_content = file_content.json()
    # print(decoded_content)

    # print('-'*100)
    # print('Pulling files')

    for file in decoded_content['directory']['item']:

        if file['name'][0] == 'm':
            file_url = make_url(base_url, ['2019', item['name'], file['name']])
            filelist.append(file_url)

# file_url = r"https://www.sec.gov/Archives/edgar/daily-index/2019/QTR2/master.20190401.idx"

for file_url in filelist[:31]:
    # print(file_url)
    content = requests.get(file_url).content

    with open('master_20190401.txt', 'wb') as f:
        f.write(content)

    with open('master_20190401.txt', 'rb') as f:
        byte_data = f.read()

    # print(byte_data)
    #decode the byte data
    # data = byte_data.decode('utf-8').split('  ')
    data = byte_data.decode('utf-8').split('--------------------------------------------------------------------------------')

    # print(data[1])

    # We need to remove the headers, so look for the end of the header and grab it's index
    for index, item in enumerate(data):
        if "ftp://ftp.sec.gov/edgar/" in item:
            start_ind = index + 1
    # print('start index is ', start_ind)

    # define a new dataset with out the header info.
    data_format = data[start_ind:]

    # data_format = data[1]
    # print(data_format)
    # print(len(data_format))

    master_data = []

    # now we need to break the data into sections, this way we can move to the final step of getting each row value.
    for index, item in enumerate(data_format):
        clean_item_data = item.replace('\n','|').split('|')
            
        for index, row in enumerate(clean_item_data):
            
            # when you find the text file.
            if '.txt' in row:
                # grab the values that belong to that row. It's 4 values before and one after.
                mini_list = clean_item_data[(index - 4): index + 1]
                
                if len(mini_list) != 0:
                    mini_list[4] = "https://www.sec.gov/Archives/" + mini_list[4]
                    master_data.append(mini_list)
                    
    # print(master_data[:3])
    # loop through each document in the master list.
    for index, document in enumerate(master_data):
        
        # create a dictionary for each document in the master list
        document_dict = {}
        document_dict['cik_number'] = document[0]
        document_dict['company_name'] = document[1]
        document_dict['form_id'] = document[2]
        document_dict['date'] = document[3]
        document_dict['file_url'] = document[4]
        
        master_data[index] = document_dict

    # print(master_data[:3])


    # by being in a dictionary format, it'll be easier to get the items we need.
    for document_dict in master_data:#[0:100]:

        # if it's a 10-K document pull the url and the name.
        if document_dict['form_id'] == '10-K' or document_dict['form_id'] == 'NT 10-K':
            # print(document_dict['file_url'])
            # get the components
            comp_name = document_dict['company_name']
            docu_url = document_dict['file_url']
            
            print('-'*100)
            print(comp_name)
            print(docu_url)

            # Create a url that takes us to the Detail filing landing page
            file_url_adj = docu_url.split('.txt')
            file_url_archive = file_url_adj[0] + '-index.htm'

            print('-'*100)
            print('     The Filing Detail can be found here: {}'.format(file_url_archive))

            # Create a url that will take us to the archive folder
            archive_url = docu_url.replace('.txt','').replace('-','')

            print('-'*100)
            print('     The Archive Folder can be found here: {}'.format(archive_url))

            # Create a url that will take us the Company filing Archive
            company_url =docu_url.rpartition('/')

            print('-'*100)
            print('     The Company Archive Folder can be found here: {}'.format(company_url[0]))