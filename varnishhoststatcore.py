# coding: utf-8

import varnishapi,time,datetime,os,re,json,signal
import logging,logging.handlers


class varnishHostStat:
	def Fini(self):
		self.vap.Fini()
	def __init__(self, opts):
		#utils
		#buf -> trx 
		self.buf       = {}
		self.trx       = [{}]
		self.thr       = 10
		self.filter    = False
		self.repl      = False
		self.mode_raw  = False
		self.o_json    = False
		self.log       = False
		self.mode_a    = False
		self.time      = int(time.time())
		self.last      = int(time.time())
		self.error     = ''
		self.field     = 'host: '
		self.exstatus  = {}
		self.header    = ''
		self.useVUT    = 0
		forcevsm       = 0
		
		vops = ['-g','request', '-I', 'ReqAcct,BereqAcct,PipeAcct,ReqHeader,ReqURL,RespStatus,Timestamp:(?i)^([0-9]|https?:/|/|Start: |PipeSess: |Resp: |host: )']
		arg = {}
		
		for o,a in opts:
			if   o == '-i' and a.isdigit():
				self.thr = int(a)
			elif o == '-w':
				lg       = logging.handlers.WatchedFileHandler(a)
				lg.setLevel(logging.INFO)
				lg.setFormatter(logging.Formatter("%(message)s"))
				self.log = logging.getLogger()
				self.log.addHandler(lg)
				self.log.setLevel(logging.INFO)
			elif o == '-r':
				self.mode_raw = True
			elif o == '-a':
				self.mode_a   = True
			elif o == '-j':
				self.o_json = True
			elif o == '-n':
				vops += ['-n', a]
			elif o == '--sopath':
				arg["sopath"] = a
			elif o == '--status':
				spl = a.split(',')
				for status in spl:
					self.exstatus[status] = 0
			elif o == '--vsm':
				forcevsm = 1
			elif o == '--start':
				start      = int(a)
				ns         = datetime.datetime.today().second
				if start > ns:
					wait   = start - ns
				elif start == ns:
					wait   = 0
				else:
					wait   = 60 - ns + start
				if wait > 0:
					self.time += wait
					self.last += wait
					time.sleep(wait)
			elif o == '-F':
				spl = a.split('@' ,2)
				tmp = [a, spl[0]]
				if len(spl) == 2:
					tmp.append(re.compile(spl[1]))
				else:
					tmp.append(False)
				if not self.filter: 
					self.filter = []
				self.filter.append(tmp)
			elif o == '-R':
				if not self.repl:
					self.repl   = []
				# spilit word [/]
				spl = a.split('/', 1)
				
				self.repl.append([
					re.compile(spl[0]),
					spl[1]
					])
			elif o == '-f':
				self.field = a.lower().rstrip(' :') + ': '
		if self.mode_a and not self.filter:
			self.mode_a = False
			print("Disabled -a option. Bacause -F option is not specified.")
		if self.mode_raw:
			self.header = "%-50s | %-11s | %-11s | %-11s | %-13s | %-11s | %-11s | %-11s | %-11s | %-11s |" % ("Host", "req", "fetch", "fetch_time","no_fetch_time","totallen", "2xx","3xx", "4xx", "5xx")
			for status in self.exstatus.keys():
				self.header +=  " %-11s |" % (status+"")
			self.header += "\n"
			self.header += '-' * (179 + len(self.exstatus)* 14) + "|\n"
		else:
			self.header = "%-50s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s |" % ("Host", "Mbps", "rps", "hit", "time/req","(H)time/req", "(M)time/req", "KB/req", "2xx/s", "3xx/s", "4xx/s", "5xx/s")
			for status in self.exstatus.keys():
				self.header +=  " %-11s |" % (status+"/s")
			self.header += "\n"
			self.header += '-' * (205 + len(self.exstatus)* 14) + "|\n"
		self.fieldlen  = len(self.field)
		arg["opt"]   = vops
		if not forcevsm:
			self.__chkUseVUT(arg)
		if self.useVUT:
			self.vap     = varnishapi.VarnishLogVUT(**arg)
		else:
			self.vap     = varnishapi.VarnishLog(**arg)
		
		
		if self.vap.error:
			print(self.vap.error)
			exit(1)
		self.vslutil = varnishapi.VSLUtil()

	def __chkUseVUT(self, _arg):
		arg = {}
		if 'sopath' in _arg:
			arg['sopath'] = _arg['sopath']
		api = varnishapi.VarnishAPI(**arg)
		if api.lva.apiversion >= 2.0:
			self.useVUT = 1

	def executeVSM(self):
		self.state=0
		arg = {
			'cb' : self.vapLineCallBack,
			'groupcb' : self.vapGroupCallBack,
			'maxread' : 0,
		}
		while 1:
			#dispatch
			self.vap.error = ''
			ret = self.vap.Dispatch(**arg)
			if self.vap.error != '':
				self.error = self.vap.error
			if ret == 0:
				time.sleep(0.1);
			self.vapGroupCallBack(None, None)

	def executeVUT(self):
		self.state=0
		arg = {
			'cb' : self.vapLineCallBack,
			'groupcb' : self.vapGroupCallBack,
			'maxread' : 0,
		}
		ret = self.vap.Dispatch(**arg)
		while 1:
			signal.pause()

	def execute(self):
		if self.useVUT:
			self.executeVUT()
		else:
			self.executeVSM()
		
	def makeCmpData(self):
		now   = int(time.time())
		delta = int((now - self.time)/self.thr)
		if delta >= 1:
			tmp   = {}
			total = {}
			while len(self.trx) > 0:
				pl = self.trx.pop(0)
				for host,v in pl.items():
					if host not in tmp:
						tmp[host] = {}
					for key,val in v.items():
						if key not in tmp[host]:
							tmp[host][key] = 0
						tmp[host][key] += val
						if host[0:3] != "[AF":
							if key not in total:
								total[key] = 0
							total[key]     += val
			otime     = self.time
			self.time = now
			if len(total) == 0:
				return {'@start-time':otime, '@end-time':now -1, '@info':''}
			tmp['#alldata']    = total
			tmp['@start-time'] = otime
			tmp['@end-time']   = now -1
			tmp['@info']       = self.error
			self.error = ''
			if self.mode_raw:
				return tmp
			for host, v in tmp.items():
				if host[0] == '@':
					continue
				tmp[host]['mbps']    = float(v['totallen'])     / self.thr  * 8 / 1024 / 1024
				tmp[host]['rps']     = float(v['req'])          / self.thr
				if v['req'] > 0:
					tmp[host]['hit']                = (1 - float(v['fetch'])     / v['req']) * 100
					tmp[host]['avg_fsize']          = float(v['totallen'])       / v['req']  / 1024
					tmp[host]['avg_time']           = (float(v['no_fetch_time']) + v['fetch_time']) / v['req']
				else:
					tmp[host]['hit']                = 0.0
					tmp[host]['avg_fsize']          = 0.0
					tmp[host]['avg_time']           = 0.0
				if v['req'] - v['fetch'] > 0:
					tmp[host]['avg_not_fetch_time'] = float(v['no_fetch_time'])  / (v['req'] - v['fetch'])
				else:
					tmp[host]['avg_not_fetch_time'] = 0.0
				if v['fetch'] > 0:
					tmp[host]['avg_fetch_time']     = float(v['fetch_time'])     / v['fetch']
				else:
					tmp[host]['avg_fetch_time']     = 0.0
				tmp[host]['avg_2xx']    = float(v['2xx'])          / self.thr
				tmp[host]['avg_3xx']    = float(v['3xx'])          / self.thr
				tmp[host]['avg_4xx']    = float(v['4xx'])          / self.thr
				tmp[host]['avg_5xx']    = float(v['5xx'])          / self.thr
				for status in self.exstatus.keys():
					tmp[host]['avg_' + status]    = float(v[status])          / self.thr
			return tmp
		else:
			while len(self.trx) -1 < delta:
				self.trx.append({})
			
	def outTxt(self,txt):
		if self.log:
			self.log.info(txt)
		else:
			if not self.o_json:
				os.system('clear')
			print(txt)

	def txtCmp(self,cmp):
		if self.o_json:
			return json.dumps(cmp, ensure_ascii=False)
		else:
			ret = ''
			ret+= "%s - %s (interval:%d) %s\n" % (datetime.datetime.fromtimestamp(cmp['@start-time']), datetime.datetime.fromtimestamp(cmp['@end-time']), self.thr, cmp['@info'])
			ret+= self.header
			if self.mode_raw:
				for host in sorted(cmp.keys()):
					if host[0] == '@':
						continue
					v = cmp[host]
					val = {'host':host, 'req':v['req'], 'fetch':v['fetch'], 'fetch_time':v['fetch_time'],'no_fetch_time':v['no_fetch_time'], 'totallen':v['totallen'], '2xx':v['2xx'], '3xx':v['3xx'], '4xx':v['4xx'], '5xx':v['5xx']}
					suf = ''
					for status in self.exstatus.keys():
						val[status] = v[status]
						suf+="| %("+status+")11d "
					ret+= ("%(host)-50s | %(req)11d | %(fetch)11d | %(fetch_time)11f | %(no_fetch_time)13f | %(totallen)11d | %(2xx)11d | %(3xx)11d | %(4xx)11d | %(5xx)11d "+suf+"|\n") % val 
			else:
				for host in sorted(cmp.keys()):
					if host[0] == '@':
						continue
					v = cmp[host]
					val = {'host':host, 'mbps':v['mbps'], 'rps':v['rps'], 'hit':v['hit'], 'avg_time':v['avg_time'], 'avg_not_fetch_time':v['avg_not_fetch_time'], 'avg_fetch_time':v['avg_fetch_time'], 'avg_fsize':v['avg_fsize'], 'avg_2xx':v['avg_2xx'], 'avg_3xx':v['avg_3xx'], 'avg_4xx':v['avg_4xx'], 'avg_5xx':v['avg_5xx']}
					suf = ''
					for status in self.exstatus.keys():
						val['avg_'+ status] = v['avg_'+ status]
						suf+="| %(avg_"+status+")11f "
					ret+= ("%(host)-50s | %(mbps)-11f | %(rps)11f | %(hit)11f | %(avg_time)11f | %(avg_not_fetch_time)11f | %(avg_fetch_time)11f | %(avg_fsize)11f | %(avg_2xx)11f | %(avg_3xx)11f | %(avg_4xx)11f | %(avg_5xx)11f "+suf+"|\n") % val
			return ret
			


	def chkFilter(self, forceHost=False, Prefix='[F'):
		if not self.filter or forceHost:
			return self.buf['Host']
		i = 0
		for v in self.filter:
			i   += 1
			host = v[1]
			reg  = v[2]
			if self.buf['Host'].endswith(host) and (not reg or reg.match(self.buf['url'])):
				return Prefix + str(i) + ']' + v[0]

	def appendTrx(self, host,  delta):
		if delta < 0 or not host:
			return

		while len(self.trx) -1 < delta:
			self.trx.append({})
		if host not in self.trx[delta]:
			self.trx[delta][host] = {'req':0, 'fetch':0, 'fetch_time':0.0,'no_fetch_time':0, 'totallen':0,'2xx':0,'3xx':0,'4xx':0,'5xx':0}
			self.trx[delta][host].update(self.exstatus)

		self.trx[delta][host]['req']          += 1
		self.trx[delta][host]['totallen']     += self.buf['RespLength']

		status = self.buf['status']
		
		if status >= 200:
			if   status < 300:
				self.trx[delta][host]['2xx'] += 1
			elif status < 400:
				self.trx[delta][host]['3xx'] += 1
			elif status < 500:
				self.trx[delta][host]['4xx'] += 1
			elif status < 600:
				self.trx[delta][host]['5xx'] += 1
		if str(status) in self.exstatus:
			self.trx[delta][host][str(status)] += 1

		if self.buf['fetch']:
			self.trx[delta][host]['fetch_time']    += self.buf['worktime']
			self.trx[delta][host]['fetch']         += 1
		else:
			self.trx[delta][host]['no_fetch_time'] += self.buf['worktime']

	def vapGroupCallBack(self, vap, prv):
		cmp = self.makeCmpData()
		if cmp:
			txt = self.txtCmp(cmp)
			self.outTxt(txt)
		if self.state == 1:
			delta = int((self.buf['time'] - self.time) / self.thr)
			if self.mode_a:
				self.appendTrx(self.chkFilter(True)  , delta)
				self.appendTrx(self.chkFilter(False,'[AF')  , delta)
			else:
				self.appendTrx(self.chkFilter()  , delta)
		self.state = 0
		
	def vapLineCallBack(self, vap, cbd, prv):
		ttag = vap.VSL_tags[cbd['tag']]
		data = cbd['data'].strip('\0')
		
		if self.state == 0:
			#initialize
			self.state = 1
			self.buf = {'Host':'#n/a','url':'', 'ReqLength':0,'RespLength':0,'BereqLength':0,'BerespLength':0,'url':'','status':0,'req':0,'fetch':0,'pipe':0,'time':0.0,'worktime':0.0}
		
		if   ttag == 'Timestamp':
			if   cbd['level'] == 1 and data[:7] == 'Start: ':
				self.buf['req'] = self.buf['req']+1
			
			elif data[:6] == 'Resp: ' or data[:10] == 'PipeSess: ':
				spl = data.split(' ')
				self.buf['time']     = float(spl[1])
				self.buf['worktime'] = float(spl[3])
		elif ttag == 'ReqURL' and self.buf['url']=='':
			self.buf['url'] = data
		elif ttag == 'ReqHeader' and data[:self.fieldlen].lower() == self.field:
			self.buf['Host'] = data[self.fieldlen:]
			if self.repl:
				for r in self.repl:
					tmp = r[0].sub(r[1], self.buf['Host'])
					if tmp != self.buf['Host']:
						self.buf['Host'] = tmp
						break
		elif ttag == 'RespStatus':
			self.buf['status'] = int(data)
		elif ttag == 'ReqAcct':
			spl = data.split(' ')
			self.buf['ReqLength']  = int(spl[2])
			self.buf['RespLength'] = int(spl[5])
		elif ttag == 'BereqAcct':
			spl = data.split(' ')
			self.buf['BereqLength']  += int(spl[2])
			self.buf['BerespLength'] += int(spl[5])
			self.buf['fetch']        += 1
		elif ttag == 'PipeAcct':
			spl = data.split(' ')
			self.buf['ReqLength']    = int(spl[0])
			self.buf['BereqLength']  = int(spl[1]) + int(spl[2])
			self.buf['BerespLength'] = int(spl[3])
			self.buf['RespLength']   = int(spl[3])
			self.buf['pipe']        += 1
		return 0

