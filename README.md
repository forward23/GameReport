# Test task.
![alt text](https://github.com/forward23/GameReport/blob/main/Test_task.pdf)

###How to launch:

1) extract archive
2) cd <folder> (in terminal)
3) pipenv install - (install dependencies)
4) pipenv shell (activate pipenv shell)
5) python report.py -h  (help for this script): 
usage: report.py [-h] [-S] [-E] [-C]

Making report: LTV growth of daily player cohorts by days of life

optional arguments:
  -h, --help        show this help message and exit
  -S , --start      start date in format yyyy-mm-dd
  -E , --end        end date in format yyyy-mm-dd
  -C , --currency   currency for report: EUR (default) | USD | RUB

### EXAMPLE1: (DEFAULT VALUES) python report.py
start 2021-01-01  
end YESTERDAY  
currency EUR   

### EXAMPLE2: python report.py -S 2021-05-01 -E 2021-05-10 -C USD
start 2021-05-01   
end 2021-05-10  
currency USD

### RESULT: 
two files report_gross_<currency>.csv, report_net_<currency>.csv