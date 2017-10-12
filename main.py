# coding: utf-8
import subprocess
import time

std_fp = open('spider.log', 'a')
err_fp = open('spider_err.log', 'a')
# 获取小区的房价
cmd1 = 'scrapy crawl fangtx'
print cmd1
p = subprocess.Popen(cmd1, stdout=std_fp, stderr=err_fp, shell=True)
p.communicate()
p.wait()
time.sleep(120)

# 获取小区的租金
'''
cmd2 = 'scrapy crawl fangtx_rent'
print cmd2
p = subprocess.Popen(cmd2, stdout=std_fp, stderr=err_fp, shell=True)
p.communicate()
p.wait()
time.sleep(120)
'''
std_fp.close()
err_fp.close()
