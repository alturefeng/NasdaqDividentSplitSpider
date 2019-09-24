import os
import sys
import requests
import json
import time
#import sched
#from threading import Timer
import logging

#pip install schedule
import schedule


EXECU_TIME = '11:07'
LOG_FORAMT="[%(asctime)s][%(levelname)s]:%(message)s"
logging.basicConfig(filename='spider.log',level=logging.INFO,format=LOG_FORAMT)


class NasdaqDividendSpilitSpider:
    def __init__(self, *args, **kwargs):
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        #print ("now date is %s" % str(date))
        self.target__url = "https://api.nasdaq.com/api/calendar/dividends?date="+str(self.date)
        #print("target_url = %s" % target__url)
        self.out_file = "Dividend"+str(time.strftime("%Y%m%d",time.localtime()))+".txt"
        self.param_file="./params.txt"
        self.path="./"
        self.params = {}
        self.read_config()
        if("path" in self.params.keys()):
            self.path = self.params['path']
        if("force" in self.params.keys()):
            self.force = self.params['force']
        if("time" in self.params.keys()):
            EXECU_TIME = self.params['time']
    def read_config(self):
        with open(r'./params.txt', "r") as f:
            lines = f.readlines()
            #print (len(lines))
            for line in lines:
                line = line.strip()
                if(line[0]=='#'):
                    continue
                vec=line.split('=')
                if(len(vec)!=2):
                    continue
                self.params[vec[0]]=vec[1]
    
    def curl_job(self):
        print("Curl dividend Start, Now time is %s..." % time.strftime("%H-%M-%S", time.localtime()))
        logging.info("Curl dividend Start...")
        headers={'Accept':'application/json, text/plain, */*',
         'Origin':'https://www.nasdaq.com',
         'Referer':'https://www.nasdaq.com/market-activity/dividends',
         'Sec-Fetch-Mode':'cors',
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        res = requests.get(self.target__url,headers=headers)
        #print (res.status_code)
        if(res.status_code == requests.codes.ok):
            #print (res.text)
            self.parse_json(res.text)
        else:
            res.raise_for_status()
    def parse_json(self,res_json):
        data=json.loads(res_json)
        rows=data['data']['calendar']['rows']
        #print (type(rows))
        if(isinstance(rows, list)):
            for e in rows:
                code_symbol=e['symbol']
                dividend_rate=e['dividend_Rate']
                dividend_Ex_Date=e['dividend_Ex_Date']
   
                #print ('{0}:{1}:{2}'.format(code_symbol,dividend_rate,dividend_Ex_Date))
                print('{0},1,{1}'.format(code_symbol,dividend_rate),file=open(self.out_file,'a+'),flush=True)
        else:
            print("%s has no dividends!!!" % time.strftime("%H-%M-%S", time.localtime()))
            logging.info("no dividends!!!")
def main():
    print("mainnnnnnnnnnnnnnnn...")
    spider = NasdaqDividendSpilitSpider()
    spider.curl_job()
if __name__=="__main__":
    '''
    spider = NasdaqDividendSpilitSpider()
    spider.curl_job()
    '''
    schedule.every().day.at('11:16').do(main)
    while(True):
        schedule.run_pending()
        time.sleep(1)
