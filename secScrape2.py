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

# request the 2019 url
content = requests.get(year_url)
decoded_content = content.json()

filelist = []

#loop through the dictionary
for item in decoded_content['directory']['item']:

    #create the qtr url
    qtr_url = make_url(base_url, ['2019', item['name'], 'index.json'])

    #request the url and decode it
    file_content = requests.get(qtr_url)
    decoded_content = file_content.json()

    for file in decoded_content['directory']['item']:

        if file['name'][0] == 'm':
            file_url = make_url(base_url, ['2019', item['name'], file['name']])
            filelist.append(file_url)

# file_url = r"https://www.sec.gov/Archives/edgar/daily-index/2019/QTR2/master.20190401.idx"

balanceSheetCount = 0

# make list of s&p 500 companies
snp = []
with open('S&PcompaniesCIK.txt') as f:
    for line in f:
        data = line.split()
        snp.append(data[0])


unique_names = []

for file_url in filelist:
    content = requests.get(file_url).content

    with open('master_20190401.txt', 'wb') as f:
        f.write(content)

    with open('master_20190401.txt', 'rb') as f:
        byte_data = f.read()

    #decode the byte data
    data = byte_data.decode('utf-8').split('--------------------------------------------------------------------------------')


    # We need to remove the headers, so look for the end of the header and grab it's index
    for index, item in enumerate(data):
        if "ftp://ftp.sec.gov/edgar/" in item:
            start_ind = index + 1

    # define a new dataset with out the header info.
    data_format = data[start_ind:]

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


    # by being in a dictionary format, it'll be easier to get the items we need.
    for document_dict in master_data:#[0:100]:

        # if it's a 10-K document pull the url and the name.
        if document_dict['cik_number'] in snp:
            if document_dict['form_id'] == '10-K' or document_dict['form_id'] == 'NT 10-K':
                # count += 1
                # get the components
                comp_name = document_dict['company_name']
                docu_url = document_dict['file_url']
                
                # print('-'*100)
                # print(comp_name)
                # print(docu_url)

                # Create a url that will take us to the archive folder
                archive_url = docu_url.replace('.txt','/index.json').replace('-','')

                # print('-'*100)
                # print('     The Archive Folder can be found here: {}'.format(archive_url))

                # normal_url = normal_url.replace('-','').replace('.txt','/index.json')


                # # Create a url that takes us to the Detail filing landing page
                # file_url_adj = docu_url.split('.txt')
                # file_url_archive = file_url_adj[0] + '-index.htm'

                # print('-'*100)
                # print('     The Filing Detail can be found here: {}'.format(file_url_archive))



                # # Create a url that will take us the Company filing Archive
                # company_url =docu_url.rpartition('/')

                # print('-'*100)
                # print('     The Company Archive Folder can be found here: {}'.format(company_url[0]))

# print("total count of companies is", count)


                base_url = r"https://www.sec.gov"

                # request the url and decode it.
                content = requests.get(archive_url).json()

                for file in content['directory']['item']:
                    
                    # Grab the filing summary and create a new url leading to the file so we can download it.
                    if file['name'] == 'FilingSummary.xml':

                        xml_summary = base_url + content['directory']['name'] + "/" + file['name']
                        
                        # print('-' * 100)
                        # print('File Name: ' + file['name'])
                        # print('File Path: ' + xml_summary)

                # define a new base url that represents the filing folder. This will come in handy when we need to download the reports.
                base_url = xml_summary.replace('FilingSummary.xml', '')

                # request and parse the content
                content = requests.get(xml_summary).content
                soup = BeautifulSoup(content, 'lxml')

                # print(soup)

                # find the 'myreports' tag because this contains all the individual reports submitted.
                reports = soup.find('myreports')
                # print(reports)

                # I want a list to store all the individual components of the report, so create the master list.
                master_reports = []

                # store where the balance sheet position
                bs_location = 0

                # loop through each report in the 'myreports' tag but avoid the last one as this will cause an error.
                for report in reports.find_all('report')[:10]:

                    # let's create a dictionary to store all the different parts we need.
                    report_dict = {}
                    report_dict['name_short'] = report.shortname.text
                    # report_dict['name_long'] = report.longname.text
                    # report_dict['position'] = report.position.text
                    # report_dict['category'] = report.menucategory.text
                    report_dict['url'] = base_url + report.htmlfilename.text


                    bs_titles_list = ['consolidated balance sheets', 'consolidated balance sheet', 'consolidated statements of financial position', \
                        'consolidated statement of financial position', 'condensed consolidated balance sheets', 'condensed consolidated balance sheet', \
                            'statement of financial position', 'statements of financial position', 'consolidated statements of financial condition', 'consolidated statement of financial condition', \
                                'consolidated balance sheet statement', 'consolidated balance sheets consolidated balance sheets', 'consolidated condensed balance sheets', \
                                    'consolidated financial position', 'consolidated and combined statements of financial position', 'balance sheets', 'balance sheet', \
                                        'Carnival Corporation & PLC Consolidated Balance Sheets'.lower(), 'Consolidated Balance Sheets, as of December 31'.lower(), \
                                            'BorgWarner Inc. and Consolidated Subsidiaries Consolidated Balance Sheets'.lower(), \
                                                'MAALP Consolidated Balance Sheets'.lower(), 'consolidated statements of condition', 'consolidated statement of condition']

                    if report.shortname.text.lower() in bs_titles_list:
                        bs_location = report.position.text

                    # append the dictionary to the master list.
                    master_reports.append(report_dict)

                    # # print the info to the user.
                    # print('-'*100)
                    # print(base_url + report.htmlfilename.text)
                    # print(report.longname.text)
                    # print(report.shortname.text)
                    # print(report.menucategory.text)
                    # print(report.position.text)

                    # if report.shortname.text.lower() == 'consolidated balance sheets' or report.shortname.text.lower() == 'consolidated balance sheet':
                    #     count += 1

                if bs_location == 0:
                    balanceSheetCount += 1
                    print(document_dict['company_name'], master_reports, bs_location)
                # # create the list to hold the statement urls
                # statements_url = []

                # for report_dict in master_reports:
                    
                # #     # define the statements we want to look for.
                # #     item1 = r"Consolidated Balance Sheets"
                # #     item2 = r"Consolidated Statements of Operations and Comprehensive Income (Loss)"
                # #     item3 = r"Consolidated Statements of Cash Flows"
                # #     item4 = r"Consolidated Statements of Stockholder's (Deficit) Equity"
                    
                # #     # store them in a list.
                # #     report_list = [item1, item2, item3, item4]
                    
                # #     # if the short name can be found in the report list.
                #     if report_dict['name_short'].lower() == 'consolidated balance sheets':
                        
                #         # print some info and store it in the statements url.
                #         print('-'*100)
                #         print(report_dict['name_short'])
                #         print(report_dict['url'])
                        
                #     #     statements_url.append(report_dict['url'])
                #     if int(report_dict['position']) < 5:
                #         if report_dict['name_short'] not in unique_names:
                #             unique_names.append(report_dict['name_short'])
                            
                # # print(unique_names)

print('count is', balanceSheetCount)
 
# count = 0
# for i in range(1, len(unique_names)):
#     if "Balance Sheet".lower() in unique_names[i].lower():
#         count = count + 1
# print("Count is", count)