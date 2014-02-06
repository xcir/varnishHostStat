================
varnishhoststat
================


-----------------------------------------------------------
Display to the Statistics for each domain or url-pattern
-----------------------------------------------------------

:Author: Shohei Tanaka(@xcir)
:Date: 2014-02-06
:Version: 0.5
:Manual section: 1

DESCRIPTION
===========
Display to the Statistics for each domain or url-pattern

ATTENTION
===========
This script use to high cpu power.
Is half cpu usage as compared with the varnishd in my environment.


SAMPLE
===========
Group by host (varnishhoststat.py -i 5)
----------------------------------------------------
::

  2014-02-03 23:13:00 - 2014-02-03 23:13:05 (interval:5)
  Host                                               | Mbps        | rps         | hit         | time/req    | (H)time/req | (M)time/req | KB/req      | 2xx/s       | 3xx/s       | 4xx/s       | 5xx/s       |
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  #alldata                                           | 0.000031    |    0.800000 |    0.000000 |    0.001085 |    0.000000 |    0.001085 |    0.004883 |    0.800000 |    0.000000 |    0.000000 |    0.000000 |
  example.net                                        | 0.000015    |    0.400000 |    0.000000 |    0.000933 |    0.000000 |    0.000933 |    0.004883 |    0.400000 |    0.000000 |    0.000000 |    0.000000 |
  hoge.example.net                                   | 0.000015    |    0.400000 |    0.000000 |    0.001237 |    0.000000 |    0.001237 |    0.004883 |    0.400000 |    0.000000 |    0.000000 |    0.000000 |

Group by url-pattern (varnishhoststat.py -i 5 -F "example.net@^/img/" -F "example.net@^/css/" -F "example.net")
--------------------------------------------------------------------------------------------------------------------------
::

  2014-02-03 23:14:19 - 2014-02-03 23:14:23 (interval:5)
  Host                                               | Mbps        | rps         | hit         | time/req    | (H)time/req | (M)time/req | KB/req      | 2xx/s       | 3xx/s       | 4xx/s       | 5xx/s       |
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  #alldata                                           | 0.001808    |    1.800000 |   44.444444 |    0.000583 |    0.000119 |    0.000954 |    0.128581 |    1.000000 |    0.000000 |    0.800000 |    0.000000 |
  [F1]example.net@^/img/                             | 0.000885    |    0.400000 |  100.000000 |    0.000110 |    0.000110 |    0.000000 |    0.283203 |    0.000000 |    0.000000 |    0.400000 |    0.000000 |
  [F2]example.net@^/css/                             | 0.000885    |    0.400000 |  100.000000 |    0.000127 |    0.000127 |    0.000000 |    0.283203 |    0.000000 |    0.000000 |    0.400000 |    0.000000 |
  [F3]example.net                                    | 0.000038    |    1.000000 |    0.000000 |    0.000954 |    0.000000 |    0.000954 |    0.004883 |    1.000000 |    0.000000 |    0.000000 |    0.000000 |

Raw-data output (varnishhoststat.py -r)
----------------------------------------------------
::

  2014-02-03 23:26:48 - 2014-02-03 23:26:57 (interval:10)
  Host                                               | req         | fetch       | fetch_time  | no_fetch_time | totallen    | 2xx         | 3xx         | 4xx         | 5xx         |
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  #alldata                                           |          23 |          14 |    0.012728 |      0.000753 |        2680 |          14 |           0 |           9 |           0 |
  example.net                                        |          18 |           9 |    0.008177 |      0.000753 |        2655 |           9 |           0 |           9 |           0 |
  hoge.example.net                                   |           5 |           5 |    0.004551 |      0.000000 |          25 |           5 |           0 |           0 |           0 |

