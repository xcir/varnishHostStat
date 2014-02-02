================
varnishhoststat
================


-----------------------------------------------------------
Display to the Statistics for each domain or url-pattern
-----------------------------------------------------------

:Author: Shohei Tanaka(@xcir)
:Date: 2014-02-02
:Version: 0.1
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

  date: 2014/02/02 12:10:00 interval: 5
  Host                                               | Mbps        | rps         | hit         | time/req    | (H)time/req | (M)time/req | KB/req      | 2xx/s       | 3xx/s       | 4xx/s       | 5xx/s
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  #alldata                                           | 0.000938    | 1.800000    | 22.222222   | 0.000905    | 0.000103    | 0.001134    | 0.066732    | 1.400000    | 0.000000    | 0.400000    | 0.000000
  example.net                                        | 0.000038    | 1.000000    | 0.000000    | 0.001236    | 0.000000    | 0.001236    | 0.004883    | 1.000000    | 0.000000    | 0.000000    | 0.000000
  example2.net                                       | 0.000015    | 0.400000    | 0.000000    | 0.000878    | 0.000000    | 0.000878    | 0.004883    | 0.400000    | 0.000000    | 0.000000    | 0.000000
  example3.net                                       | 0.000885    | 0.400000    | 100.000000  | 0.000103    | 0.000103    | 0.000000    | 0.283203    | 0.000000    | 0.000000    | 0.400000    | 0.000000

Group by url-pattern (varnishhoststat.py -i 5 -F "example.net@^/img/" -F "example.net@^/css/" -F "example.net")
--------------------------------------------------------------------------------------------------------------------------
::

  date: 2014/02/02 12:14:32 interval: 5
  Host                                               | Mbps        | rps         | hit         | time/req    | (H)time/req | (M)time/req | KB/req      | 2xx/s       | 3xx/s       | 4xx/s       | 5xx/s
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  #alldata                                           | 0.002698    | 1.600000    | 75.000000   | 0.000339    | 0.000101    | 0.001053    | 0.215820    | 0.400000    | 0.000000    | 1.200000    | 0.000000
  [F1]example.net@^/img/                             | 0.001788    | 0.800000    | 100.000000  | 0.000095    | 0.000095    | 0.000000    | 0.286133    | 0.000000    | 0.000000    | 0.800000    | 0.000000
  [F2]example.net@^/css/                             | 0.000894    | 0.400000    | 100.000000  | 0.000112    | 0.000112    | 0.000000    | 0.286133    | 0.000000    | 0.000000    | 0.400000    | 0.000000
  [F3]example.net                                    | 0.000015    | 0.400000    | 0.000000    | 0.001053    | 0.000000    | 0.001053    | 0.004883    | 0.400000    | 0.000000    | 0.000000    | 0.000000

OUTPUT FORMAT
==============
::

  date: [time] interval: [interval time]
  Host                    | Mbps                 | rps             | hit      | time/req              | (H)time/req                             | (M)time/req                            | KB/req                     | 2xx/s                 | 3xx/s                 | 4xx/s                 | 5xx/s
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Host or filter rule     | Traffic (w/o header) | Request Per Sec | Hit per  | Average response time | Average response time by hit request    |  Average response time by miss request | average response body size | HTTP status 2xx rate  | HTTP status 3xx rate  | HTTP status 4xx rate  | HTTP status 5xx rate
  
  * hit rate
    Decision as follows:
    Fetch to backend = Miss
    Not fetch        = Hit

OPTION
===========
::

  -i [interval] -F [filter pattern]
  
-i [interval]
----------------
Specify interval second.
Default is 10 second.

example
#########
::

  #10 second
  -i 10

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

