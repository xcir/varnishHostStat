# coding: utf-8

import varnishapi,time,datetime,os,sys,getopt,re

def main():
	smp = varnishHostStat()
	smp.execute()

class varnishHostStat:
	def __init__(self):
		#connect varnishapi
		self.vap     = varnishapi.VarnishAPI(['-c', '-i', 'Length,RxHeader,RxUrl,TxStatus,ReqEnd,ReqStart,VCL_Call', '-I', '^([0-9]+$|Host:|/|[0-9\. ]+$|[a-z]+$)'])

		#utils
		#buf -> trx 
		self.buf       = {}
		self.trx       = [{}]
		self.time      = int(time.time())
		self.vslutil   = varnishapi.VSLUtil()
		self.thr       = 10
		self.filter    = False

		#opt
		try:
			opts,args = getopt.getopt(sys.argv[1:],"F:i:")
		except getopt.GetoptError:
			print 'param err'
			sys.exit(2)
		for o,a in opts:
			if   o == '-i' and a.isdigit():
				self.thr = int(a)
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

	

	def execute(self):
		while 1:
			#dispatch
			self.vap.VSL_NonBlockingDispatch(self.vapCallBack)
			cmp = self.makeCmpData()
			if cmp:
				self.printCmp(cmp)

			time.sleep(0.1)

	def makeCmpData(self):
		now = int(time.time())
		#if now - self.time >= self.thr:
		if len(self.trx) > self.thr:
			tmp   = {}
			total = {}
			while len(self.trx) > 1:
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
			self.time = now
			if len(total) == 0:
				return False
			tmp['#alldata'] = total
			return tmp

	def printCmp(self,cmp):
		tmp = {}
		print cmp
		for host,v in cmp.items():
			tmp[host] = {'bps':0.0, 'rps':0.0, 'hit':0.0, 'aftime':0.0, 'anftime':0.0,'atime':0.0, 'asize':0.0, 'a2xx':0.0, 'a3xx':0.0, 'a4xx':0.0, 'a5xx':0.0}
			tmp[host]['mbps']    = float(v['totallen'])     / self.thr  * 8 / 1024 / 1024
			tmp[host]['rps']     = float(v['req'])          / self.thr
			if v['req'] > 0:
				tmp[host]['hit']     = (1 - float(v['fetch'])   / v['req']) * 100
				tmp[host]['akb']     = float(v['totallen'])     / v['req']  / 1024
				tmp[host]['atime']   = (float(v['nofetch_time']) + v['fetch_time']) / v['req']
			if v['req'] - v['fetch'] > 0:
				tmp[host]['anftime'] = float(v['nofetch_time']) / (v['req'] - v['fetch'])
			if v['fetch'] > 0:
				tmp[host]['aftime']  = float(v['fetch_time'])   / v['fetch']
			tmp[host]['a2xx']    = float(v['2xx'])          / self.thr
			tmp[host]['a3xx']    = float(v['3xx'])          / self.thr
			tmp[host]['a4xx']    = float(v['4xx'])          / self.thr
			tmp[host]['a5xx']    = float(v['5xx'])          / self.thr
		os.system('clear')
		print time.strftime("date: %Y/%m/%d %H:%M:%S interval: " + str(self.thr))
		print "%-50s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s | %-11s" % ("Host", "Mbps", "rps", "hit", "time/req","(H)time/req", "(M)time/req", "KB/req", "2xx/s", "3xx/s", "4xx/s", "5xx/s")
		print '-' * 200
		for host in sorted(tmp.keys()):
			v = tmp[host]
			print "%-50s | %-11f | %-11f | %-11f | %-11f | %-11f | %-11f | %-11f | %-11f | %-11f | %-11f | %-11f" % (host, v['mbps'], v['rps'], v['hit'], v['atime'], v['anftime'], v['aftime'], v['akb'], v['a2xx'], v['a3xx'], v['a4xx'], v['a5xx'])

		#print tmp
			




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
			delta                       = self.buf[nfd]['time'] - self.time
			

			if delta >= 0:
				host = self.chkFilter(self.buf[nfd])
				if host:
					while len(self.trx) -1 < delta:
						self.trx.append({})
					#host = self.buf[nfd]['Host']
					if host not in self.trx[delta]:
						self.trx[delta][host] = {'req':0, 'fetch':0, 'fetch_time':0.0,'nofetch_time':0, 'totallen':0,'2xx':0,'3xx':0,'4xx':0,'5xx':0}
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
						self.trx[delta][host]['nofetch_time'] += self.buf[nfd]['worktime']

			else:
				print 'delay:'
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