JSON-format output (varnishhoststat.py -j)
----------------------------------------------------
::

  {"hoge.example.net": {"avg_fsize": 0.0048828125, "rps": 0.5, "avg_not_fetch_time": 0.0, "hit": 0.0, "avg_fetch_time": 0.00086789131164550777, "fetch_time": 0.0043394565582275391, "2xx": 5, "avg_2xx": 0.5, "mbps": 1.9073486328125e-05, "req": 5, "5xx": 0, "avg_3xx": 0.0, "no_fetch_time": 0, "totallen": 25, "4xx": 0, "3xx": 0, "avg_time": 0.00086789131164550777, "avg_5xx": 0.0, "fetch": 5, "avg_4xx": 0.0}, "#alldata": {"avg_fsize": 0.1162109375, "rps": 2.5, "avg_not_fetch_time": 8.5520744323730466e-05, "hit": 40.0, "avg_fetch_time": 0.0009458700815836589, "fetch_time": 0.014188051223754883, "2xx": 15, "avg_2xx": 1.5, "mbps": 0.002269744873046875, "req": 25, "5xx": 0, "avg_3xx": 0.0, "no_fetch_time": 0.00085520744323730469, "totallen": 2975, "4xx": 10, "3xx": 0, "avg_time": 0.00060173034667968753, "avg_5xx": 0.0, "fetch": 15, "avg_4xx": 1.0}, "example.net": {"avg_fsize": 0.14404296875, "rps": 2.0, "avg_not_fetch_time": 8.5520744323730466e-05, "hit": 50.0, "avg_fetch_time": 0.00098485946655273442, "fetch_time": 0.0098485946655273438, "2xx": 10, "avg_2xx": 1.0, "mbps": 0.00225067138671875, "req": 20, "5xx": 0, "avg_3xx": 0.0, "no_fetch_time": 0.00085520744323730469, "totallen": 2950, "4xx": 10, "3xx": 0, "avg_time": 0.00053519010543823242, "avg_5xx": 0.0, "fetch": 10, "avg_4xx": 1.0}, "@start-time": 1391437481, "@end-time": 1391437490}
  {"hoge.example.net": {"avg_fsize": 0.0048828125, "rps": 0.5, "avg_not_fetch_time": 0.0, "hit": 0.0, "avg_fetch_time": 0.00083451271057128902, "fetch_time": 0.0041725635528564453, "2xx": 5, "avg_2xx": 0.5, "mbps": 1.9073486328125e-05, "req": 5, "5xx": 0, "avg_3xx": 0.0, "no_fetch_time": 0, "totallen": 25, "4xx": 0, "3xx": 0, "avg_time": 0.00083451271057128902, "avg_5xx": 0.0, "fetch": 5, "avg_4xx": 0.0}, "#alldata": {"avg_fsize": 0.1162109375, "rps": 2.5, "avg_not_fetch_time": 8.2373619079589844e-05, "hit": 40.0, "avg_fetch_time": 0.00090791384379069009, "fetch_time": 0.013618707656860352, "2xx": 15, "avg_2xx": 1.5, "mbps": 0.002269744873046875, "req": 25, "5xx": 0, "avg_3xx": 0.0, "no_fetch_time": 0.00082373619079589844, "totallen": 2975, "4xx": 10, "3xx": 0, "avg_time": 0.00057769775390624999, "avg_5xx": 0.0, "fetch": 15, "avg_4xx": 1.0}, "example.net": {"avg_fsize": 0.14404296875, "rps": 2.0, "avg_not_fetch_time": 8.2373619079589844e-05, "hit": 50.0, "avg_fetch_time": 0.00094461441040039062, "fetch_time": 0.0094461441040039062, "2xx": 10, "avg_2xx": 1.0, "mbps": 0.00225067138671875, "req": 20, "5xx": 0, "avg_3xx": 0.0, "no_fetch_time": 0.00082373619079589844, "totallen": 2950, "4xx": 10, "3xx": 0, "avg_time": 0.00051349401473999023, "avg_5xx": 0.0, "fetch": 10, "avg_4xx": 1.0}, "@start-time": 1391437491, "@end-time": 1391437500}

