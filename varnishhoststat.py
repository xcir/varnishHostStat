# coding: utf-8

import varnishapi,time,datetime,os,sys,getopt,re,json

def main():
	smp = varnishHostStat()
	smp.execute()

class varnishHostStat:
	def __init__(self):
		#utils
		#buf -> trx 
		self.buf       = {}
		self.trx       = [{}]
		self.thr       = 10
		self.filter    = False
		self.mode_raw  = False
		self.o_json    = False
		self.start     = False
		#opt
		try:
			opts,args = getopt.getopt(sys.argv[1:],"jrF:i:",["start="])
		except getopt.GetoptError:
			print 'param err'
			sys.exit(2)
		for o,a in opts:
			if   o == '-i' and a.isdigit():
				self.thr = int(a)
			elif o == '-r':
				self.mode_raw = True
			elif o == '-j':
				self.o_json = True
			elif o == '--start':
				self.start = int(a)
				ns         = datetime.datetime.today().second
				if self.start > ns:
					wait   = self.start - ns
				else:
					wait   = 60 - ns + self.start
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

		self.time    = int(time.time())
		self.vap     = varnishapi.VarnishAPI(['-c', '-i', 'Length,RxHeader,RxUrl,TxStatus,ReqEnd,ReqStart,VCL_Call', '-I', '^([0-9]+$|Host:|/|[0-9\. ]+$|[a-z]+$)'])
		self.vslutil = varnishapi.VSLUtil()
	

	def execute(self):
		while 1:
			#dispatch
			self.vap.VSL_NonBlockingDispatch(self.vapCallBack)
			cmp = self.makeCmpData()
			if cmp:
				self.printCmp(cmp)

			time.sleep(0.1)

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
						if key not in total:
							total[key] = 0
						tmp[host][key] += val
						total[key]     += val
			otime     = self.time
			self.time = now
			if len(total) == 0:
				return {'@start-time':otime, '@end-time':now -1}
				#return False
			tmp['#alldata']    = total
			tmp['@start-time'] = otime
			tmp['@end-time']   = now -1
			if self.mode_raw:
				return tmp
			for host, v in tmp.items():
				if host[0] == '@':
					continue
				tmp[host]['mbps']    = float(v['totallen'])     / self.thr  * 8 / 1024 / 1024
				tmp[host]['rps']     = float(v['req'])          / self.thr
				if v['req'] > 0:
					tmp[host]['hit']                = (1 - float(v['fetch'])   / v['req']) * 100
					tmp[host]['avg_fsize']          = float(v['totallen'])     / v['req']  / 1024
					tmp[host]['avg_time']           = (float(v['no_fetch_time']) + v['fetch_time']) / v['req']
				else:
					tmp[host]['hit']                = 0.0
					tmp[host]['avg_fsize']          = 0.0
					tmp[host]['avg_time']           = 0.0
				if v['req'] - v['fetch'] > 0:
					tmp[host]['avg_not_fetch_time'] = float(v['no_fetch_time']) / (v['req'] - v['fetch'])
				else:
					tmp[host]['avg_not_fetch_time'] = 0.0
				if v['fetch'] > 0:
					tmp[host]['avg_fetch_time']     = float(v['fetch_time'])   / v['fetch']
				else:
					tmp[host]['avg_fetch_time']     = 0.0
				tmp[host]['avg_2xx']    = float(v['2xx'])          / self.thr
				tmp[host]['avg_3xx']    = float(v['3xx'])          / self.thr
				tmp[host]['avg_4xx']    = float(v['4xx'])          / self.thr
				tmp[host]['avg_5xx']    = float(v['5xx'])          / self.thr
			return tmp
		else:
			while len(self.trx) -1 < delta:
				self.trx.append({})
			

	def printCmp(self,cmp):
		if self.o_json:
			print json.dumps(cmp)
		else:
			os.system('clear')
			print str(datetime.datetime.fromtimestamp(cmp['@start-time'])) + ' - ' + str(datetime.datetime.fromtimestamp(cmp['@end-time'])) + ' (interval:'+ str(self.thr) +')'
			if self.mode_raw:
				print "%-50s | %-11s | %-11s | %-11s | %-13s | %-11s | %-11s | %-11s | %-11s | %-11s |" % ("Host", "req", "fetch", "fetch_time","no_fetch_time","totallen", "2xx","3xx", "4xx", "5xx")
				print '-' * 179 + '|'
				for host in sorted(cmp.keys()):
					if host[0] == '@':
						continue
					v = cmp[host]
					print "%-50s | %11d | %11d | %11f | %13f | %11d | %11d | %11d | %11d | %11d |" % (host, v['req'], v['fetch'], v['fetch_time'],v['no_fetch_time'], v['totallen'], v['2xx'], v['3xx'], v['4xx'], v['5xx'] )
			else:
				print "%-50s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s |" % ("Host", "Mbps", "rps", "hit", "time/req","(H)time/req", "(M)time/req", "KB/req", "2xx/s", "3xx/s", "4xx/s", "5xx/s")
				print '-' * 205 + '|'
				for host in sorted(cmp.keys()):
					if host[0] == '@':
						continue
					v = cmp[host]
					print "%-50s | %-11f | %11f | %11f | %11f | %11f | %11f | %11f | %11f | %11f | %11f | %11f |" % (host, v['mbps'], v['rps'], v['hit'], v['avg_time'], v['avg_not_fetch_time'], v['avg_fetch_time'], v['avg_fsize'], v['avg_2xx'], v['avg_3xx'], v['avg_4xx'], v['avg_5xx'])

			




	def chkFilter(self, dat):
		if not self.filter:
			return dat['Host']
		i = 0
		for v in self.filter:
			i += 1
			host = v[1]
			reg  = v[2]
			if dat['Host'].endswith(host) and (not reg or reg.match(dat['url'])):
				return '[F' + str(i) + ']' + v[0]


	def vapCallBack(self, priv, tag, fd, length, spec, ptr, bm):
		if spec == 0:
			return

		nml = self.vap.normalizeDic(priv, tag, fd, length, spec, ptr, bm)
		ntag = nml['tag']
		nfd  = str(nml['fd'])
		nmsg = nml['msg']

		if   ntag == 'ReqStart':
			self.buf[nfd] = {'Host':'#n/a', 'Length':0,'url':'','status':0,'fetch':0,'time':0.0,'worktime':0.0}
		elif ntag == 'ReqEnd':
			spl = nmsg.split(' ',4)
			self.buf[nfd]['worktime']   = float(spl[2]) - float(spl[1])
			self.buf[nfd]['time']       = int(float(spl[2])) #EndTime
			delta                       = int((self.buf[nfd]['time'] - self.time) / self.thr)
			

			if delta >= 0:
				host = self.chkFilter(self.buf[nfd])
				if host:
					while len(self.trx) -1 < delta:
						self.trx.append({})
					#host = self.buf[nfd]['Host']
					if host not in self.trx[delta]:
						self.trx[delta][host] = {'req':0, 'fetch':0, 'fetch_time':0.0,'no_fetch_time':0, 'totallen':0,'2xx':0,'3xx':0,'4xx':0,'5xx':0}
					self.trx[delta][host]['req']          += 1
					self.trx[delta][host]['totallen']     += self.buf[nfd]['Length']
					status = self.buf[nfd]['status']
					if   status >= 200 and status < 300:
						self.trx[delta][host]['2xx'] += 1
					elif status >= 300 and status < 400:
						self.trx[delta][host]['3xx'] += 1
					elif status >= 400 and status < 500:
						self.trx[delta][host]['4xx'] += 1
					elif status >= 500 and status < 600:
						self.trx[delta][host]['5xx'] += 1

					if self.buf[nfd]['fetch']:
						self.trx[delta][host]['fetch_time']   += self.buf[nfd]['worktime']
						self.trx[delta][host]['fetch']        += 1
					else:
						self.trx[delta][host]['no_fetch_time'] += self.buf[nfd]['worktime']

			#else:
			#	print 'delay:'
			del self.buf[nfd]
		elif nfd in self.buf:
			if ntag == 'Length':
				self.buf[nfd]['Length'] = int(nmsg)
			elif ntag == 'RxHeader':
				self.buf[nfd]['Host']   = nmsg.split(':', 2)[1].strip()
			elif ntag == 'RxURL':
				self.buf[nfd]['url']    = nmsg
			elif ntag == 'TxStatus':
				self.buf[nfd]['status'] = int(nmsg)
			elif ntag == 'VCL_call' and nmsg == 'fetch':
				self.buf[nfd]['fetch']  = 1 




main()


