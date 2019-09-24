from __future__ import print_function
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


LOG_FORAMT="[%(asctime)s][%(levelname)s]:%(message)s"
logging.basicConfig(filename='spider.log',level=logging.INFO,format=LOG_FORAMT)


class NasdaqDividendSpilitSpider:
    def __init__(self, *args, **kwargs):
        logging.info("Spider init start...")
        self.param_file="./params.txt"
        self.path="./"
        self.exec_time="2030"
        self.params = {}
        self.read_config()
        if("path" in self.params.keys()):
            self.path = self.params['path']+'\\'
        if("force" in self.params.keys()):
            self.force = self.params['force']
        if("time" in self.params.keys()):
            self.exec_time = self.params['time']
        print("params path = %s, force = %s, exec_time = %s" % (str(self.path), str(self.force), str(self.exec_time)))
        logging.info("params path = %s, force = %s, exec_time = %s" % (str(self.path), str(self.force), str(self.exec_time)))
    def read_config(self):
        with open(r'.\params.txt', "r") as f:
            lines = f.readlines()
            #print (len(lines))
            for line in lines:
                line = line.strip()
                if(line[0]=='#'):
                    continue
                vec=line.split('=')
                if(len(vec)!=2):
                    continue
                self.params[vec[0].strip()]=vec[1].strip()
    
    def curl_job(self):
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        #print ("now date is %s" % str(date))
        self.dividend_target__url = "https://api.nasdaq.com/api/calendar/dividends?date="+str(self.date)
        self.split_target_url = "https://api.nasdaq.com/api/calendar/splits?date="+str(self.date)
        print("Curl Start, Now time is %s..." % time.strftime("%Y/%m%d %H-%M-%S", time.localtime()))
        logging.info("Curl Start...")
        self.out_file = "Dividend"+str(time.strftime("%Y%m%d",time.localtime()))+".txt"
        headers={'Accept':'application/json, text/plain, */*',
         'Origin':'https://www.nasdaq.com',
         'Referer':'https://www.nasdaq.com/market-activity/dividends',
         'Sec-Fetch-Mode':'cors',
         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
        res = requests.get(self.dividend_target__url,headers=headers)
        #print (res.status_code)
        if(res.status_code == requests.codes.ok):
            #print (res.text)
            self.parse_json(res.text,1)
        else:
            res.raise_for_status()
        
        res = requests.get(self.split_target_url, headers=headers)
        if(res.status_code == requests.codes.ok):
            #print (res.text)
            self.parse_json(res.text,2)
        else:
            res.raise_for_status()

    def parse_json(self,res_json,url_type):
        data=json.loads(res_json)
        if(url_type == 1):
            rows=data['data']['calendar']['rows']
        else:
            rows=data['data']['rows']
        #print (type(rows))
        if(url_type == 1):
            if(isinstance(rows, list)):
                for e in rows:
                    code_symbol=e['symbol']
                    dividend_rate=e['dividend_Rate']
                    dividend_Ex_Date=e['dividend_Ex_Date']
   
                    #print ('{0}:{1}:{2}'.format(code_symbol,dividend_rate,dividend_Ex_Date))
                    print('{0},1,{1}'.format(code_symbol,dividend_rate),file=open(self.path+self.out_file,'a+'),flush=True)
            else:
                print("%s has no dividends!!!" % time.strftime("%H-%M-%S", time.localtime()))
                logging.info("no dividends!!!")
                print(file=open(self.path+self.out_file,'a+'),flush=True)
        elif(url_type == 2):
            temp_date = time.strftime("%m/%d/%Y", time.localtime())
            #print(temp_date)
            if(isinstance(rows,list)):
                for e in rows:
                    code_symbol=e['symbol']
                    executionDate=e['executionDate']
                    ratio=e['ratio']
                    if (executionDate != temp_date):
                        continue
                    ratio_vec = ratio.split(':')
                    if(len(ratio_vec) == 2):#1:10
                        ratio1 = float(ratio_vec[0])
                        ratio2 = float(ratio_vec[1])
                        split_ratio= ratio1/ratio2
                    elif(len(ratio_vec) == 1):#3.0000%
                        split_ratio=float(ratio[:-1])/100
                    #print('{0},2,{1}'.format(code_symbol, split_ratio),flush=True)
                    print('{0},2,{1}'.format(code_symbol, split_ratio), file=open(self.path + self.out_file, 'a+'), flush=True)
            else:
                logging.info("no split!!!")

if __name__=="__main__":
    spider = NasdaqDividendSpilitSpider()
    if(spider.force != '0' ):
        spider.curl_job()
    schedule.every().day.at(spider.exec_time).do(spider.curl_job)
    while(True):
        schedule.run_pending()
        time.sleep(1)