Raw-data output by JSON-format(varnishhoststat.py -r -j)
----------------------------------------------------
::

  {"hoge.example.net": {"fetch_time": 0.0037126541137695312, "2xx": 4, "req": 4, "5xx": 0, "no_fetch_time": 0, "totallen": 20, "4xx": 0, "3xx": 0, "fetch": 4}, "#alldata": {"fetch_time": 0.01218414306640625, "2xx": 13, "req": 23, "5xx": 0, "no_fetch_time": 0.00090909004211425781, "totallen": 2965, "4xx": 10, "3xx": 0, "fetch": 13}, "example.net": {"fetch_time": 0.0084714889526367188, "2xx": 9, "req": 19, "5xx": 0, "no_fetch_time": 0.00090909004211425781, "totallen": 2945, "4xx": 10, "3xx": 0, "fetch": 9}, "@start-time": 1391437527, "@end-time": 1391437536}
  {"hoge.example.net": {"fetch_time": 0.0052282810211181641, "2xx": 5, "req": 5, "5xx": 0, "no_fetch_time": 0, "totallen": 25, "4xx": 0, "3xx": 0, "fetch": 5}, "#alldata": {"fetch_time": 0.013852119445800781, "2xx": 15, "req": 25, "5xx": 0, "no_fetch_time": 0.00098705291748046875, "totallen": 2975, "4xx": 10, "3xx": 0, "fetch": 15}, "example.net": {"fetch_time": 0.0086238384246826172, "2xx": 10, "req": 20, "5xx": 0, "no_fetch_time": 0.00098705291748046875, "totallen": 2950, "4xx": 10, "3xx": 0, "fetch": 10}, "@start-time": 1391437537, "@end-time": 1391437546}

OUTPUT FORMAT
==============
::

  -Default
  
  [start-time] - [end-time] (interval:[interval time])
  Host                    | Mbps                 | rps             | hit      | time/req              | (H)time/req                             | (M)time/req                            | KB/req                     | 2xx/s                 | 3xx/s                 | 4xx/s                 | 5xx/s
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Host or filter rule     | Traffic (w/o header) | Request Per Sec | Hit per  | Average response time | Average response time by hit request    |  Average response time by miss request | average response body size | HTTP status 2xx rate  | HTTP status 3xx rate  | HTTP status 4xx rate  | HTTP status 5xx rate
  
  * hit rate
    Decision as follows:
    Fetch to backend = Miss
    Not fetch        = Hit
  
  -Raw
  [start-time] - [end-time] (interval:[interval time])
  Host                 | req           | fetch       | fetch_time                   | no_fetch_time         | totallen                 | 2xx                    | 3xx                    | 4xx                    | 5xx                    |
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  Host or filter rule  | Request count | Fetch count | Total time(fetch to backend) | Total time(not fetch) | Total transfer body size | HTTP-status count(2xx) | HTTP-status count(3xx) | HTTP-status count(4xx) | HTTP-status count(5xx) |
  

OPTION
===========
::

  -r -j -i [interval] -F [filter pattern] --start [second] -w [file-name]
  
-r
----------------
Raw data(no summarize)

-j
----------------
Output json format

-i [interval]
----------------
Specify interval second.
Default is 10 second.

example
#########
::

  #10 second
  -i 10

-D
------------------
Daemonize.

-P [pid-file]
------------------
Write the process's PID to the specified file.(require -D option)

-F [host@url-pattern]
--------------------------------
Specify filter pattern.
Statistics for each domain separately ,if you do not  specified.

example
#########
::

  #Filter by example.net (ends-with match)
  #This pattern is match to a.example.net and b.example.net and example.net
  -F example.net
  
  #Filter by example.net^/img/[0-9]
  #This pattern is match to a.example.net/img/0 and b.example.net/img/1 and example.net/img/2
  -F "example.net@^/img/[0-9]"
  
  #Filter by example.net^/img/[0-9] and other example.net
  -F "example.net@^/img/[0-9]" -F example.net
  
  #Bad pattern
  #Not match to example.net@^/img/[0-9]
  -F example.net -F "example.net@^/img/[0-9]" 

-w [file-name]
--------------------------------
Specify write log file-name.
Move log file ,if you want rotation. (Don't send HUP)

--start [second]
------------------
Fix starting time.

HISTORY
===========

Version 0.5: Support -D -P option

Version 0.4: Support -w option

Version 0.3: Support --start option, Bugfix

Version 0.2: Support -r -j option

Version 0.1: First version
