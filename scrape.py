import requests
import os
import csv
import re
import os.path
import sys
import logging
from bs4 import BeautifulSoup

logging.basicConfig(format = '%(asctime)s %(name)-30s %(levelname)-8s %(message)s', level = logging.DEBUG)

def download(info, 
             url = 'http://www.nadaguides.com/Cars/{year}/{make}/{model}/{trim}/Values',
             file_fmt = '{year}-{make}-{model}-{trim}.html', 
             years = range(2000, 2016),
             path = './html/{make}-{model}-{trim}/'):
    """info should be a dict with make, model, and trim members
    
    """
    path = path.format(**info)
    if not os.path.exists(path):
        os.makedirs(path)
    for year in years:
        info['year'] = year        
        dlurl = url.format(**info)
        filename = os.path.join(path, file_fmt.format(**info))
                
        logging.debug("downloading {} --> {}".format(dlurl, filename))
        
        
        if os.path.exists(filename):
            logging.warn("   SKIP -- output file already exists.")
            return            
        r = requests.get(dlurl)
                
        if r.status_code == requests.status_codes.codes.ok:
            with open (filename, 'w') as f:
                f.write(r.text)            
        else:
            logging.warn("  status -- {}".format(r.status_code))


# http://stackoverflow.com/questions/259091/how-can-i-scrape-an-html-table-to-csv
def cell_text(cell):
    return " ".join(cell.stripped_strings)
    
                
def html_to_csv(pathname):
    """extract prices from html files from nadaguides in the given path"""
    files = os.listdir(pathname)
    
    for filename in files:
        if not filename.endswith("html"):
            continue
            
        filepath = os.path.join(pathname, filename)
        logging.debug("reading {}".format(filepath))
        with open(filepath, 'r') as f:
            s = BeautifulSoup (f.read())
            tbl = s.select(".tbl-pricing")[0]
            
            #print tbl
    
            csv_file = os.path.splitext(filepath)[0] + '.csv'
            
            with open (csv_file, 'w') as ofile:
                output = csv.writer(ofile)
                for row in tbl.find_all('tr'):
                    col = map(cell_text, row.find_all(re.compile('t[dh]')))
                    output.writerow(col)
                output.writerow([])

    

#download ({'make':'Toyota',
           #'model': 'Tacoma-Double-Cab',
           #'trim': 'Base-4WD-V6'})

#download ({'make':'Toyota',
           #'model': 'Tacoma-Double-Cab-V6',
           #'trim': 'Base-4WD'})


           
           
#html_to_csv("/home/alan/Src/python/nadaScrape/html/Toyota-Tacoma-Double-Cab-Base-4WD-V6")


def plot_csv(pathname):
    """plot extracted data"""
    files = os.listdir(pathname)
    
    data = []
    
    for filename in files:
        if not filename.endswith("csv"):
            continue
        if filename == 'output.csv':
            continue
        
        year = int(filename.split("-")[0])
        
        
        
        csvfile = os.path.join(pathname, filename)
        logging.debug("Reading {}".format(csvfile))
        with open(csvfile, 'r') as f:
            csvr = csv.DictReader(f)
            #print csvr.fieldnames
            for row in csvr:
                if row[''] == 'Price with Options':
                    row['year'] = year
                    
                    data += [row]
                    
                    
    fields = ['Rough Trade-In', 'Average Trade-In', 'Clean Trade-In', 'Clean Retail', 'year', 'MSRP', 'Invoice', '']

            
    outfile = os.path.join(pathname, 'output.csv')
    logging.info("writing output to {}".format(outfile))
    with open(outfile, 'w') as outf:
        wr = csv.DictWriter(outf, fields)
        wr.writeheader()
        wr.writerows(data)
    
        

plot_csv("/home/alan/Src/python/nadaScrape/html/Toyota-Tacoma-Double-Cab-Base-4WD-V6")
